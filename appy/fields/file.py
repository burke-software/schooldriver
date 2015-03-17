# ------------------------------------------------------------------------------
# This file is part of Appy, a framework for building applications in the Python
# language. Copyright (C) 2007 Gaetan Delannay

# Appy is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.

# Appy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# Appy. If not, see <http://www.gnu.org/licenses/>.

# ------------------------------------------------------------------------------
import time, os.path, mimetypes, shutil
from cStringIO import StringIO
from appy import Object
from appy.fields import Field
from appy.px import Px
from appy.shared import utils as sutils
from appy.shared import UnmarshalledFile, mimeTypesExts

# ------------------------------------------------------------------------------
WRONG_FILE_TUPLE = 'This is not the way to set a file. You can specify a ' \
    '2-tuple (fileName, fileContent) or a 3-tuple (fileName, fileContent, ' \
    'mimeType).'
CONVERSION_ERROR = 'An error occurred. %s'

def guessMimeType(fileName):
    '''Try to find the MIME type of file p_fileName.'''
    return mimetypes.guess_type(fileName)[0] or File.defaultMimeType

def osPathJoin(*pathElems):
    '''Version of os.path.elems that takes care of path elems being empty
       strings.'''
    return os.path.join(*pathElems).rstrip(os.sep)

def getShownSize(size):
    '''Express p_size (a file size in bytes) in a human-readable way.'''
    # Display the size in bytes if smaller than 1024 bytes
    if size < 1024: return '%d byte(s)' % size
    size = size / 1024.0 # This is the size, in Kb
    if size < 1024: return '%s Kb' % sutils.formatNumber(size, precision=1)
    size = size / 1024.0 # This is the size, in Mb
    return '%s Mb' % sutils.formatNumber(size, precision=1)

