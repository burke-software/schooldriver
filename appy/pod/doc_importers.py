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
import os, os.path, time, shutil, struct, random, urlparse
from appy.pod import PodError
from appy.pod.odf_parser import OdfEnvironment
from appy.shared import mimeTypesExts
from appy.shared.utils import FileWrapper
from appy.shared.dav import Resource
# The uuid module is there only if python >= 2.5
try:
    import uuid
except ImportError:
    uuid = None

# ------------------------------------------------------------------------------
FILE_NOT_FOUND = "'%s' does not exist or is not a file."
PDF_TO_IMG_ERROR = 'A PDF file could not be converted into images. Please ' \
                   'ensure that Ghostscript (gs) is installed on your ' \
                   'system and the "gs" program is in the path.'
CONVERT_ERROR = 'Program "convert", from imagemagick, must be installed and ' \
                'in the path for converting a SVG file into a PNG file. ' \
                'Conversion of SVG files must also be enabled. On Ubuntu: ' \
                'apt-get install librsvg2-bin'
TO_PDF_ERROR = 'ConvertImporter error while converting a doc to PDF: %s.'

# ------------------------------------------------------------------------------
class DocImporter:
    '''Base class used for importing external content into a pod template (an
       image, another pod template, another odt document...'''
    def __init__(self, content, at, format, renderer):
        self.content = content
        # If content is None, p_at tells us where to find it (file system path,
        # url, etc)
        self.at = at
        # Ensure this path exists, if it is a local path.
        if at and not at.startswith('http') and not os.path.isfile(at):
            raise PodError(FILE_NOT_FOUND % at)
        self.format = format
        self.res = u''
        self.renderer = renderer
        self.ns = renderer.currentParser.env.namespaces
        # Unpack some useful namespaces
        self.textNs = self.ns[OdfEnvironment.NS_TEXT]
        self.linkNs = self.ns[OdfEnvironment.NS_XLINK]
        self.drawNs = self.ns[OdfEnvironment.NS_DRAW]
        self.svgNs = self.ns[OdfEnvironment.NS_SVG]
        self.tempFolder = renderer.tempFolder
        self.importFolder = self.getImportFolder()
        # Create the import folder if it does not exist.
        if not os.path.exists(self.importFolder): os.mkdir(self.importFolder)
        self.importPath = self.getImportPath(at, format)
        # A link to the global fileNames dict (explained in renderer.py)
        self.fileNames = renderer.fileNames
        if at:
            # Move the file within the ODT, if it is an image and if this image
            # has not already been imported.
            self.importPath = self.moveFile(at, self.importPath)
        else:
            # We need to dump the file content (in self.content) in a temp file
            # first. self.content may be binary, a file handler or a
            # FileWrapper.
            if isinstance(self.content, FileWrapper):
                self.content.dump(self.importPath)
            else:
                if isinstance(self.content, file):
                    fileContent = self.content.read()
                else:
                    fileContent = self.content
                f = file(self.importPath, 'wb')
                f.write(fileContent)
                f.close()
        # Some importers add specific attrs, through method init.

    def getUuid(self):
        '''Creates a unique id for images/documents to be imported into an
           ODT document.'''
        if uuid:
            return uuid.uuid4().hex
        else:
            # The uuid module is not there. Generate a UUID based on random.
            return 'f%d.%f' % (random.randint(0,1000), time.time())

    def getImportFolder(self):
        '''This method must be overridden and gives the path where to dump the
           content of the document or image. In the case of a document it is a
           temp folder; in the case of an image it is a folder within the ODT
           result.'''

    def getImportPath(self, at, format):
        '''Gets the path name of the file to dump on disk (within the ODT for
           images, in a temp folder for docs).'''
        if not format:
            if at.startswith('http'):
                format = '' # We will know it only after the HTTP GET.
            else:
                format = os.path.splitext(at)[1][1:]
        fileName = '%s.%s' % (self.getUuid(), format)
        return os.path.abspath('%s/%s' % (self.importFolder, fileName))

    def moveFile(self, at, importPath):
        '''In the case parameter "at" was used, we may want to move the file at
           p_at within the ODT result in p_importPath (for images) or do
           nothing (for docs). In the latter case, the file to import stays
           at _at, and is not copied into p_importPath. So the previously
           computed p_importPath is not used at all.'''
        return at

