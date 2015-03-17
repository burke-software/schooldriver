# ------------------------------------------------------------------------------
# Appy is a framework for building applications in the Python language.
# Copyright (C) 2007 Gaetan Delannay

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,USA.

# ------------------------------------------------------------------------------
import zipfile, shutil, xml.sax, os, os.path, re, mimetypes, time

from UserDict import UserDict

import appy.pod, time, cgi
from appy.pod import PodError
from appy.shared import mimeTypes, mimeTypesExts
from appy.shared.xml_parser import XmlElement
from appy.shared.utils import FolderDeleter, executeCommand, FileWrapper
from appy.pod.pod_parser import PodParser, PodEnvironment, OdInsert
from appy.pod.converter import FILE_TYPES
from appy.pod.buffers import FileBuffer
from appy.pod.xhtml2odt import Xhtml2OdtConverter
from appy.pod.doc_importers import \
     OdtImporter, ImageImporter, PdfImporter, ConvertImporter, PodImporter
from appy.pod.styles_manager import StylesManager

# ------------------------------------------------------------------------------
BAD_CONTEXT = 'Context must be either a dict, a UserDict or an instance.'
RESULT_FILE_EXISTS = 'Result file "%s" exists.'
CANT_WRITE_RESULT = 'I cannot write result file "%s". %s'
CANT_WRITE_TEMP_FOLDER = 'I cannot create temp folder "%s". %s'
NO_PY_PATH = 'Extension of result file is "%s". In order to perform ' \
             'conversion from ODT to this format we need to call LibreOffice. ' \
             'But the Python interpreter which runs the current script does ' \
             'not know UNO, the library that allows to connect to ' \
             'LibreOffice in server mode. If you can\'t install UNO in this ' \
             'Python interpreter, you can specify, in parameter ' \
             '"pythonWithUnoPath", the path to a UNO-enabled Python ' \
             'interpreter. One such interpreter may be found in ' \
             '<open_office_path>/program.'
PY_PATH_NOT_FILE = '"%s" is not a file. You must here specify the absolute ' \
                   'path of a Python interpreter (.../python, .../python.sh, ' \
                   '.../python.exe, .../python.bat...).'
BLANKS_IN_PATH = 'Blanks were found in path "%s". Please use the DOS-names ' \
                 '(ie, "progra~1" instead of "Program files" or "docume~1" ' \
                 'instead of "Documents and settings".'
BAD_RESULT_TYPE = 'Result "%s" has a wrong extension. Allowed extensions ' \
                  'are: "%s".'
CONVERT_ERROR = 'An error occurred during the conversion. %s'
BAD_OO_PORT = 'Bad LibreOffice port "%s". Make sure it is an integer.'
XHTML_ERROR = 'An error occurred while rendering XHTML content.'
WARNING_INCOMPLETE_OD = 'Warning: your OpenDocument file may not be complete ' \
  '(ie imported documents may not be present). This is because we could not ' \
  'connect to LibreOffice in server mode: %s'
DOC_NOT_SPECIFIED = 'Please specify a document to import, either with a ' \
                    'stream (parameter "content") or with a path (parameter ' \
                    '"at")'
DOC_FORMAT_ERROR = 'POD was unable to deduce the document format. Please ' \
                   'specify it through parameter named "format" (=odt, gif, ' \
                   'png, ...).'
DOC_WRONG_FORMAT = 'Format "%s" is not supported.'
WARNING_FINALIZE_ERROR = 'Warning: error while calling finalize function. %s'

# Default automatic text styles added by pod in content.xml
f = open('%s/styles.in.content.xml' % os.path.dirname(appy.pod.__file__))
CONTENT_POD_STYLES = f.read()
f.close()

# Default font added by pod in content.xml
CONTENT_POD_FONTS = '<@style@:font-face @style@:name="PodStarSymbol" ' \
                    '@svg@:font-family="StarSymbol"/>'

# Default text styles added by pod in styles.xml
f = file('%s/styles.in.styles.xml' % os.path.dirname(appy.pod.__file__))
STYLES_POD_STYLES = f.read()
f.close()