# ------------------------------------------------------------------------------
class FileInfo:
    '''A FileInfo instance holds metadata about a file on the filesystem.

       For every File field, we will store a FileInfo instance in the dabatase;
       the real file will be stored in the Appy/ZODB database-managed
       filesystem.

       This is the primary usage of FileInfo instances. FileInfo instances can
       also be used every time we need to manipulate a file. For example, when
       getting the content of a Pod field, a temporary file may be generated and
       you will get a FileInfo that represents it.
    '''
    BYTES = 5000

    def __init__(self, fsPath, inDb=True, uploadName=None):
        '''p_fsPath is the path of the file on disk.
           - If p_inDb is True, this FileInfo will be stored in the database and
             will hold metadata about a File field whose content will lie in the
             database-controlled filesystem. In this case, p_fsPath is the path
             of the file *relative* to the root DB folder. We avoid storing
             absolute paths in order to ease the transfer of databases from one
             place to the other. Moreover, p_fsPath does not include the
             filename, that will be computed later, from the field name.

           - If p_inDb is False, this FileInfo is a simple temporary object
             representing any file on the filesystem (not necessarily in the
             db-controlled filesystem). For instance, it could represent a temp
             file generated from a Pod field in the OS temp folder. In this
             case, p_fsPath is the absolute path to the file, including the
             filename. If you manipulate such a FileInfo instance, please avoid
             using methods that are used by Appy to manipulate
             database-controlled files (like methods getFilePath, removeFile,
             writeFile or copyFile).'''
        self.fsPath = fsPath
        self.fsName = None # The name of the file in fsPath
        self.uploadName = uploadName # The name of the uploaded file
        self.size = 0 # Its size, in bytes
        self.mimeType = None # Its MIME type
        self.modified = None # The last modification date for this file.
        # Complete metadata if p_inDb is False
        if not inDb:
            self.fsName = '' # Already included in self.fsPath.
            # We will not store p_inDb. Checking if self.fsName is the empty
            # string is equivalent.
            fileInfo = os.stat(self.fsPath)
            self.size = fileInfo.st_size
            self.mimeType = guessMimeType(self.fsPath)
            from DateTime import DateTime
            self.modified = DateTime(fileInfo.st_mtime)

    def getFilePath(self, obj):
        '''Returns the absolute file name of the file on disk that corresponds
           to this FileInfo instance.'''
        dbFolder, folder = obj.o.getFsFolder()
        return osPathJoin(dbFolder, folder, self.fsName)

    def removeFile(self, dbFolder='', removeEmptyFolders=False):
        '''Removes the file from the filesystem.'''
        try:
            os.remove(osPathJoin(dbFolder, self.fsPath, self.fsName))
        except Exception, e:
            # If the current ZODB transaction is re-triggered, the file may
            # already have been deleted.
            pass
        # Don't leave empty folders on disk. So delete folder and parent folders
        # if this removal leaves them empty (unless p_removeEmptyFolders is
        # False).
        if removeEmptyFolders:
            sutils.FolderDeleter.deleteEmpty(osPathJoin(dbFolder,self.fsPath))

    def normalizeFileName(self, name):
        '''Normalizes file p_name.'''
        return name[max(name.rfind('/'), name.rfind('\\'), name.rfind(':'))+1:]

    def getShownSize(self): return getShownSize(self.size)

    def replicateFile(self, src, dest):
        '''p_src and p_dest are open file handlers. This method copies content
           of p_src to p_dest and returns the file size. Note that p_src can
           also be binary data in a string.'''
        size = 0
        if isinstance(src, str): src = StringIO(src)
        while True:
            chunk = src.read(self.BYTES)
            if not chunk: break
            size += len(chunk)
            dest.write(chunk)
        return size

    def writeFile(self, fieldName, fileObj, dbFolder):
        '''Writes to the filesystem the p_fileObj file, that can be:
           - a Zope FileUpload (coming from a HTTP post);
           - a OFS.Image.File object (legacy within-ZODB file object);
           - a tuple (fileName, fileContent, mimeType)
             (see doc in method File.store below).'''
        # Determine p_fileObj's type.
        fileType = fileObj.__class__.__name__
        # Set MIME type.
        if fileType == 'FileUpload':
            mimeType = fileObj.headers.get('content-type')
        elif fileType == 'File':
            mimeType = fileObj.content_type
        else:
            mimeType = fileObj[2]
        self.mimeType = mimeType or File.defaultMimeType
        # Determine the original name of the file to store.
        fileName= fileType.startswith('File') and fileObj.filename or fileObj[0]
        if not fileName:
            # Name it according to field name. Deduce file extension from the
            # MIME type.
            ext = (self.mimeType in mimeTypesExts) and \
                  mimeTypesExts[self.mimeType] or 'bin'
            fileName = '%s.%s' % (fieldName, ext)
        # As a preamble, extract file metadata from p_fileObj and store it in
        # this FileInfo instance.
        name = self.normalizeFileName(fileName)
        self.uploadName = name
        self.fsName = '%s%s' % (fieldName, os.path.splitext(name)[1].lower())
        # Write the file on disk (and compute/get its size in bytes)
        fsName = osPathJoin(dbFolder, self.fsPath, self.fsName)
        f = file(fsName, 'wb')
        if fileType == 'FileUpload':
            # Write the FileUpload instance on disk.
            self.size = self.replicateFile(fileObj, f)
        elif fileType == 'File':
            # Write the File instance on disk.
            if fileObj.data.__class__.__name__ == 'Pdata':
                # The file content is splitted in several chunks.
                f.write(fileObj.data.data)
                nextPart = fileObj.data.next
                while nextPart:
                    f.write(nextPart.data)
                    nextPart = nextPart.next
            else:
                # Only one chunk
                f.write(fileObj.data)
            self.size = fileObj.size
        else:
            # Write fileObj[1] on disk.
            if fileObj[1].__class__.__name__ == 'file':
                # It is an open file handler.
                self.size = self.replicateFile(fileObj[1], f)
            else:
                # We have file content directly in fileObj[1]
                self.size = len(fileObj[1])
                f.write(fileObj[1])
        f.close()
        from DateTime import DateTime
        self.modified = DateTime()

    def copyFile(self, fieldName, filePath, dbFolder):
        '''Copies the "external" file stored at p_filePath in the db-controlled
           file system, for storing a value for p_fieldName.'''
        # Set names for the file
        name = self.normalizeFileName(filePath)
        self.uploadName = name
        self.fsName = '%s%s' % (fieldName, os.path.splitext(name)[1])
        # Set mimeType
        self.mimeType = guessMimeType(filePath)
        # Copy the file
        fsName = osPathJoin(dbFolder, self.fsPath, self.fsName)
        shutil.copyfile(filePath, fsName)
        from DateTime import DateTime
        self.modified = DateTime()
        self.size = os.stat(fsName).st_size

    def writeResponse(self, response, dbFolder='', disposition='inline'):
        '''Writes this file in the HTTP p_response object.'''
        # As a preamble, initialise response headers.
        header = response.setHeader
        header('Content-Disposition',
               '%s;filename="%s"' % (disposition, self.uploadName))
        header('Content-Type', self.mimeType)
        header('Content-Length', self.size)
        header('Accept-Ranges', 'bytes')
        header('Last-Modified', self.modified.rfc822())
        #sh('Cachecontrol', 'no-cache')
        #sh('Expires', 'Thu, 11 Dec 1975 12:05:05 GMT')
        # Write the file in the response
        fsName = osPathJoin(dbFolder, self.fsPath, self.fsName)
        f = file(fsName, 'rb')
        while True:
            chunk = f.read(self.BYTES)
            if not chunk: break
            response.write(chunk)
        f.close()

    def dump(self, obj, filePath=None, format=None):
        '''Exports this file to disk (outside the db-controller filesystem).
           The tied Appy p_obj(ect) is required. If p_filePath is specified, it
           is the path name where the file will be dumped; folders mentioned in
           it must exist. If not, the file will be dumped in the OS temp folder.
           The absolute path name of the dumped file is returned. If an error
           occurs, the method returns None. If p_format is specified,
           LibreOffice will be called for converting the dumped file to the
           desired format.'''
        if not filePath:
            filePath = '%s/file%f.%s' % (sutils.getOsTempFolder(), time.time(),
                                         self.fsName)
        # Copies the file to disk.
        shutil.copyfile(self.getFilePath(obj), filePath)
        if format:
            # Convert the dumped file using LibreOffice
            errorMessage = obj.tool.convert(filePath, format)
            # Even if we have an "error" message, it could be a simple warning.
            # So we will continue here and, as a subsequent check for knowing if
            # an error occurred or not, we will test the existence of the
            # converted file (see below).
            os.remove(filePath)
            # Return the name of the converted file.
            baseName, ext = os.path.splitext(filePath)
            if (ext == '.%s' % format):
                filePath = '%s.res.%s' % (baseName, format)
            else:
                filePath = '%s.%s' % (baseName, format)
            if not os.path.exists(filePath):
                obj.log(CONVERSION_ERROR % errorMessage, type='error')
                return
        return filePath