class OdtImporter(DocImporter):
    '''This class allows to import the content of another ODT document into a
       pod template.'''
    def getImportFolder(self): return '%s/docImports' % self.tempFolder

    def init(self, pageBreakBefore, pageBreakAfter):
        '''OdtImporter-specific constructor.'''
        self.pageBreakBefore = pageBreakBefore
        self.pageBreakAfter = pageBreakAfter

    def run(self):
        # Define a "pageBreak" if needed.
        if self.pageBreakBefore or self.pageBreakAfter:
            pageBreak = '<%s:p %s:style-name="podPageBreak"></%s:p>' % \
                        (self.textNs, self.textNs, self.textNs)
        # Insert a page break before importing the doc if needed
        if self.pageBreakBefore: self.res += pageBreak
        # Import the external odt document
        self.res += '<%s:section %s:name="PodImportSection%f">' \
                    '<%s:section-source %s:href="%s" ' \
                    '%s:filter-name="writer8"/></%s:section>' % (
                        self.textNs, self.textNs, time.time(), self.textNs,
                        self.linkNs, self.importPath, self.textNs, self.textNs)
        # Insert a page break after importing the doc if needed
        if self.pageBreakAfter: self.res += pageBreak
        return self.res

class PodImporter(DocImporter):
    '''This class allows to import the result of applying another POD template,
       into the current POD result.'''
    def getImportFolder(self): return '%s/docImports' % self.tempFolder

    def init(self, context, pageBreakBefore, pageBreakAfter):
        '''PodImporter-specific constructor.'''
        self.context = context
        self.pageBreakBefore = pageBreakBefore
        self.pageBreakAfter = pageBreakAfter

    def run(self):
        # Define where to store the pod result in the temp folder
        r = self.renderer
        # Define where to store the ODT result.
        op = os.path
        resOdt = op.join(self.getImportFolder(), '%s.odt' % self.getUuid())
        # The POD template is in self.importPath
        renderer = r.__class__(self.importPath, self.context, resOdt,
                               pythonWithUnoPath=r.pyPath,
                               ooPort=r.ooPort, forceOoCall=r.forceOoCall,
                               imageResolver=r.imageResolver)
        renderer.stylesManager.stylesMapping = r.stylesManager.stylesMapping
        renderer.run()
        # The POD result is in "resOdt". Import it into the main POD result
        # using an OdtImporter.
        odtImporter = OdtImporter(None, resOdt, 'odt', self.renderer)
        odtImporter.init(self.pageBreakBefore, self.pageBreakAfter)
        return odtImporter.run()

class PdfImporter(DocImporter):
    '''This class allows to import the content of a PDF file into a pod
       template. It calls gs to split the PDF into images and calls the
       ImageImporter for importing it into the result.'''
    def getImportFolder(self): return '%s/docImports' % self.tempFolder
    def run(self):
        imagePrefix = os.path.splitext(os.path.basename(self.importPath))[0]
        # Split the PDF into images with Ghostscript
        imagesFolder = os.path.dirname(self.importPath)
        cmd = 'gs -dNOPAUSE -dBATCH -sDEVICE=jpeg -r125x125 ' \
              '-sOutputFile=%s/%s%%d.jpg %s' % \
              (imagesFolder, imagePrefix, self.importPath)
        os.system(cmd)
        # Check that at least one image was generated
        succeeded = False
        firstImage = '%s1.jpg' % imagePrefix
        for fileName in os.listdir(imagesFolder):
            if fileName == firstImage:
                succeeded = True
                break
        if not succeeded: raise PodError(PDF_TO_IMG_ERROR)
        # Insert images into the result.
        noMoreImages = False
        i = 0
        while not noMoreImages:
            i += 1
            nextImage = '%s/%s%d.jpg' % (imagesFolder, imagePrefix, i)
            if os.path.exists(nextImage):
                # Use internally an Image importer for doing this job.
                imgImporter= ImageImporter(None, nextImage, 'jpg',self.renderer)
                imgImporter.init('paragraph', True, None, None, None)
                self.res += imgImporter.run()
                os.remove(nextImage)
            else:
                noMoreImages = True
        return self.res

