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
from appy.shared import mimeTypesExts
from appy.shared.xml_parser import XmlElement
from appy.shared.utils import FolderDeleter, executeCommand
from appy.shared.utils import FileWrapper
from appy.pod.pod_parser import PodParser, PodEnvironment, OdInsert
from appy.pod.converter import FILE_TYPES
from appy.pod.buffers import FileBuffer
from appy.pod.xhtml2odt import Xhtml2OdtConverter
from appy.pod.doc_importers import OdtImporter, ImageImporter, PdfImporter
from appy.pod.styles_manager import StylesManager

# ------------------------------------------------------------------------------
BAD_CONTEXT = 'Context must be either a dict, a UserDict or an instance.'
RESULT_FILE_EXISTS = 'Result file "%s" exists.'
CANT_WRITE_RESULT = 'I cannot write result file "%s". %s'
CANT_WRITE_TEMP_FOLDER = 'I cannot create temp folder "%s". %s'
NO_PY_PATH = 'Extension of result file is "%s". In order to perform ' \
             'conversion from ODT to this format we need to call OpenOffice. ' \
             'But the Python interpreter which runs the current script does ' \
             'not know UNO, the library that allows to connect to ' \
             'OpenOffice in server mode. If you can\'t install UNO in this ' \
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
BAD_OO_PORT = 'Bad OpenOffice port "%s". Make sure it is an integer.'
XHTML_ERROR = 'An error occurred while rendering XHTML content.'
WARNING_INCOMPLETE_ODT = 'Warning: your ODT file may not be complete (ie ' \
                         'imported documents may not be present). This is ' \
                         'because we could not connect to OpenOffice in ' \
                         'server mode: %s'
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
CONTENT_POD_FONTS = '<@style@:font-face style:name="PodStarSymbol" ' \
                    '@svg@:font-family="StarSymbol"/>'

# Default text styles added by pod in styles.xml
f = file('%s/styles.in.styles.xml' % os.path.dirname(appy.pod.__file__))
STYLES_POD_STYLES = f.read()
f.close()

# Default font added by pod
STYLES_POD_FONTS = '<@style@:font-face @style@:name="PodStarSymbol" ' \
                   '@svg@:font-family="StarSymbol"/>'

