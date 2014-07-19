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
import time, os, os.path
from file import FileInfo
from appy import Object
from appy.fields import Field
from appy.px import Px
from appy.gen.layout import Table
from appy.gen import utils as gutils
from appy.pod import PodError
from appy.pod.renderer import Renderer
from appy.shared import utils as sutils

# ------------------------------------------------------------------------------
class Pod(Field):
    '''A pod is a field allowing to produce a (PDF, ODT, Word, RTF...) document
       from data contained in Appy class and linked objects or anything you
       want to put in it. It is the way gen uses pod.'''
    # Layout for rendering a POD field for exporting query results.
    rLayouts = {'view': 'fl!'}
    allFormats = {'.odt': ('pdf', 'doc', 'odt'), '.ods': ('xls', 'ods')}
    POD_ERROR = 'An error occurred while generating the document. Please ' \
                'contact the system administrator.'
    NO_TEMPLATE = 'Please specify a pod template in field "template".'
    UNAUTHORIZED = 'You are not allow to perform this action.'
    TEMPLATE_NOT_FOUND = 'Template not found at %s.'
    FREEZE_ERROR = 'Error while trying to freeze a "%s" file in pod field ' \
                    '"%s" (%s).'
    FREEZE_FATAL_ERROR = 'Server error. Please contact the administrator.'

    # Icon allowing to generate a given template in a given format.
    pxIcon = Px('''
     <img var="iconSuffix=frozen and 'Frozen' or ''"
          src=":url(fmt + iconSuffix)" class="clickable"
          title=":field.getIconTitle(obj, fmt, frozen)"
          onclick=":'generatePod(%s,%s,%s,%s,%s)' % (q(uid), q(name), \
                    q(info.template), q(fmt), q(ztool.getQueryInfo()))"/>''')

    pxView = pxCell = Px('''
     <x var="uid=obj.uid"
        for="info in field.getVisibleTemplates(obj)">
      <x for="fmt in info.formats"
         var2="freezeAllowed=(fmt in info.freezeFormats) and \
                             (field.show != 'result');
               frozen=field.isFrozen(obj, info.template, fmt)">
       <!-- A clickable icon if no freeze action is allowed -->
       <x if="not freezeAllowed">:field.pxIcon</x>
       <!-- A clickable icon and a dropdown menu else. -->
       <span if="freezeAllowed" class="dropdownMenu"
             var2="dropdownId='%s_%s' % (uid, \
                              field.getFreezeName(info.template, fmt, sep='_'))"
             onmouseover=":'toggleDropdown(%s)' % q(dropdownId)"
             onmouseout=":'toggleDropdown(%s,%s)' % (q(dropdownId), q('none'))">
        <x>:field.pxIcon</x>
        <!-- The dropdown menu containing freeze actions -->
        <table id=":dropdownId" class="dropdown" width="75px">
         <!-- Unfreeze -->
         <tr if="frozen" valign="top">
          <td>
           <a onclick=":'freezePod(%s,%s,%s,%s,%s)' % (q(uid), q(name), \
                        q(info.template), q(fmt), q('unfreeze'))"
              class="smaller">:_('unfreezeField')</a>
          </td>
          <td align="center"><img src=":url('unfreeze')"/></td>
         </tr>
         <!-- (Re-)freeze -->
         <tr valign="top">
          <td>
           <a onclick=":'freezePod(%s,%s,%s,%s,%s)' % (q(uid), q(name), \
                        q(info.template), q(fmt), q('freeze'))"
              class="smaller">:_('freezeField')</a>
          </td>
          <td align="center"><img src=":url('freeze')"/></td>
         </tr>
         <!-- (Re-)upload -->
         <tr valign="top">
          <td>
           <a onclick=":'uploadPod(%s,%s,%s,%s)' % (q(uid), q(name), \
                        q(info.template), q(fmt))"
              class="smaller">:_('uploadField')</a>
          </td>
          <td align="center"><img src=":url('upload')"/></td>
         </tr>
        </table>
       </span>
      </x> 
      <!-- Show the specific template name only if there is more than one
           template. For a single template, the field label already does the
           job. -->
      <span if="len(field.template) &gt; 1"
            class=":not loop.info.last and 'pod smaller' or \
                    'smaller'">:field.getTemplateName(obj, info.template)</span>
     </x>''')

    pxEdit = pxSearch = ''

    def __init__(self, validator=None, default=None, show=('view', 'result'),
                 page='main', group=None, layouts=None, move=0, indexed=False,
                 searchable=False, specificReadPermission=False,
                 specificWritePermission=False, width=None, height=None,
                 maxChars=None, colspan=1, master=None, masterValue=None,
                 focus=False, historized=False, mapping=None, label=None,
                 template=None, templateName=None, showTemplate=None,
                 freezeTemplate=None, context=None, stylesMapping={},
                 formats=None):
        # Param "template" stores the path to the pod template(s).
        if not template: raise Exception(Pod.NO_TEMPLATE)
        if isinstance(template, basestring):
            self.template = [template]
        else:
            self.template = template
        # Param "templateName", if specified, is a method that will be called
        # with the current template (from self.template) as single arg and must
        # return the name of this template. If self.template stores a single
        # template, you have no need to use param "templateName". Simply use the
        # field label to name the template. But if you have a multi-pod field
        # (with several templates specified as a list or tuple in param
        # "template"), you will probably choose to hide the field label and use
        # param "templateName" to give a specific name to every template. If
        # "template" contains several templates and "templateName" is None, Appy
        # will produce names from template filenames.
        self.templateName = templateName
        # "showTemplate" determines if the current user may generate documents
        # based on this pod field. More precisely, "showTemplate", if specified,
        # must be a method that will be called with the current template as
        # single arg (one among self.template) and that must return the list or
        # tuple of formats that the current user may use as output formats for
        # generating a document. If the current user is not allowed at all to
        # generate documents based on the current template, "showTemplate" must
        # return an empty tuple/list. If "showTemplate" is not specified, the
        # user will be able to generate documents based on the current template,
        # in any format from self.formats (see below).
        # "showTemplate" comes in addition to self.show. self.show dictates the
        # visibility of the whole field (ie, all templates from self.template)
        # while "showTemplate" dictates the visiblity of a specific template
        # within self.template.
        self.showTemplate = showTemplate
        # "freezeTemplate" determines if the current user may freeze documents
        # normally generated dynamically from this pod field. More precisely,
        # "freezeTemplate", if specified, must be a method that will be called
        # with the current template as single arg and must return the (possibly
        # empty) list or tuple of formats the current user may freeze. The
        # "freezing-related actions" that are granted by "freezeTemplate" are
        # the following. When no document is frozen yet for a given
        # template/format, the user may:
        # - freeze the document: pod will be called to produce a document from
        #   the current database content and will store it in the database.
        #   Subsequent user requests for this pod field will return the frozen
        #   doc instead of generating on-the-fly documents;
        # - upload a document: the user will be able to upload a document that
        #   will be stored in the database. Subsequent user requests for this
        #   pod field will return this doc instead of generating on-the-fly
        #   documents.
        # When a document is already frozen or uploaded for a given
        # template/format, the user may:
        # - unfreeze the document: the frozen or uploaded document will be
        #   deleted from the database and subsequent user requests for the pod
        #   field will again generate on-the-fly documents;
        # - re-freeze the document: the frozen or uploaded document will be
        #   deleted, a new document will be generated from the current database
        #   content and will be frozen as a replacement to the deleted one;
        # - upload a document: the frozen or uploaded document will be replaced
        #   by a new document uploaded by the current user.
        self.freezeTemplate = freezeTemplate
        # The context is a dict containing a specific pod context, or a method
        # that returns such a dict.
        self.context = context
        # A global styles mapping that would apply to the whole template
        self.stylesMapping = stylesMapping
        # What are the output formats when generating documents from this pod ?
        self.formats = formats
        if not formats:
            # Compute default ones
            if self.template[0].endswith('.ods'):
                self.formats = ('xls', 'ods')
            else:
                self.formats = ('pdf', 'doc', 'odt')
        Field.__init__(self, None, (0,1), default, show, page, group, layouts,
                       move, indexed, searchable, specificReadPermission,
                       specificWritePermission, width, height, None, colspan,
                       master, masterValue, focus, historized, mapping, label,
                       None, None, None, None, True)
        # Param "persist" is set to True but actually, persistence for a pod
        # field is determined by freezing.
        self.validable = False

    def getAllFormats(self, template):
        '''Gets all the outputy formats that are available for a given
           p_template.'''
        ext = os.path.splitext(template)[1]
        return self.allFormats[ext]

    def getTemplateName(self, obj, fileName):
        '''Gets the name of a template given its p_fileName.'''
        res = None
        if self.templateName:
            # Use the method specified in self.templateName.
            res = self.templateName(obj, fileName)
        # Else, deduce a nice name from p_fileName.
        if not res:
            name = os.path.splitext(os.path.basename(fileName))[0]
            res = gutils.produceNiceMessage(name)
        return res

    def getDownloadName(self, obj, template, format, queryRelated):
        '''Gets the name of the pod result as will be seen by the user that will
           download it.'''
        fileName = self.getTemplateName(obj, template)
        if not queryRelated:
            # This is a POD for a single object: personalize the file name with
            # the object title.
            fileName = '%s-%s' % (obj.title, fileName)
        return obj.tool.normalize(fileName) + '.' + format

    def getVisibleTemplates(self, obj):
        '''Returns, among self.template, the template(s) that can be shown.'''
        res = []
        if not self.showTemplate:
            # Show them all in any format.
            for template in self.template:
                res.append(Object(template=template,
                        formats=self.getAllFormats(template),
                        freezeFormats=self.getFreezeFormats(obj, template)))
        else:
            isManager = obj.user.has_role('Manager')
            for template in self.template:
                formats = self.showTemplate(obj, template)
                if not formats: continue
                formats = isManager and self.getAllFormats(template) or formats
                if isinstance(formats, basestring): formats = (formats,)
                res.append(Object(template=template, formats=formats,
                           freezeFormats=self.getFreezeFormats(obj, template)))
        return res

    def getValue(self, obj, template=None, format=None, result=None,
                 queryData=None, customParams=None, noSecurity=False):
        '''For a pod field, getting its value means computing a pod document or
           returning a frozen one. A pod field differs from other field types
           because there can be several ways to produce the field value (ie:
           self.template can hold various templates; output file format can be
           odt, pdf,.... We get those precisions about the way to produce the
           file, either from params, or from default values.
           * p_template is the specific template, among self.template, that must
             be used as base for generating the document;
           * p_format is the output format of the resulting document;
           * p_result, if given, must be the absolute path of the document that
             will be computed by pod. If not given, pod will produce a doc in
             the OS temp folder;
           * if the pod document is related to a query, the query parameters
             needed to re-trigger the query are given in p_queryData;
           * p_customParams may be specified. Every custom param must have form
             "name:value". Custom params override any other value available in
             the context, including values from the field-specific context.
        '''
        obj = obj.appy()
        template = template or self.template[0]
        format = format or 'odt'
        # Security check.
        if not noSecurity and not queryData:
            if self.showTemplate and not self.showTemplate(obj, template):
                raise Exception(self.UNAUTHORIZED)
        # Return the possibly frozen document (not applicable for query-related
        # pods).
        if not queryData:
            frozen = self.isFrozen(obj, template, format)
            if frozen:
                fileName = self.getDownloadName(obj, template, format, False)
                return FileInfo(frozen, inDb=False, uploadName=fileName)
        # We must call pod to compute a pod document from "template".
        tool = obj.tool
        diskFolder = tool.getDiskFolder()
        # Get the path to the pod template.
        templatePath = os.path.join(diskFolder, template)
        if not os.path.isfile(templatePath):
            raise Exception(self.TEMPLATE_NOT_FOUND % templatePath)
        # Get or compute the specific POD context
        specificContext = None
        if callable(self.context):
            specificContext = self.callMethod(obj, self.context)
        else:
            specificContext = self.context
        # Compute the name of the result file.
        if not result:
            result = '%s/%s_%f.%s' % (sutils.getOsTempFolder(),
                                      obj.uid, time.time(), format)
        # Define parameters to give to the appy.pod renderer
        podContext = {'tool': tool, 'user': obj.user, 'self': obj, 'field':self,
                      'now': obj.o.getProductConfig().DateTime(),
                      '_': obj.translate, 'projectFolder': diskFolder}
        # If the pod document is related to a query, re-trigger it and put the
        # result in the pod context.
        if queryData:
            # Retrieve query params
            cmd = ', '.join(tool.o.queryParamNames)
            cmd += " = queryData.split(';')"
            exec cmd
            # (re-)execute the query, but without any limit on the number of
            # results; return Appy objects.
            objs = tool.o.executeQuery(obj.o.portal_type, searchName=search,
                     sortBy=sortKey, sortOrder=sortOrder, filterKey=filterKey,
                     filterValue=filterValue, maxResults='NO_LIMIT')
            podContext['objects'] = [o.appy() for o in objs.objects]
        # Add the field-specific context if present.
        if specificContext:
            podContext.update(specificContext)
        # If a custom param comes from the request, add it to the context.
        if customParams:
            paramsDict = eval(customParams)
            podContext.update(paramsDict)
        # Define a potential global styles mapping
        if callable(self.stylesMapping):
            stylesMapping = self.callMethod(obj, self.stylesMapping)
        else:
            stylesMapping = self.stylesMapping
        rendererParams = {'template': templatePath, 'context': podContext,
                          'result': result, 'stylesMapping': stylesMapping,
                          'imageResolver': tool.o.getApp(),
                          'overwriteExisting': True}
        if tool.unoEnabledPython:
            rendererParams['pythonWithUnoPath'] = tool.unoEnabledPython
        if tool.openOfficePort:
            rendererParams['ooPort'] = tool.openOfficePort
        # Launch the renderer
        try:
            renderer = Renderer(**rendererParams)
            renderer.run()
        except PodError, pe:
            if not os.path.exists(result):
                # In some (most?) cases, when OO returns an error, the result is
                # nevertheless generated.
                obj.log(str(pe).strip(), type='error')
                return Pod.POD_ERROR
        # Give a friendly name for this file
        fileName = self.getDownloadName(obj, template, format, queryData)
        # Get a FileInfo instance to manipulate the file on the filesystem.
        return FileInfo(result, inDb=False, uploadName=fileName)

    def getFreezeName(self, template=None, format='pdf', sep='.'):
        '''Gets the name on disk on the frozen document corresponding to this
           pod field, p_template and p_format.'''
        template = template or self.template[0]
        templateName = os.path.splitext(template)[0].replace(os.sep, '_')
        return '%s_%s%s%s' % (self.name, templateName, sep, format)

    def isFrozen(self, obj, template=None, format='pdf'):
        '''Is there a frozen document for thid pod field, on p_obj, for
           p_template in p_format? If yes, it returns the absolute path to the
           frozen doc.'''
        template = template or self.template[0]
        dbFolder, folder = obj.o.getFsFolder()
        fileName = self.getFreezeName(template, format)
        res = os.path.join(dbFolder, folder, fileName)
        if os.path.exists(res): return res

    def freeze(self, obj, template=None, format='pdf', noSecurity=True,
               upload=None, freezeOdtOnError=True):
        '''Freezes, on p_obj, a document for this pod field, for p_template in
           p_format. If p_noSecurity is True, the security check, based on
           self.freezeTemplate, is bypassed. If no p_upload file is specified,
           we re-compute a pod document on-the-fly and we freeze this document.
           Else, we store the uploaded file.
           
           If p_freezeOdtOnError is True and format is not "odt" (has only sense
           when no p_upload file is specified), if the freezing fails we try to
           freeze the odt version, which is more robust because it does not
           require calling LibreOffice.'''
        # Security check.
        if not noSecurity and \
           (format not in self.getFreezeFormats(obj, template)):
            raise Exception(self.UNAUTHORIZED)
        # Compute the absolute path where to store the frozen document in the
        # database.
        dbFolder, folder = obj.o.getFsFolder(create=True)
        fileName = self.getFreezeName(template, format)
        result = os.path.join(dbFolder, folder, fileName)
        if os.path.exists(result):
            prefix = upload and 'Freeze (upload)' or 'Freeze'
            obj.log('%s: overwriting %s...' % (prefix, result))
        if not upload:
            # Generate the document.
            doc = self.getValue(obj, template=template, format=format,
                                result=result)
            if isinstance(doc, basestring):
                # An error occurred, the document was not generated.
                obj.log(self.FREEZE_ERROR % (format, self.name, doc),
                        type='error')
                if not freezeOdtOnError or (format == 'odt'):
                    raise Exception(self.FREEZE_FATAL_ERROR)
                obj.log('Trying to freeze the ODT version...')
                # Try to freeze the ODT version of the document, which does not
                # require to call LibreOffice: the risk of error is smaller.
                fileName = self.getFreezeName(template, 'odt')
                result = os.path.join(dbFolder, folder, fileName)
                if os.path.exists(result):
                    obj.log('Freeze: overwriting %s...' % result)
                doc = self.getValue(obj, template=template, format='odt',
                                    result=result)
                if isinstance(doc, basestring):
                    self.log(self.FREEZE_ERROR % ('odt', self.name, doc),
                             type='error')
                    raise Exception(self.FREEZE_FATAL_ERROR)
        else:
            # Store the uploaded file in the database.
            f = file(result, 'wb')
            doc = FileInfo(result, inDb=False)
            doc.replicateFile(upload, f)
            f.close()
        return doc

    def unfreeze(self, obj, template=None, format='pdf', noSecurity=True):
        '''Unfreezes, on p_obj, the document for this pod field, for p_template
           in p_format.'''
        # Security check.
        if not noSecurity and \
           (format not in self.getFreezeFormats(obj, template)):
            raise Exception(self.UNAUTHORIZED)
        # Compute the absolute path to the frozen doc.
        dbFolder, folder = obj.o.getFsFolder()
        fileName = self.getFreezeName(template, format)
        frozenName = os.path.join(dbFolder, folder, fileName)
        if os.path.exists(frozenName): os.remove(frozenName)

    def getFreezeFormats(self, obj, template=None):
        '''What are the formats into which the current user may freeze
           p_template?'''
        # One may have the right to edit the field to freeze anything in it.
        if not obj.o.mayEdit(self.writePermission): return ()
        # Manager can perform all freeze actions.
        template = template or self.template[0]
        isManager = obj.user.has_role('Manager')
        if isManager: return self.getAllFormats(template)
        # Others users can perform freeze actions depending on
        # self.freezeTemplate.
        if not self.freezeTemplate: return ()
        return self.freezeTemplate(obj, template)

    def getIconTitle(self, obj, format, frozen):
        '''Get the title of the format icon.'''
        res = obj.translate(format)
        if frozen:
            res += ' (%s)' % obj.translate('frozen')
        return res

    def onUiRequest(self, obj, rq):
        '''This method is called when an action tied to this pod field
           (generate, freeze, upload...) is triggered from the user
           interface.'''
        # What is the action to perform?
        action = rq.get('action', 'generate')
        # Security check.
        obj.o.mayView(self.readPermission, raiseError=True)
        # Perform the requested action.
        tool = obj.tool.o
        template = rq.get('template')
        format = rq.get('podFormat')
        if action == 'generate':
            # Generate a (or get a frozen) document.
            res = self.getValue(obj, template=template, format=format,
                                queryData=rq.get('queryData'),
                                customParams=rq.get('customParams'))
            if isinstance(res, basestring):
                # An error has occurred, and p_res contains the error message.
                obj.say(res)
                return tool.goto(rq.get('HTTP_REFERER'))
            # res contains a FileInfo instance.
            res.writeResponse(rq.RESPONSE)
            return
        # Performing any other action requires write access to p_obj.
        obj.o.mayEdit(self.writePermission, raiseError=True)
        msg = 'action_done'
        if action == 'freeze':
            # (Re-)freeze a document in the database.
            self.freeze(obj, template, format, noSecurity=False,
                        freezeOdtOnError=False)
        elif action == 'unfreeze':
            # Unfreeze a document in the database.
            self.unfreeze(obj, template, format, noSecurity=False)
        elif action == 'upload':
            # Ensure a file from the correct type has been uploaded.
            upload = rq.get('uploadedFile')
            if not upload or not upload.filename or \
               not upload.filename.endswith('.%s' % format):
                # A wrong file has been uploaded (or no file at all)
                msg = 'upload_invalid'
            else:
                # Store the uploaded file in the database.
                self.freeze(obj, template, format, noSecurity=False,
                            upload=upload)
        # Return a message to the user interface.
        obj.say(obj.translate(msg))
        return tool.goto(rq.get('HTTP_REFERER'))
# ------------------------------------------------------------------------------