class ConvertImporter(DocImporter):
    '''This class allows to import the content of any file that LibreOffice (LO)
       can convert into PDF: doc, rtf, xls. It first calls LO to convert the
       document into PDF, then calls a PdfImporter.'''
    def getImportFolder(self): return '%s/docImports' % self.tempFolder
    def run(self):
        # Convert the document into PDF with LibreOffice
        output = self.renderer.callLibreOffice(self.importPath, 'pdf')
        if output: raise PodError(TO_PDF_ERROR % output)
        pdfFile = '%s.pdf' % os.path.splitext(self.importPath)[0]
        # Launch a PdfImporter to import this PDF into the POD result.
        pdfImporter = PdfImporter(None, pdfFile, 'pdf', self.renderer)
        return pdfImporter.run()

# Compute size of images -------------------------------------------------------
jpgTypes = ('jpg', 'jpeg')
pxToCm = 44.173513561
def getSize(filePath, fileType):
    '''Gets the size of an image by reading first bytes.'''
    x, y = (None, None)
    # Get fileType from filePath if not given.
    if not fileType: fileType = os.path.splitext(filePath)[1][1:]
    f = file(filePath, 'rb')
    if fileType in jpgTypes:
        # Dummy read to skip header ID
        f.read(2)
        while True:
            # Extract the segment header.
            (marker, code, length) = struct.unpack("!BBH", f.read(4))
            # Verify that it's a valid segment.
            if marker != 0xFF:
                # No JPEG marker
                break
            elif code >= 0xC0 and code <= 0xC3:
                # Segments that contain size info
                (y, x) = struct.unpack("!xHH", f.read(5))
                break
            else:
                # Dummy read to skip over data
                f.read(length-2)
    elif fileType == 'png':
        # Dummy read to skip header data
        f.read(12)
        if f.read(4) == "IHDR":
            x, y = struct.unpack("!LL", f.read(8))
    elif fileType == 'gif':
        imgType = f.read(6)
        buf = f.read(5)
        if len(buf) == 5:
            # else: invalid/corrupted GIF (bad header)
            x, y, u = struct.unpack("<HHB", buf)
    f.close()
    if x and y:
        return float(x)/pxToCm, float(y)/pxToCm
    else:
        return x, y