# ------------------------------------------------------------------------------
class File(Field):

    pxView = pxCell = Px('''
     <x var="downloadUrl='%s/download?name=%s' % (zobj.absolute_url(), name);
             shownSize=value and value.getShownSize() or 0">
      <x if="value and not field.isImage">
       <a href=":downloadUrl">:value.uploadName</a>&nbsp;&nbsp;-
       <i class="discreet">:shownSize</i>
      </x>
      <x if="value and field.isImage">
       <img src=":downloadUrl"
            title=":'%s, %s' % (value.uploadName, shownSize)"/></x>
      <x if="not value">-</x>
     </x>''')

    pxEdit = Px('''
     <x var="fName=q('%s_file' % name)">
      <x if="value">:field.pxView</x><br if="value"/>
      <x if="value">
       <!-- Keep the file unchanged. -->
       <input type="radio" value="nochange"
              checked=":value and 'checked' or None"
              name=":'%s_delete' % name" id=":'%s_nochange' % name"
              onclick=":'document.getElementById(%s).disabled=true' % fName"/>
       <label lfor=":'%s_nochange' % name">Keep the file unchanged</label><br/>
       <!-- Delete the file. -->
       <x if="not field.required">
        <input type="radio" value="delete"
               name=":'%s_delete' % name" id=":'%s_delete' % name"
               onclick=":'document.getElementById(%s).disabled=true' % fName"/>
        <label lfor=":'%s_delete' % name">Delete the file</label><br/>
       </x>
       <!-- Replace with a new file. -->
       <input type="radio" value=""
              checked=":not value and 'checked' or None"
              name=":'%s_delete' % name" id=":'%s_upload' % name"
              onclick=":'document.getElementById(%s).disabled=false' % fName"/>
       <label lfor=":'%s_upload' % name">Replace it with a new file</label><br/>
      </x>
      <!-- The upload field. -->
      <input type="file" name=":'%s_file' % name" id=":'%s_file' % name"
             size=":field.width"/>
      <script var="isDisabled=not value and 'false' or 'true'"
             type="text/javascript">:'document.getElementById(%s).disabled=%s'%\
                                     (fName, isDisabled)</script></x>''')

    pxSearch = ''

    def __init__(self, validator=None, multiplicity=(0,1), default=None,
                 show=True, page='main', group=None, layouts=None, move=0,
                 indexed=False, searchable=False, specificReadPermission=False,
                 specificWritePermission=False, width=None, height=None,
                 maxChars=None, colspan=1, master=None, masterValue=None,
                 focus=False, historized=False, mapping=None, label=None,
                 isImage=False, sdefault='', scolspan=1, swidth=None,
                 sheight=None):
        self.isImage = isImage
        Field.__init__(self, validator, multiplicity, default, show, page,
                       group, layouts, move, indexed, False,
                       specificReadPermission, specificWritePermission, width,
                       height, None, colspan, master, masterValue, focus,
                       historized, mapping, label, sdefault, scolspan, swidth,
                       sheight, True)

    def getRequestValue(self, obj, requestName=None):
        name = requestName or self.name
        return obj.REQUEST.get('%s_file' % name)

    def getCopyValue(self, obj): raise Exception('Not implemented yet.')
    def getDefaultLayouts(self): return {'view':'l-f','edit':'lrv-f'}

    def isEmptyValue(self, obj, value):
        '''Must p_value be considered as empty?'''
        if value: return
        # If "nochange", the value must not be considered as empty
        return obj.REQUEST.get('%s_delete' % self.name) != 'nochange'

    imageExts = ('.jpg', '.jpeg', '.png', '.gif')
    def validateValue(self, obj, value):
        form = obj.REQUEST.form
        action = '%s_delete' % self.name
        if (not value or not value.filename) and form.has_key(action) and \
            not form[action]:
            # If this key is present but empty, it means that the user selected
            # "replace the file with a new one". So in this case he must provide
            # a new file to upload.
            return obj.translate('file_required')
        # Check that, if self.isImage, the uploaded file is really an image
        if value and value.filename and self.isImage:
            ext = os.path.splitext(value.filename)[1].lower()
            if ext not in File.imageExts:
                return obj.translate('image_required')

    defaultMimeType = 'application/octet-stream'
    def store(self, obj, value):
        '''Stores the p_value that represents some file. p_value can be:
           a. an instance of Zope class ZPublisher.HTTPRequest.FileUpload. In
              this case, it is file content coming from a HTTP POST;
           b. an instance of Zope class OFS.Image.File (legacy within-ZODB file
              object);
           c. an instance of appy.shared.UnmarshalledFile. In this case, the
              file comes from a peer Appy site, unmarshalled from XML content
              sent via an HTTP request;
           d. a string. In this case, the string represents the path of a file
              on disk;
           e. a 2-tuple (fileName, fileContent) where:
              - fileName is the name of the file (ie "myFile.odt")
              - fileContent is the binary or textual content of the file or an
                open file handler.
           f. a 3-tuple (fileName, fileContent, mimeType) where
              - fileName and fileContent have the same meaning than above;
              - mimeType is the MIME type of the file.
        '''
        zobj = obj.o
        if value:
            # There is a new value to store. Get the folder on disk where to
            # store the new file.
            dbFolder, folder = zobj.getFsFolder(create=True)
            # Remove the previous file if it existed.
            info = getattr(obj.aq_base, self.name, None)
            if info:
                # The previous file can be a legacy File object in an old
                # database we are migrating.
                if isinstance(info, FileInfo): info.removeFile(dbFolder)
                else: delattr(obj, self.name)
            # Store the new file. As a preamble, create a FileInfo instance.
            info = FileInfo(folder)
            cfg = zobj.getProductConfig()
            if isinstance(value, cfg.FileUpload) or isinstance(value, cfg.File):
                # Cases a, b
                value.filename = value.filename.replace('/', '-')
                info.writeFile(self.name, value, dbFolder)
            elif isinstance(value, UnmarshalledFile):
                # Case c
                fileInfo = (value.name, value.content, value.mimeType)
                info.writeFile(self.name, fileInfo, dbFolder)
            elif isinstance(value, basestring):
                # Case d
                info.copyFile(self.name, value, dbFolder)
            else:
                # Cases e, f. Extract file name, content and MIME type.
                fileName = mimeType = None
                if len(value) == 2:
                    fileName, fileContent = value
                elif len(value) == 3:
                    fileName, fileContent, mimeType = value
                if not fileName:
                    raise Exception(WRONG_FILE_TUPLE)
                mimeType = mimeType or guessMimeType(fileName)
                info.writeFile(self.name, (fileName, fileContent, mimeType),
                               dbFolder)
            # Store the FileInfo instance in the database.
            setattr(obj, self.name, info)
        else:
            # I store value "None", excepted if I find in the request the desire
            # to keep the file unchanged.
            action = None
            rq = getattr(zobj, 'REQUEST', None)
            if rq: action = rq.get('%s_delete' % self.name, None)
            if action != 'nochange':
                # Delete the file on disk
                info = getattr(zobj.aq_base, self.name, None)
                if info:
                    info.removeFile(zobj.getDbFolder(), removeEmptyFolders=True)
                # Delete the FileInfo in the DB
                setattr(zobj, self.name, None)
# ------------------------------------------------------------------------------