# Default font added by pod
STYLES_POD_FONTS = '<@style@:font-face @style@:name="PodStarSymbol" ' \
                   '@svg@:font-family="StarSymbol"/>'

# do ... \n from text(...) is obsolete.
OBSOLETE_RENDER_TEXT = 'Obsolete function. Use a pod expression instead ' \
                       '(field or track-changed). Now, a pod expression ' \
                       'handles carriage returns and tabs correctly.'

# ------------------------------------------------------------------------------
class Renderer:
    templateTypes = ('odt', 'ods') # Types of POD templates

    def __init__(self, template, context, result, pythonWithUnoPath=None,
                 ooPort=2002, stylesMapping={}, forceOoCall=False,
                 finalizeFunction=None, overwriteExisting=False,
                 raiseOnError=False, imageResolver=None):
        '''This Python Open Document Renderer (PodRenderer) loads a document
           template (p_template) which is an ODT or ODS file with some elements
           written in Python. Based on this template and some Python objects
           defined in p_context, the renderer generates an ODT file (p_result)
           that instantiates the p_template and fills it with objects from the
           p_context.

         - If p_result does not end with .odt or .ods, the Renderer will call
           LibreOffice to perform a conversion. If p_forceOoCall is True, even
           if p_result ends with .odt, LibreOffice will be called, not for
           performing a conversion, but for updating some elements like indexes
           (table of contents, etc) and sections containing links to external
           files (which is the case, for example, if you use the default
           function "document").

         - If the Python interpreter which runs the current script is not
           UNO-enabled, this script will run, in another process, a UNO-enabled
           Python interpreter (whose path is p_pythonWithUnoPath) which will
           call LibreOffice. In both cases, we will try to connect to
           LibreOffice in server mode on port p_ooPort.

         - If you plan to make "XHTML to OpenDocument" conversions, you may
           specify a styles mapping in p_stylesMapping.

         - If you specify a function in p_finalizeFunction, this function will
           be called by the renderer before re-zipping the ODT/S result. This
           way, you can still perform some actions on the content of the ODT/S
           file before it is zipped and potentially converted. This function
           must accept one arg: the absolute path to the temporary folder
           containing the un-zipped content of the ODT/S result.

         - If you set p_overwriteExisting to True, the renderer will overwrite
           the result file. Else, an exception will be thrown if the result file
           already exists.

         - If p_raiseOnError is False (the default value), any error encountered
           during the generation of the result file will be dumped into it, as
           a Python traceback within a note. Else, the error will be raised.

         - p_imageResolver allows POD to retrieve images, from "img" tags within
           XHTML content. Indeed, POD may not be able (ie, may not have the
           permission to) perform a HTTP GET on those images. Currently, the
           resolver can only be a Zope application object.
        '''
        self.template = template
        self.templateZip = zipfile.ZipFile(template)
        self.result = result
        self.contentXml = None # Content (string) of content.xml
        self.stylesXml = None # Content (string) of styles.xml
        self.stylesManager = None # Manages the styles defined into the ODT
        # template
        self.tempFolder = None
        self.env = None
        self.pyPath = pythonWithUnoPath
        self.ooPort = ooPort
        self.forceOoCall = forceOoCall
        self.finalizeFunction = finalizeFunction
        self.overwriteExisting = overwriteExisting
        self.raiseOnError = raiseOnError
        self.imageResolver = imageResolver
        # Remember potential files or images that will be included through
        # "do ... from document" statements: we will need to declare them in
        # META-INF/manifest.xml. Keys are file names as they appear within the
        # ODT file (to dump in manifest.xml); values are original paths of
        # included images (used for avoiding to create multiple copies of a file
        # which is imported several times).
        self.fileNames = {}
        self.prepareFolders()
        # Unzip template
        self.unzipFolder = os.path.join(self.tempFolder, 'unzip')
        os.mkdir(self.unzipFolder)
        for zippedFile in self.templateZip.namelist():
            # Before writing the zippedFile into self.unzipFolder, create the
            # intermediary subfolder(s) if needed.
            fileName = None
            if zippedFile.endswith('/') or zippedFile.endswith(os.sep):
                # This is an empty folder. Create it nevertheless. If zippedFile
                # starts with a '/', os.path.join will consider it an absolute
                # path and will throw away self.unzipFolder.
                os.makedirs(os.path.join(self.unzipFolder,
                                         zippedFile.lstrip('/')))
            else:
                fileName = os.path.basename(zippedFile)
                folderName = os.path.dirname(zippedFile)
                fullFolderName = self.unzipFolder
                if folderName:
                    fullFolderName = os.path.join(fullFolderName, folderName)
                    if not os.path.exists(fullFolderName):
                        os.makedirs(fullFolderName)
            # Unzip the file in self.unzipFolder
            if fileName:
                fullFileName = os.path.join(fullFolderName, fileName)
                f = open(fullFileName, 'wb')
                fileContent = self.templateZip.read(zippedFile)
                if (fileName == 'content.xml') and not folderName:
                    # content.xml files may reside in subfolders.
                    # We modify only the one in the root folder.
                    self.contentXml = fileContent
                elif (fileName == 'styles.xml') and not folderName:
                    # Same remark as above.
                    self.stylesManager = StylesManager(fileContent)
                    self.stylesXml = fileContent
                elif (fileName == 'mimetype') and \
                     (fileContent == mimeTypes['ods']):
                    # From LibreOffice 3.5, it is not possible anymore to dump
                    # errors into the resulting ods as annotations. Indeed,
                    # annotations can't reside anymore within paragraphs. ODS
                    # files generated with pod and containing error messages in
                    # annotations cause LibreOffice 3.5 and 4.0 to crash.
                    # LibreOffice >= 4.1 simply does not show the annotation.
                    self.raiseOnError = True
                f.write(fileContent)
                f.close()
        self.templateZip.close()
        # Create the content.xml parser
        pe = PodEnvironment
        contentInserts = (
            OdInsert(CONTENT_POD_FONTS,
                XmlElement('font-face-decls', nsUri=pe.NS_OFFICE),
                nsUris={'style': pe.NS_STYLE, 'svg': pe.NS_SVG}),
            OdInsert(CONTENT_POD_STYLES,
                XmlElement('automatic-styles', nsUri=pe.NS_OFFICE),
                nsUris={'style': pe.NS_STYLE, 'fo': pe.NS_FO,
                        'text': pe.NS_TEXT, 'table': pe.NS_TABLE}))
        self.contentParser = self.createPodParser('content.xml', context,
                                                  contentInserts)
        # Create the styles.xml parser
        stylesInserts = (
            OdInsert(STYLES_POD_FONTS,
                XmlElement('font-face-decls', nsUri=pe.NS_OFFICE),
                nsUris={'style': pe.NS_STYLE, 'svg': pe.NS_SVG}),
            OdInsert(STYLES_POD_STYLES,
                XmlElement('styles', nsUri=pe.NS_OFFICE),
                nsUris={'style': pe.NS_STYLE, 'fo': pe.NS_FO,
                        'text': pe.NS_TEXT}))
        self.stylesParser = self.createPodParser('styles.xml', context,
                                                 stylesInserts)
        # Store the styles mapping
        self.setStylesMapping(stylesMapping)
        # While working, POD may identify "dynamic styles" to insert into
        # the "automatic styles" section of content.xml, like the column styles
        # of tables generated from XHTML tables via xhtml2odt.py.
        self.dynamicStyles = []

    def createPodParser(self, odtFile, context, inserts):
        '''Creates the parser with its environment for parsing the given
           p_odtFile (content.xml or styles.xml). p_context is given by the pod
           user, while p_inserts depends on the ODT file we must parse.'''
        evalContext = {'xhtml': self.renderXhtml,
                       'text':  self.renderText,
                       'test': self.evalIfExpression,
                       'document': self.importDocument,
                       'pod': self.importPod,
                       'pageBreak': self.insertPageBreak} # Default context
        if hasattr(context, '__dict__'):
            evalContext.update(context.__dict__)
        elif isinstance(context, dict) or isinstance(context, UserDict):
            evalContext.update(context)
        else:
            raise PodError(BAD_CONTEXT)
        env = PodEnvironment(evalContext, inserts)
        fileBuffer = FileBuffer(env, os.path.join(self.tempFolder,odtFile))
        env.currentBuffer = fileBuffer
        return PodParser(env, self)

    def renderXhtml(self, xhtmlString, encoding='utf-8', stylesMapping={}):
        '''Method that can be used (under the name 'xhtml') into a pod template
           for converting a chunk of XHTML content (p_xhtmlString) into a chunk
           of ODT content.'''
        stylesMapping = self.stylesManager.checkStylesMapping(stylesMapping)
        # xhtmlString can only be a chunk of XHTML. So we must surround it with
        # a tag in order to get a XML-compliant file (we need a root tag).
        if xhtmlString == None: xhtmlString = ''
        xhtmlContent = '<p>%s</p>' % xhtmlString
        return Xhtml2OdtConverter(xhtmlContent, encoding, self.stylesManager,
                                  stylesMapping, self).run()

    def renderText(self, text, encoding='utf-8', stylesMapping={}):
        '''Obsolete method.'''
        raise Exception(OBSOLETE_RENDER_TEXT)

    def evalIfExpression(self, condition, ifTrue, ifFalse):
        '''This method implements the method 'test' which is proposed in the
           default pod context. It represents an 'if' expression (as opposed to
           the 'if' statement): depending on p_condition, expression result is
           p_ifTrue or p_ifFalse.'''
        if condition:
            return ifTrue
        return ifFalse

    imageFormats = ('png', 'jpeg', 'jpg', 'gif', 'svg')
    ooFormats = ('odt',)
    convertibleFormats = FILE_TYPES.keys()
    def importDocument(self, content=None, at=None, format=None,
                       anchor='as-char', wrapInPara=True, size=None,
                       sizeUnit='cm', style=None,
                       pageBreakBefore=False, pageBreakAfter=False):
        '''If p_at is not None, it represents a path or url allowing to find
           the document. If p_at is None, the content of the document is
           supposed to be in binary format in p_content. The document
           p_format may be: odt or any format in imageFormats.

           p_anchor, p_wrapInPara and p_size, p_sizeUnit and p_style are only
           relevant for images:
           * p_anchor defines the way the image is anchored into the document;
                      Valid values are 'page','paragraph', 'char' and 'as-char';
           * p_wrapInPara, if true, wraps the resulting 'image' tag into a 'p'
                           tag;
           * p_size, if specified, is a tuple of float or integers
                     (width, height) expressing size in p_sizeUnit (see below).
                     If not specified, size will be computed from image info;
           * p_sizeUnit is the unit for p_size elements, it can be "cm"
             (centimeters), "px" (pixels) or "pc" (percentage). Percentages, in
             p_size, must be expressed as integers from 1 to 100.
           * if p_style is given, it is the content of a "style" attribute,
             containing CSS attributes. If "width" and "heigth" attributes are
             found there, they will override p_size and p_sizeUnit.

           p_pageBreakBefore and p_pageBreakAfter are only relevant for import
           of external odt documents, and allows to insert a page break
           before/after the inserted document.
        '''
        importer = None
        # Is there someting to import?
        if not content and not at: raise PodError(DOC_NOT_SPECIFIED)
        # Convert Zope files into Appy wrappers.
        if content.__class__.__name__ in ('File', 'Image'):
            content = FileWrapper(content)
        # Guess document format
        if isinstance(content, FileWrapper):
            format = content.mimeType
        if not format:
            # It should be deduced from p_at
            if not at:
                raise PodError(DOC_FORMAT_ERROR)
            format = os.path.splitext(at)[1][1:]
        else:
            # If format is a mimeType, convert it to an extension
            if mimeTypesExts.has_key(format):
                format = mimeTypesExts[format]
        isImage = False
        isOdt = False
        if format in self.ooFormats:
            importer = OdtImporter
            self.forceOoCall = True
            isOdt = True
        elif (format in self.imageFormats) or not format:
            # If the format can't be guessed, we suppose it is an image.
            importer = ImageImporter
            isImage = True
        elif format == 'pdf':
            importer = PdfImporter
        elif format in self.convertibleFormats:
            importer = ConvertImporter
        else:
            raise PodError(DOC_WRONG_FORMAT % format)
        imp = importer(content, at, format, self)
        # Initialise image-specific parameters
        if isImage: imp.init(anchor, wrapInPara, size, sizeUnit, style)
        elif isOdt: imp.init(pageBreakBefore, pageBreakAfter)
        return imp.run()

    def importPod(self, content=None, at=None, format='odt', context=None,
                  pageBreakBefore=False, pageBreakAfter=False):
        '''Similar to m_importDocument, but allows to import the result of
           executing the POD template specified in p_content or p_at, and
           include it in the POD result.'''
        # Is there a pod template defined?
        if not content and not at:
            raise PodError(DOC_NOT_SPECIFIED)
        # If the POD template is specified as a Zope file, convert it into a
        # Appy FileWrapper.
        if content.__class__.__name__ == 'File':
            content = FileWrapper(content)
        imp = PodImporter(content, at, format, self)
        self.forceOoCall = True
        # Define the context to use: either the current context of the current
        # POD renderer, or p_context if given.
        if context:
            ctx = context
        else:
            ctx = self.contentParser.env.context
        imp.init(ctx, pageBreakBefore, pageBreakAfter)
        return imp.run()

    def insertPageBreak(self):
        '''Inserts a page break into the result.'''
        textNs = self.currentParser.env.namespaces[PodEnvironment.NS_TEXT]
        return '<%s:p %s:style-name="podPageBreak"></%s:p>' % \
               (textNs, textNs, textNs)

    def prepareFolders(self):
        # Check if I can write the result
        if not self.overwriteExisting and os.path.exists(self.result):
            raise PodError(RESULT_FILE_EXISTS % self.result)
        try:
            f = open(self.result, 'w')
            f.write('Hello')
            f.close()
        except OSError, oe:
            raise PodError(CANT_WRITE_RESULT % (self.result, oe))
        except IOError, ie:
            raise PodError(CANT_WRITE_RESULT % (self.result, ie))
        self.result = os.path.abspath(self.result)
        os.remove(self.result)
        # Create a temp folder for storing temporary files
        absResult = os.path.abspath(self.result)
        self.tempFolder = '%s.%f' % (absResult, time.time())
        try:
            os.mkdir(self.tempFolder)
        except OSError, oe:
            raise PodError(CANT_WRITE_TEMP_FOLDER % (self.result, oe))

    def patchManifest(self):
        '''Declares, in META-INF/manifest.xml, images or files included via the
           "do... from document" statements if any.'''
        if self.fileNames:
            j = os.path.join
            toInsert = ''
            for fileName in self.fileNames.iterkeys():
                if fileName.endswith('.svg'):
                    fileName = os.path.splitext(fileName)[0] + '.png'
                mimeType = mimetypes.guess_type(fileName)[0]
                toInsert += ' <manifest:file-entry manifest:media-type="%s" ' \
                            'manifest:full-path="%s"/>\n' % (mimeType, fileName)
            manifestName = j(self.unzipFolder, j('META-INF', 'manifest.xml'))
            f = file(manifestName)
            manifestContent = f.read()
            hook = '</manifest:manifest>'
            manifestContent = manifestContent.replace(hook, toInsert+hook)
            f.close()
            # Write the new manifest content
            f = file(manifestName, 'w')
            f.write(manifestContent)
            f.close()

    # Public interface
    def run(self):
        '''Renders the result.'''
        try:
            # Remember which parser is running
            self.currentParser = self.contentParser
            # Create the resulting content.xml
            self.currentParser.parse(self.contentXml)
            self.currentParser = self.stylesParser
            # Create the resulting styles.xml
            self.currentParser.parse(self.stylesXml)
            # Patch META-INF/manifest.xml
            self.patchManifest()
            # Re-zip the result
            self.finalize()
        finally:
            FolderDeleter.delete(self.tempFolder)

    def getStyles(self):
        '''Returns a dict of the styles that are defined into the template.'''
        return self.stylesManager.styles

    def setStylesMapping(self, stylesMapping):
        '''Establishes a correspondance between, on one hand, CSS styles or
           XHTML tags that will be found inside XHTML content given to POD,
           and, on the other hand, ODT styles found into the template.'''
        try:
            stylesMapping = self.stylesManager.checkStylesMapping(stylesMapping)
            # The predefined styles below are currently ignored, because the
            # xhtml2odt parser does not take into account span tags.
            if 'span[font-weight=bold]' not in stylesMapping:
                stylesMapping['span[font-weight=bold]'] = 'podBold'
            if 'span[font-style=italic]' not in stylesMapping:
                stylesMapping['span[font-style=italic]'] = 'podItalic'
            self.stylesManager.stylesMapping = stylesMapping
        except PodError, po:
            self.contentParser.env.currentBuffer.content.close()
            self.stylesParser.env.currentBuffer.content.close()
            if os.path.exists(self.tempFolder):
                FolderDeleter.delete(self.tempFolder)
            raise po

    def callLibreOffice(self, resultName, resultType):
        '''Call LibreOffice in server mode to convert or update the result.'''
        loOutput = ''
        try:
            if (not isinstance(self.ooPort, int)) and \
               (not isinstance(self.ooPort, long)):
                raise PodError(BAD_OO_PORT % str(self.ooPort))
            try:
                from appy.pod.converter import Converter, ConverterError
                try:
                    Converter(resultName, resultType, self.ooPort).run()
                except ConverterError, ce:
                    raise PodError(CONVERT_ERROR % str(ce))
            except ImportError:
                # I do not have UNO. So try to launch a UNO-enabled Python
                # interpreter which should be in self.pyPath.
                if not self.pyPath:
                    raise PodError(NO_PY_PATH % resultType)
                if self.pyPath.find(' ') != -1:
                    raise PodError(BLANKS_IN_PATH % self.pyPath)
                if not os.path.isfile(self.pyPath):
                    raise PodError(PY_PATH_NOT_FILE % self.pyPath)
                if resultName.find(' ') != -1:
                    qResultName = '"%s"' % resultName
                else:
                    qResultName = resultName
                convScript = '%s/converter.py' % \
                            os.path.dirname(appy.pod.__file__)
                if convScript.find(' ') != -1:
                    convScript = '"%s"' % convScript
                cmd = '%s %s %s %s -p%d' % \
                    (self.pyPath, convScript, qResultName, resultType,
                    self.ooPort)
                loOutput = executeCommand(cmd)
        except PodError, pe:
            # When trying to call LO in server mode for producing ODT or ODS
            # (=forceOoCall=True), if an error occurs we have nevertheless
            # an ODT or ODS to return to the user. So we produce a warning
            # instead of raising an error.
            if (resultType in self.templateTypes) and self.forceOoCall:
                print(WARNING_INCOMPLETE_OD % str(pe))
            else:
                raise pe
        return loOutput

    def getTemplateType(self):
        '''Identifies the type of the pod template in self.template
           (ods or odt). If self.template is a string, it is a file name and we
           simply get its extension. Else, it is a binary file in a StringIO
           instance, and we seek the mime type from the first bytes.'''
        if isinstance(self.template, basestring):
            res = os.path.splitext(self.template)[1][1:]
        else:
            # A StringIO instance
            self.template.seek(0)
            firstBytes = self.template.read(90)
            firstBytes = firstBytes[firstBytes.index('mimetype')+8:]
            if firstBytes.startswith(mimeTypes['ods']):
                res = 'ods'
            else:
                # We suppose this is ODT
                res = 'odt'
        return res

    def finalize(self):
        '''Re-zip the result and potentially call LibreOffice if target format
           is not among self.templateTypes or if forceOoCall is True.'''
        for innerFile in ('content.xml', 'styles.xml'):
            shutil.copy(os.path.join(self.tempFolder, innerFile),
                        os.path.join(self.unzipFolder, innerFile))
        # Insert dynamic styles
        contentXml = os.path.join(self.unzipFolder, 'content.xml')
        f = file(contentXml)
        dynamicStyles = ''.join(self.dynamicStyles)
        content = f.read().replace('<!DYNAMIC_STYLES!>', dynamicStyles)
        f.close()
        f = file(contentXml, 'w')
        f.write(content)
        f.close()
        # Call the user-defined "finalize" function when present.
        if self.finalizeFunction:
            try:
                self.finalizeFunction(self.unzipFolder)
            except Exception, e:
                print(WARNING_FINALIZE_ERROR % str(e))
        # Re-zip the result, first as an OpenDocument file of the same type as
        # the POD template (odt, ods...)
        resultExt = self.getTemplateType()
        resultName = os.path.join(self.tempFolder, 'result.%s' % resultExt)
        try:
            resultZip = zipfile.ZipFile(resultName, 'w', zipfile.ZIP_DEFLATED)
        except RuntimeError:
            resultZip = zipfile.ZipFile(resultName,'w')
        # Insert first the file "mimetype" (uncompressed), in order to be
        # compliant with the OpenDocument Format specification, section 17.4,
        # that expresses this restriction. Else, libraries like "magic", under
        # Linux/Unix, are unable to detect the correct mimetype for a pod result
        # (it simply recognizes it as a "application/zip" and not a
        # "application/vnd.oasis.opendocument.text)".
        mimetypeFile = os.path.join(self.unzipFolder, 'mimetype')
        # This file may not exist (presumably, ods files from Google Drive)
        if not os.path.exists(mimetypeFile):
            f = open(mimetypeFile, 'w')
            f.write(mimeTypes[resultExt])
            f.close()
        resultZip.write(mimetypeFile, 'mimetype', zipfile.ZIP_STORED)
        for dir, dirnames, filenames in os.walk(self.unzipFolder):
            for f in filenames:
                folderName = dir[len(self.unzipFolder)+1:]
                # Ignore file "mimetype" that was already inserted.
                if (folderName == '') and (f == 'mimetype'): continue
                resultZip.write(os.path.join(dir, f),
                                os.path.join(folderName, f))
            if not dirnames and not filenames:
                # This is an empty leaf folder. We must create an entry in the
                # zip for him.
                folderName = dir[len(self.unzipFolder):]
                zInfo = zipfile.ZipInfo("%s/" % folderName,time.localtime()[:6])
                zInfo.external_attr = 48
                resultZip.writestr(zInfo, '')
        resultZip.close()
        resultType = os.path.splitext(self.result)[1].strip('.')
        if (resultType in self.templateTypes) and not self.forceOoCall:
            # Simply move the ODT result to the result
            os.rename(resultName, self.result)
        else:
            if resultType not in FILE_TYPES:
                raise PodError(BAD_RESULT_TYPE % (
                    self.result, FILE_TYPES.keys()))
            # Call LibreOffice to perform the conversion or document update.
            output = self.callLibreOffice(resultName, resultType)
            # I (should) have the result. Move it to the correct name.
            resPrefix = os.path.splitext(resultName)[0]
            if resultType in self.templateTypes:
                # converter.py has (normally!) created a second file
                # suffixed .res.[resultType]
                finalResultName = '%s.res.%s' % (resPrefix, resultType)
                if not os.path.exists(finalResultName):
                    finalResultName = resultName
                    # In this case OO in server mode could not be called to
                    # update indexes, sections, etc.
            else:
                finalResultName = '%s.%s' % (resPrefix, resultType)
            if not os.path.exists(finalResultName):
                raise PodError(CONVERT_ERROR % output)
            os.rename(finalResultName, self.result)
# ------------------------------------------------------------------------------
