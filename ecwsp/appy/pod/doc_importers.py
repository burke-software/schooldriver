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
import os, os.path, time, shutil, struct, random
from appy.pod import PodError
from appy.pod.odf_parser import OdfEnvironment
from appy.shared.utils import FileWrapper

# ------------------------------------------------------------------------------
FILE_NOT_FOUND = "'%s' does not exist or is not a file."
PDF_TO_IMG_ERROR = 'A PDF file could not be converted into images. Please ' \
                   'ensure that Ghostscript (gs) is installed on your ' \
                   'system and the "gs" program is in the path.'

# ------------------------------------------------------------------------------
class DocImporter:
    '''Base class used for importing external content into a pod template (an
       image, another pod template, another odt document...'''
    def __init__(self, content, at, format, tempFolder, ns, fileNames):
        self.content = content
        # If content is None, p_at tells us where to find it (file system path,
        # url, etc)
        self.at = at
        # Ensure this path exists.
        if at and not os.path.isfile(at): raise PodError(FILE_NOT_FOUND % at)
        self.format = format
        self.res = u''
        self.ns = ns
        # Unpack some useful namespaces
        self.textNs = ns[OdfEnvironment.NS_TEXT]
        self.linkNs = ns[OdfEnvironment.NS_XLINK]
        self.drawNs = ns[OdfEnvironment.NS_DRAW]
        self.svgNs = ns[OdfEnvironment.NS_SVG]
        self.tempFolder = tempFolder
        self.importFolder = self.getImportFolder()
        # Create the import folder if it does not exist.
        if not os.path.exists(self.importFolder): os.mkdir(self.importFolder)
        self.importPath = self.getImportPath(at, format)
        # A link to the global fileNames dict (explained in renderer.py)
        self.fileNames = fileNames
        if at:
            # Move the file within the ODT, if it is an image and if this image
            # has not already been imported.
            self.importPath = self.moveFile(at, self.importPath)
        else:
            # We need to dump the file content (in self.content) in a temp file
            # first. self.content may be binary, a file handler or a
            # FileWrapper.
            if isinstance(self.content, file):
                fileContent = self.content.read()
            elif isinstance(self.content, FileWrapper):
                fileContent = content.content
            else:
                fileContent = self.content
            f = file(self.importPath, 'wb')
            f.write(fileContent)
            f.close()
        # ImageImporter adds additional, image-specific attrs, through
        # ImageImporter.setImageInfo.

    def getImportFolder(self):
        '''This method must be overridden and gives the path where to dump the
           content of the document or image. In the case of a document it is a
           temp folder; in the case of an image it is a folder within the ODT
           result.'''

    def getImportPath(self, at, format):
        '''Gets the path name of the file to dump on disk (within the ODT for
           images, in a temp folder for docs).'''
        if not format:
            format = os.path.splitext(at)[1][1:]
        fileName = 'f.%d.%f.%s' % (random.randint(0,10), time.time(), format)
        return os.path.abspath('%s/%s' % (self.importFolder, fileName))

    def moveFile(self, at, importPath):
        '''In the case parameter "at" was used, we may want to move the file at
           p_at within the ODT result in p_importPath (for images) or do
           nothing (for docs). In the latter case, the file to import stays
           at _at, and is not copied into p_importPath.'''
        return at

class OdtImporter(DocImporter):
    '''This class allows to import the content of another ODT document into a
       pod template.'''
    def getImportFolder(self): return '%s/docImports' % self.tempFolder
    def run(self):
        self.res += '<%s:section %s:name="PodImportSection%f">' \
                    '<%s:section-source %s:href="%s" ' \
                    '%s:filter-name="writer8"/></%s:section>' % (
                        self.textNs, self.textNs, time.time(), self.textNs,
                        self.linkNs, self.importPath, self.textNs, self.textNs)
        return self.res

class PdfImporter(DocImporter):
    '''This class allows to import the content of a PDF file into a pod
       template. It calls gs to split the PDF into images and calls the
       ImageImporter for importing it into the result.'''
    imagePrefix = 'PdfPart'
    def getImportFolder(self): return '%s/docImports' % self.tempFolder
    def run(self):
        # Split the PDF into images with Ghostscript
        imagesFolder = os.path.dirname(self.importPath)
        cmd = 'gs -dNOPAUSE -dBATCH -sDEVICE=jpeg -r125x125 ' \
              '-sOutputFile=%s/%s%%d.jpg %s' % \
              (imagesFolder, self.imagePrefix, self.importPath)
        os.system(cmd)
        # Check that at least one image was generated
        succeeded = False
        firstImage = '%s1.jpg' % self.imagePrefix
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
            nextImage = '%s/%s%d.jpg' % (imagesFolder, self.imagePrefix, i)
            if os.path.exists(nextImage):
                # Use internally an Image importer for doing this job.
                imgImporter = ImageImporter(None, nextImage, 'jpg',
                    self.tempFolder, self.ns, self.fileNames)
                imgImporter.setAnchor('paragraph')
                self.res += imgImporter.run()
                os.remove(nextImage)
            else:
                noMoreImages = True
        return self.res

# Compute size of images -------------------------------------------------------
jpgTypes = ('jpg', 'jpeg')
pxToCm = 44.173513561
def getSize(filePath, fileType):
    '''Gets the size of an image by reading first bytes.'''
    x, y = (None, None)
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
    return float(x)/pxToCm, float(y)/pxToCm

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
        # If I am here, the image has not already been imported: copy it.
        shutil.copy(at, importPath)
        return importPath

    def setImageInfo(self, anchor, wrapInPara, size):
        # Initialise anchor
        if anchor not in self.anchorTypes:
            raise PodError(self.WRONG_ANCHOR % str(self.anchorTypes))
        self.anchor = anchor
        self.wrapInPara = wrapInPara
        self.size = size

    def run(self):
        # Some shorcuts for the used xml namespaces
        d = self.drawNs
        t = self.textNs
        x = self.linkNs
        s = self.svgNs
        imageName = 'Image%f' % time.time()
        # Compute path to image
        i = self.importPath.rfind(self.pictFolder)
        imagePath = self.importPath[i+1:].replace('\\', '/')
        self.fileNames[imagePath] = self.at
        # Compute image size, or retrieve it from self.size if given
        if self.size:
            width, height = self.size
        else:
            width, height = getSize(self.importPath, self.format)
        if width != None:
            size = ' %s:width="%fcm" %s:height="%fcm"' % (s, width, s, height)
        else:
            size = ''
        image = '<%s:frame %s:name="%s" %s:z-index="0" %s:anchor-type="%s"%s>' \
                '<%s:image %s:type="simple" %s:show="embed" %s:href="%s" ' \
                '%s:actuate="onLoad"/></%s:frame>' % (d, d, imageName, d, t, \
                self.anchor, size, d, x, x, x, imagePath, x, d)
        if hasattr(self, 'wrapInPara') and self.wrapInPara:
            image = '<%s:p>%s</%s:p>' % (t, image, t)
        self.res += image
        return self.res
# ------------------------------------------------------------------------------