class ImageImporter(DocImporter):
    '''This class allows to import into the ODT result an image stored
       externally.'''
    anchorTypes = ('page', 'paragraph', 'char', 'as-char')
    WRONG_ANCHOR = 'Wrong anchor. Valid values for anchors are: %s.'
    pictFolder = '%sPictures%s' % (os.sep, os.sep)
    def getImportFolder(self):
        return os.path.join(self.tempFolder, 'unzip', 'Pictures')

    def moveFile(self, at, importPath):
        '''Copies file at p_at into the ODT file at p_importPath.'''
        # Has this image already been imported ?
        for imagePath, imageAt in self.fileNames.iteritems():
            if imageAt == at:
                # Yes!
                i = importPath.rfind(self.pictFolder) + 1
                return importPath[:i] + imagePath
        # The image has not already been imported: copy it.
        if not at.startswith('http'):
            shutil.copy(at, importPath)
            return importPath
        # The image must be retrieved via a URL. Try to perform a HTTP GET.
        response = Resource(at).get()
        if response.code == 200:
            # At last, I can get the file format.
            self.format = mimeTypesExts[response.headers['Content-Type']]
            importPath += self.format
            f = file(importPath, 'wb')
            f.write(response.body)
            f.close()
            return importPath
        # The HTTP GET did not work, maybe for security reasons (we probably
        # have no permission to get the file). But maybe the URL was a local
        # one, from an application server running this POD code. In this case,
        # if an image resolver has been given to POD, use it to retrieve the
        # image.
        imageResolver = self.renderer.imageResolver
        if not imageResolver:
            # Return some default image explaining that the image wasn't found.
            import appy.pod
            podFolder = os.path.dirname(appy.pod.__file__)
            img = os.path.join(podFolder, 'imageNotFound.jpg')
            self.format = 'jpg'
            importPath += self.format
            f = file(img)
            imageContent = f.read()
            f.close()
            f = file(importPath, 'wb')
            f.write(imageContent)
            f.close()
        else:
            # The imageResolver is a Zope application. From it, we will
            # retrieve the object on which the image is stored and get
            # the file to download.
            urlParts = urlparse.urlsplit(at)
            path = urlParts[2][1:].split('/')[:-1]
            try:
                obj = imageResolver.unrestrictedTraverse(path)
            except KeyError:
                # Maybe a rewrite rule as added some prefix to all URLs?
                obj = imageResolver.unrestrictedTraverse(path[1:])
            zopeFile = getattr(obj, urlParts[3].split('=')[1])
            appyFile = FileWrapper(zopeFile)
            self.format = mimeTypesExts[appyFile.mimeType]
            importPath += self.format
            appyFile.dump(importPath)
        return importPath

    def init(self, anchor, wrapInPara, size, sizeUnit, style):
        '''ImageImporter-specific constructor.'''
        # Initialise anchor
        if anchor not in self.anchorTypes:
            raise PodError(self.WRONG_ANCHOR % str(self.anchorTypes))
        self.anchor = anchor
        self.wrapInPara = wrapInPara
        self.size = size
        self.sizeUnit = sizeUnit
        # Put CSS attributes from p_style in a dict.
        self.cssAttrs = {}
        if style:
            for attr in style.split(';'):
                if not attr.strip(): continue
                name, value = attr.strip().split(':')
                value = value.strip()
                if value.endswith('px'): value = value[:-2]
                if value.isdigit(): value=int(value)
                self.cssAttrs[name.strip()] = value

    def run(self):
        # Some shorcuts for the used xml namespaces
        d = self.drawNs
        t = self.textNs
        x = self.linkNs
        s = self.svgNs
        # Compute path to image
        i = self.importPath.rfind(self.pictFolder)
        imagePath = self.importPath[i+1:].replace('\\', '/')
        self.fileNames[imagePath] = self.at
        # In the case of SVG files, perform an image conversion to PNG
        if imagePath.endswith('.svg'):
            newImportPath = os.path.splitext(self.importPath)[0] + '.png'
            err= os.system('convert "%s" "%s"'% (self.importPath,newImportPath))
            if err:
                raise Exception(CONVERT_ERROR)
            os.remove(self.importPath)
            self.importPath = newImportPath
            imagePath = os.path.splitext(imagePath)[0] + '.png'
            self.format = 'png'
        # Retrieve image size from self.size.
        width = height = None
        if self.size and (self.sizeUnit != 'pc'):
            width, height = self.size
            if self.sizeUnit == 'px':
                # Convert it to cm
                width = float(width) / pxToCm
                height = float(height) / pxToCm
        # Override self.size if 'height' or 'width' is found in self.cssAttrs
        if 'width' in self.cssAttrs:
            width = float(self.cssAttrs['width']) / pxToCm
        if 'height' in self.cssAttrs:
            height = float(self.cssAttrs['height']) / pxToCm
        # If width and/or height is missing, compute it.
        if not width or not height:
            width, height = getSize(self.importPath, self.format)
            if self.sizeUnit == 'pc':
                # Apply the given percentage to the real width and height.
                width = width * (float(self.size[0])/100)
                height = height * (float(self.size[1])/100)
        if width != None:
            size = ' %s:width="%fcm" %s:height="%fcm"' % (s, width, s, height)
        else:
            size = ''
        if 'float' in self.cssAttrs:
            floatValue = self.cssAttrs['float'].capitalize()
            styleInfo = '%s:style-name="podImage%s" ' % (d, floatValue)
            self.anchor = 'char'
        else:
            styleInfo = ''
        image = '<%s:frame %s%s:name="%s" %s:z-index="0" ' \
                '%s:anchor-type="%s"%s><%s:image %s:type="simple" ' \
                '%s:show="embed" %s:href="%s" %s:actuate="onLoad"/>' \
                '</%s:frame>' % (d, styleInfo, d, self.getUuid(), d, t,
                self.anchor, size, d, x, x, x, imagePath, x, d)
        if hasattr(self, 'wrapInPara') and self.wrapInPara:
            image = '<%s:p>%s</%s:p>' % (t, image, t)
        self.res += image
        return self.res
# ------------------------------------------------------------------------------