# ------------------------------------------------------------------------------
class Renderer:
    def __init__(self, template, context, result, pythonWithUnoPath=None,
                 ooPort=2002, stylesMapping={}, forceOoCall=False,
                 finalizeFunction=None, overwriteExisting=False):
        '''This Python Open Document Renderer (PodRenderer) loads a document
        template (p_template) which is an ODT file with some elements
        written in Python. Based on this template and some Python objects
        defined in p_context, the renderer generates an ODT file
        (p_result) that instantiates the p_template and fills it with objects
        from the p_context.

         - If p_result does not end with .odt, the Renderer
           will call OpenOffice to perform a conversion. If p_forceOoCall is
           True, even if p_result ends with .odt, OpenOffice will be called, not
           for performing a conversion, but for updating some elements like
           indexes (table of contents, etc) and sections containing links to
           external files (which is the case, for example, if you use the
           default function "document").

         - If the Python interpreter which runs the current script is not
           UNO-enabled, this script will run, in another process, a UNO-enabled
           Python interpreter (whose path is p_pythonWithUnoPath) which will
           call OpenOffice. In both cases, we will try to connect to OpenOffice
           in server mode on port p_ooPort.

         - If you plan to make "XHTML to OpenDocument" conversions, you may
           specify a styles mapping in p_stylesMapping.

         - If you specify a function in p_finalizeFunction, this function will
           be called by the renderer before re-zipping the ODT result. This way,
           you can still perform some actions on the content of the ODT file
           before it is zipped and potentially converted. This function must
           accept one arg: the absolute path to the temporary folder containing
           the un-zipped content of the ODT result.

         - If you set p_overwriteExisting to True, the renderer will overwrite
           the result file. Else, an exception will be thrown if the result file
           already exists.'''
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
        # Remember potential files or images that will be included through
        # "do ... from document" statements: we will need to declare them in
        # META-INF/manifest.xml. Keys are file names as they appear within the
        # ODT file (to dump in manifest.xml); values are original paths of
        # included images (used for avoiding to create multiple copies of a file
        # which is imported several times).
        # imported file).
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
                # This is an empty folder. Create it nevertheless.
                os.makedirs(os.path.join(self.unzipFolder, zippedFile))
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
                nsUris={'style': pe.NS_STYLE, 'fo': pe.NS_FO}))
        self.stylesParser = self.createPodParser('styles.xml', context,
                                                 stylesInserts)
        # Stores the styles mapping
        self.setStylesMapping(stylesMapping)

    def createPodParser(self, odtFile, context, inserts):
        '''Creates the parser with its environment for parsing the given
           p_odtFile (content.xml or styles.xml). p_context is given by the pod
           user, while p_inserts depends on the ODT file we must parse.'''
        evalContext = {'xhtml': self.renderXhtml,
                       'text':  self.renderText,
                       'test': self.evalIfExpression,
                       'document': self.importDocument} # Default context
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
        ns = self.currentParser.env.namespaces
        # xhtmlString can only be a chunk of XHTML. So we must surround it a
        # tag in order to get a XML-compliant file (we need a root tag).
        if xhtmlString == None: xhtmlString = ''
        xhtmlContent = '<p>%s</p>' % xhtmlString
        return Xhtml2OdtConverter(xhtmlContent, encoding, self.stylesManager,
                                  stylesMapping, ns).run()

    def renderText(self, text, encoding='utf-8', stylesMapping={}):
        '''Method that can be used (under the name 'text') into a pod template
           for inserting a text containing carriage returns.'''
        if text == None: text = ''
        text = cgi.escape(text).replace('\r\n', '<br/>').replace('\n', '<br/>')
        return self.renderXhtml(text, encoding, stylesMapping)

    def evalIfExpression(self, condition, ifTrue, ifFalse):
        '''This method implements the method 'test' which is proposed in the
           default pod context. It represents an 'if' expression (as opposed to
           the 'if' statement): depending on p_condition, expression result is
           p_ifTrue or p_ifFalse.'''
        if condition:
            return ifTrue
        return ifFalse

    imageFormats = ('png', 'jpeg', 'jpg', 'gif')
    ooFormats = ('odt',)
    def importDocument(self, content=None, at=None, format=None,
                       anchor='as-char', wrapInPara=True, size=None):
        '''If p_at is not None, it represents a path or url allowing to find
           the document. If p_at is None, the content of the document is
           supposed to be in binary format in p_content. The document
           p_format may be: odt or any format in imageFormats.

           p_anchor, p_wrapInPara and p_size are only relevant for images:
           * p_anchor defines the way the image is anchored into the document;
                      Valid values are 'page','paragraph', 'char' and 'as-char';
           * p_wrapInPara, if true, wraps the resulting 'image' tag into a 'p'
                           tag;
           * p_size, if specified, is a tuple of float or integers
                     (width, height) expressing size in centimeters. If not
                     specified, size will be computed from image info.'''
        ns = self.currentParser.env.namespaces
        importer = None
        # Is there someting to import?
        if not content and not at:
            raise PodError(DOC_NOT_SPECIFIED)
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
        if format in self.ooFormats:
            importer = OdtImporter
            self.forceOoCall = True
        elif format in self.imageFormats:
            importer = ImageImporter
            isImage = True
        elif format == 'pdf':
            importer = PdfImporter
        else:
            raise PodError(DOC_WRONG_FORMAT % format)
        imp = importer(content, at, format, self.tempFolder, ns, self.fileNames)
        # Initialise image-specific parameters
        if isImage: imp.setImageInfo(anchor, wrapInPara, size)
        res = imp.run()
        return res

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

    def getStyles(self):
        '''Returns a dict of the styles that are defined into the template.'''
        return self.stylesManager.styles

    def setStylesMapping(self, stylesMapping):
        '''Establishes a correspondance between, on one hand, CSS styles or
           XHTML tags that will be found inside XHTML content given to POD,
           and, on the other hand, ODT styles found into the template.'''
        try:
            stylesMapping = self.stylesManager.checkStylesMapping(stylesMapping)
            self.stylesManager.stylesMapping = stylesMapping
        except PodError, po:
            self.contentParser.env.currentBuffer.content.close()
            self.stylesParser.env.currentBuffer.content.close()
            if os.path.exists(self.tempFolder):
                FolderDeleter.delete(self.tempFolder)
            raise po

    def reportProblem(self, msg, resultType):
        '''When trying to call OO in server mode for producing ODT
           (=forceOoCall=True), if an error occurs we still have an ODT to
           return to the user. So we produce a warning instead of raising an
           error.'''
        if (resultType == 'odt') and self.forceOoCall:
            print WARNING_INCOMPLETE_ODT % msg
        else:
            raise msg

    def callOpenOffice(self, resultOdtName, resultType):
        '''Call Open Office in server mode to convert or update the ODT
           result.'''
        ooOutput = ''
        try:
            if (not isinstance(self.ooPort, int)) and \
            (not isinstance(self.ooPort, long)):
                raise PodError(BAD_OO_PORT % str(self.ooPort))
            try:
                from appy.pod.converter import Converter, ConverterError
                try:
                    Converter(resultOdtName, resultType,
                                self.ooPort).run()
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
                if resultOdtName.find(' ') != -1:
                    qResultOdtName = '"%s"' % resultOdtName
                else:
                    qResultOdtName = resultOdtName
                convScript = '%s/converter.py' % \
                            os.path.dirname(appy.pod.__file__)
                if convScript.find(' ') != -1:
                    convScript = '"%s"' % convScript
                cmd = '%s %s %s %s -p%d' % \
                    (self.pyPath, convScript, qResultOdtName, resultType,
                    self.ooPort)
                ooOutput = executeCommand(cmd)
        except PodError, pe:
            # When trying to call OO in server mode for producing
            # ODT (=forceOoCall=True), if an error occurs we still
            # have an ODT to return to the user. So we produce a
            # warning instead of raising an error.
            if (resultType == 'odt') and self.forceOoCall:
                print WARNING_INCOMPLETE_ODT % str(pe)
            else:
                raise pe
        return ooOutput

    def finalize(self):
        '''Re-zip the result and potentially call OpenOffice if target format is
           not ODT or if forceOoCall is True.'''
        for odtFile in ('content.xml', 'styles.xml'):
            shutil.copy(os.path.join(self.tempFolder, odtFile),
                        os.path.join(self.unzipFolder, odtFile))
        if self.finalizeFunction:
            try:
                self.finalizeFunction(self.unzipFolder)
            except Exception, e:
                print WARNING_FINALIZE_ERROR % str(e)
        resultOdtName = os.path.join(self.tempFolder, 'result.odt')
        try:
            resultOdt = zipfile.ZipFile(resultOdtName,'w', zipfile.ZIP_DEFLATED)
        except RuntimeError:
            resultOdt = zipfile.ZipFile(resultOdtName,'w')
        for dir, dirnames, filenames in os.walk(self.unzipFolder):
            for f in filenames:
                folderName = dir[len(self.unzipFolder)+1:]
                resultOdt.write(os.path.join(dir, f),
                                os.path.join(folderName, f))
            if not dirnames and not filenames:
                # This is an empty leaf folder. We must create an entry in the
                # zip for him
                folderName = dir[len(self.unzipFolder):]
                zInfo = zipfile.ZipInfo("%s/" % folderName,time.localtime()[:6])
                zInfo.external_attr = 48
                resultOdt.writestr(zInfo, '')
        resultOdt.close()
        resultType = os.path.splitext(self.result)[1]
        try:
            if (resultType == '.odt') and not self.forceOoCall:
                # Simply move the ODT result to the result
                os.rename(resultOdtName, self.result)
            else:
                if resultType.startswith('.'): resultType = resultType[1:]
                if not resultType in FILE_TYPES.keys():
                    raise PodError(BAD_RESULT_TYPE % (
                        self.result, FILE_TYPES.keys()))
                # Call OpenOffice to perform the conversion or document update
                output = self.callOpenOffice(resultOdtName, resultType)
                # I (should) have the result. Move it to the correct name
                resPrefix = os.path.splitext(resultOdtName)[0] + '.'
                if resultType == 'odt':
                    # converter.py has (normally!) created a second file
                    # suffixed .res.odt
                    resultName = resPrefix + 'res.odt'
                    if not os.path.exists(resultName):
                        resultName = resultOdtName
                        # In this case OO in server mode could not be called to
                        # update indexes, sections, etc.
                else:
                    resultName = resPrefix + resultType
                if not os.path.exists(resultName):
                    raise PodError(CONVERT_ERROR % output)
                os.rename(resultName, self.result)
        finally:
            FolderDeleter.delete(self.tempFolder)
# ------------------------------------------------------------------------------
