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
import time, os.path, mimetypes
from appy import Object
from appy.fields import Field
from appy.px import Px
from appy.shared import utils as sutils

# ------------------------------------------------------------------------------
class File(Field):

    pxView = pxCell = Px('''
     <x var="info=field.getFileInfo(value);
             empty=not info.size;
             imgSrc='%s/download?name=%s' % (zobj.absolute_url(), name)">
      <x if="not empty and not field.isImage">
       <a href=":imgSrc">:info.filename</a>&nbsp;&nbsp;-
       <i class="discreet">'%sKb' % (info.size / 1024)"></i>
      </x>
      <x if="not empty and field.isImage"><img src=":imgSrc"/></x>
      <x if="empty">-</x>
     </x>''')

    pxEdit = Px('''
     <x var="info=field.getFileInfo(value);
             empty= not info.size;
             fName=q('%s_file' % name)">

      <x if="not empty">:field.pxView</x><br/>
      <x if="not empty">
       <!-- Keep the file unchanged. -->
       <input type="radio" value="nochange"
              checked=":(info.size != 0) and 'checked' or None"
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
              checked=":(info.size == 0) and 'checked' or None"
              name=":'%s_delete' % name" id=":'%s_upload' % name"
              onclick=":'document.getElementById(%s).disabled=false' % fName"/>
       <label lfor=":'%s_upload' % name">Replace it with a new file</label><br/>
      </x>
      <!-- The upload field. -->
      <input type="file" name=":'%s_file' % name" id=":'%s_file' % name"
             size=":field.width"/>
      <script var="isDisabled=empty and 'false' or 'true'"
              type="text/javascript">:document.getElementById(%s).disabled=%s'%\
                                      (q(fName), q(isDisabled))">
      </script>
     </x>''')

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
                       historized, True, mapping, label, sdefault, scolspan,
                       swidth, sheight)

    @staticmethod
    def getFileObject(filePath, fileName=None, zope=False):
        '''Returns a File instance as can be stored in the database or
           manipulated in code, filled with content from a file on disk,
           located at p_filePath. If you want to give it a name that is more
           sexy than the actual basename of filePath, specify it in
           p_fileName.

           If p_zope is True, it will be the raw Zope object = an instance of
           OFS.Image.File. Else, it will be a FileWrapper instance from Appy.'''
        f = file(filePath, 'rb')
        if not fileName:
            fileName = os.path.basename(filePath)
        fileId = 'file.%f' % time.time()
        import OFS.Image
        res = OFS.Image.File(fileId, fileName, f)
        res.filename = fileName
        res.content_type = mimetypes.guess_type(fileName)[0]
        f.close()
        if not zope: res = sutils.FileWrapper(res)
        return res

    def getValue(self, obj):
        value = Field.getValue(self, obj)
        if value: value = sutils.FileWrapper(value)
        return value

    def getFormattedValue(self, obj, value, showChanges=False):
        if not value: return value
        return value._zopeFile

    def getRequestValue(self, request, requestName=None):
        name = requestName or self.name
        return request.get('%s_file' % name)

    def getDefaultLayouts(self): return {'view':'l-f','edit':'lrv-f'}

    def isEmptyValue(self, value, obj=None):
        '''Must p_value be considered as empty?'''
        if not obj: return Field.isEmptyValue(self, value)
        if value: return False
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
           * an instance of Zope class ZPublisher.HTTPRequest.FileUpload. In
             this case, it is file content coming from a HTTP POST;
           * an instance of Zope class OFS.Image.File;
           * an instance of appy.shared.utils.FileWrapper, which wraps an
             instance of OFS.Image.File and adds useful methods for manipulating
             it;
           * a string. In this case, the string represents the path of a file
             on disk;
           * a 2-tuple (fileName, fileContent) where:
             - fileName is the name of the file (ie "myFile.odt")
             - fileContent is the binary or textual content of the file or an
                           open file handler.
           * a 3-tuple (fileName, fileContent, mimeType) where
             - fileName and fileContent have the same meaning than above;
             - mimeType is the MIME type of the file.
        '''
        if value:
            ZFileUpload = obj.o.getProductConfig().FileUpload
            OFSImageFile = obj.o.getProductConfig().File
            if isinstance(value, ZFileUpload):
                # The file content comes from a HTTP POST.
                # Retrieve the existing value, or create one if None
                existingValue = getattr(obj.aq_base, self.name, None)
                if not existingValue:
                    existingValue = OFSImageFile(self.name, '', '')
                # Set mimetype
                if value.headers.has_key('content-type'):
                    mimeType = value.headers['content-type']
                else:
                    mimeType = File.defaultMimeType
                existingValue.content_type = mimeType
                # Set filename
                fileName = value.filename
                filename= fileName[max(fileName.rfind('/'),fileName.rfind('\\'),
                                       fileName.rfind(':'))+1:]
                existingValue.filename = fileName
                # Set content
                existingValue.manage_upload(value)
                setattr(obj, self.name, existingValue)
            elif isinstance(value, OFSImageFile):
                setattr(obj, self.name, value)
            elif isinstance(value, sutils.FileWrapper):
                setattr(obj, self.name, value._zopeFile)
            elif isinstance(value, basestring):
                setattr(obj, self.name, File.getFileObject(value, zope=True))
            elif type(value) in sutils.sequenceTypes:
                # It should be a 2-tuple or 3-tuple
                fileName = None
                mimeType = None
                if len(value) == 2:
                    fileName, fileContent = value
                elif len(value) == 3:
                    fileName, fileContent, mimeType = value
                else:
                    raise WRONG_FILE_TUPLE
                if fileName:
                    fileId = 'file.%f' % time.time()
                    zopeFile = OFSImageFile(fileId, fileName, fileContent)
                    zopeFile.filename = fileName
                    if not mimeType:
                        mimeType = mimetypes.guess_type(fileName)[0]
                    zopeFile.content_type = mimeType
                    setattr(obj, self.name, zopeFile)
        else:
            # I store value "None", excepted if I find in the request the desire
            # to keep the file unchanged.
            action = None
            rq = getattr(obj, 'REQUEST', None)
            if rq: action = rq.get('%s_delete' % self.name, None)
            if action == 'nochange': pass
            else: setattr(obj, self.name, None)

    def getFileInfo(self, fileObject):
        '''Returns filename and size of p_fileObject.'''
        if not fileObject: return Object(filename='', size=0)
        return Object(filename=fileObject.filename, size=fileObject.size)
# ------------------------------------------------------------------------------
