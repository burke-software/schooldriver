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
import os, os.path, time, shutil, struct
from appy.pod import PodError
from appy.pod.odf_parser import OdfEnvironment

# ------------------------------------------------------------------------------
FILE_NOT_FOUND = "'%s' does not exist or is not a file."
PDF_TO_IMG_ERROR = 'A PDF file could not be converted into images. Please ' \
                   'ensure that Ghostscript (gs) is installed on your ' \
                   'system and the "gs" program is in the path.'

# ------------------------------------------------------------------------------
class DocImporter:
    '''Base class used for importing external content into a pod template (an
       image, another pod template, another odt document...'''
    def __init__(self, content, at, format, tempFolder, ns):
        self.content = content
        self.at = at # If content is None, p_at tells us where to find it
        # (file system path, url, etc)
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
        # If the importer generates one or several images, we will retain their
        # names here, because we will need to declare them in
        # META-INF/manifest.xml
        self.fileNames = []
        if self.at:
            # Check that the file exists
            if not os.path.isfile(self.at):
                raise PodError(FILE_NOT_FOUND % self.at)
            self.importPath = self.moveFile(self.at)
        else:
            # We need to dump the file content (in self.content) in a temp file
            # first. self.content may be binary or a file handler.
            if not os.path.exists(self.importFolder):
                os.mkdir(self.importFolder)
            if isinstance(self.content, file):
                self.fileName = os.path.basename(self.content.name)
                fileContent = self.content.read()
            else:
                self.fileName = 'f%f.%s' % (time.time(), self.format)
                fileContent = self.content
            self.importPath = self.getImportPath(self.fileName)
            theFile = file(self.importPath, 'w')
            theFile.write(fileContent)
            theFile.close()
        self.importPath = os.path.abspath(self.importPath)
    def getImportFolder(self):
        '''This method must be overridden and gives the path where to dump the
           content of the document or image. In the case of a document it is a
           temp folder; in the case of an image it is a folder within the ODT
           result.'''
        pass
    def getImportPath(self, fileName):
        '''Import path is the path to the external file or image that is now
           stored on disk. We check here that this name does not correspond
           to an existing file; if yes, we change the path until we get a path
           that does not correspond to an existing file.'''
        res = '%s/%s' % (self.importFolder, fileName)
        resIsGood = False
        while not resIsGood:
            if not os.path.exists(res):
                resIsGood = True
            else:
                # We must find another file name, this one already exists.
                name, ext = os.path.splitext(res)
                name += 'g'
                res = name + ext
        return res
    def moveFile(self, at):
        '''In the case parameter "at" was used, we may want to move the file at
           p_at within the ODT result (for images) or do nothing (for
           documents).'''
        return at

class OdtImporter(DocImporter):
    '''This class allows to import the content of another ODT document into a
       pod template.'''
    def getImportFolder(self):
        return '%s/docImports' % self.tempFolder
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
    def getImportFolder(self):
        return '%s/docImports' % self.tempFolder
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
        if not succeeded:
            raise PodError(PDF_TO_IMG_ERROR)
        # Insert images into the result.
        noMoreImages = False
        i = 0
        while not noMoreImages:
            i += 1
            nextImage = '%s/%s%d.jpg' % (imagesFolder, self.imagePrefix, i)
            if os.path.exists(nextImage):
                # Use internally an Image importer for doing this job.
                imgImporter = ImageImporter(None, nextImage, 'jpg',
                    self.tempFolder, self.ns)
                imgImporter.setAnchor('paragraph')
                self.res += imgImporter.run()
                self.fileNames += imgImporter.fileNames
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
    f = file(filePath)
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
    def getImportFolder(self):
        return '%s/unzip/Pictures' % self.tempFolder
    def moveFile(self, at):
        '''Image to insert is at p_at. We must move it into the ODT result.'''
        fileName = os.path.basename(at)
        folderName = self.getImportFolder()
        if not os.path.exists(folderName):
            os.mkdir(folderName)
        res = self.getImportPath(fileName)
        shutil.copy(at, res)
        return res
    def setAnchor(self, anchor):
        if anchor not in self.anchorTypes:
            raise PodError(self.WRONG_ANCHOR % str(self.anchorTypes))
        self.anchor = anchor
    def run(self):
        # Some shorcuts for the used xml namespaces
        d = self.drawNs
        t = self.textNs
        x = self.linkNs
        s = self.svgNs
        imageName = 'Image%f' % time.time()
        # Compute path to image
        i = self.importPath.rfind('/Pictures/')
        imagePath = self.importPath[i+1:]
        self.fileNames.append(imagePath)
        # Compute image size
        width, height = getSize(self.importPath, self.format)
        if width != None:
            size = ' %s:width="%fcm" %s:height="%fcm"' % (s, width, s, height)
        else:
            size = ''
        self.res += '<%s:p><%s:frame %s:name="%s" %s:z-index="0" ' \
                    '%s:anchor-type="%s"%s><%s:image %s:type="simple" ' \
                    '%s:show="embed" %s:href="%s" %s:actuate="onLoad"/>' \
                    '</%s:frame></%s:p>' % \
                    (t, d, d, imageName, d, t, self.anchor, size, d, x, x, x,
                     imagePath, x, d, t)
        return self.res
# ------------------------------------------------------------------------------
