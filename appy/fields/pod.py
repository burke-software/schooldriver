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
class Mailing:
    '''Represents a mailing list as can be used by a pod field (see below).'''
    def __init__(self, name=None, logins=None, subject=None, body=None):
        # The mailing list name, as shown in the user interface
        self.name = name
        # The list of logins that will be used as recipients for sending
        # emails.
        self.logins = logins
        # The mail subject
        self.subject = subject
        # The mail body
        self.body = body

# ------------------------------------------------------------------------------
class Pod(Field):
    '''A pod is a field allowing to produce a (PDF, ODT, Word, RTF...) document
       from data contained in Appy class and linked objects or anything you
       want to put in it. It is the way gen uses pod.'''
    # Some right-aligned layouts, convenient for pod fields exporting query
    # results or multi-template pod fields.
    rLayouts = {'view': Table('fl!', css_class='podTable')} # "r"ight
    # "r"ight "m"ulti-template (where the global field label is not used
    rmLayouts = {'view': Table('f!', css_class='podTable')}
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
     <img var="iconSuffix=frozen and 'Frozen' or '';
               gc=field.getChecked and q(field.getChecked) or 'null'"
          src=":url(fmt + iconSuffix)" class="clickable"
          title=":field.getIconTitle(obj, fmt, frozen)"
          onclick=":'generatePod(%s,%s,%s,%s,%s,null,%s)' % (q(uid), q(name), \
                   q(info.template), q(fmt), q(ztool.getQueryInfo()), gc)"/>''')

    pxView = pxCell = Px('''
     <x var="uid=obj.uid"
        for="info in field.getVisibleTemplates(obj)"
        var2="mailings=field.getVisibleMailings(obj, info.template);
              lineBreak=((loop.info.nb + 1) % field.maxPerRow) == 0">
      <x for="fmt in info.formats"
         var2="freezeAllowed=(fmt in info.freezeFormats) and \
                             (field.show != 'result');
               hasMailings=mailings and (fmt in mailings);
               dropdownEnabled=freezeAllowed or hasMailings;
               frozen=field.isFrozen(obj, info.template, fmt)">
       <!-- A clickable icon if no freeze action is allowed and no mailing is
            available for this format -->
       <x if="not dropdownEnabled">:field.pxIcon</x>
       <!-- A clickable icon and a dropdown menu else. -->
       <span if="dropdownEnabled" class="dropdownMenu"
             var2="dropdownId='%s_%s' % (uid, \
                              field.getFreezeName(info.template, fmt, sep='_'))"
             onmouseover=":'toggleDropdown(%s)' % q(dropdownId)"
             onmouseout=":'toggleDropdown(%s,%s)' % (q(dropdownId), q('none'))">
        <x>:field.pxIcon</x>
        <!-- The dropdown menu containing freeze actions -->
        <table id=":dropdownId" class="dropdown" width="100px">
         <!-- Unfreeze -->
         <tr if="freezeAllowed and frozen" valign="top">
          <td width="85px">
           <a onclick=":'freezePod(%s,%s,%s,%s,%s)' % (q(uid), q(name), \
                        q(info.template), q(fmt), q('unfreeze'))"
              class="smaller">:_('unfreezeField')</a>
          </td>
          <td width="15px"><img src=":url('unfreeze')"/></td>
         </tr>
         <!-- (Re-)freeze -->
         <tr if="freezeAllowed" valign="top">
          <td width="85px">
           <a onclick=":'freezePod(%s,%s,%s,%s,%s)' % (q(uid), q(name), \
                        q(info.template), q(fmt), q('freeze'))"
              class="smaller">:_('freezeField')</a>
          </td>
          <td width="15px"><img src=":url('freeze')"/></td>
         </tr>
         <!-- (Re-)upload -->
         <tr if="freezeAllowed" valign="top">
          <td width="85px">
           <a onclick=":'uploadPod(%s,%s,%s,%s)' % (q(uid), q(name), \
                        q(info.template), q(fmt))"
              class="smaller">:_('uploadField')</a>
          </td>
          <td width="15px"><img src=":url('upload')"/></td>
         </tr>
         <!-- Mailing lists -->
         <x if="hasMailings" var2="sendLabel=_('email_send')">
          <tr for="mailing in mailings[fmt]" valign="top"
              var2="mailingName=field.getMailingName(obj, mailing)">
           <td colspan="2">
            <a var="js='generatePod(%s,%s,%s,%s,%s,null,null,%s)' % \
                       (q(uid), q(name), q(info.template), q(fmt), \
                        q(ztool.getQueryInfo()), q(mailing))"
               onclick=":'askConfirm(%s,%s)' % (q('script'), q(js, False))"
               title=":sendLabel">
             <img src=":url('email')" align="left" style="margin-right: 2px"/>
             <x>:mailingName</x></a>
            </td>
          </tr>
         </x>
        </table>
       </span>
      </x>
      <!-- Show the specific template name only if there is more than one
           template. For a single template, the field label already does the
           job. -->
      <span if="len(field.template) &gt; 1"
            class=":(not loop.info.last and not lineBreak) and 'pod smaller' \
                 or 'smaller'">:field.getTemplateName(obj, info.template)</span>
      <br if="lineBreak"/>
     </x>''')

    pxEdit = pxSearch = ''

    def __init__(self, validator=None, default=None, show=('view', 'result'),
                 page='main', group=None, layouts=None, move=0, indexed=False,
                 searchable=False, specificReadPermission=False,
                 specificWritePermission=False, width=None, height=None,
                 maxChars=None, colspan=1, master=None, masterValue=None,
                 focus=False, historized=False, mapping=None, label=None,
                 template=None, templateName=None, showTemplate=None,
                 freezeTemplate=None, maxPerRow=5, context=None,
                 stylesMapping={}, formats=None, getChecked=None, mailing=None,
                 mailingName=None, showMailing=None, mailingInfo=None):
        # Param "template" stores the path to the pod template(s). If there is
        # a single template, a string is expected. Else, a list or tuple of
        # strings is expected. Every such path must be relative to your
        # application. A pod template name Test.odt that is stored at the root
        # of your app will be referred as "Test.odt" in self.template. If it is
        # stored within sub-folder "pod", it will be referred as "pod/Test.odt".
        if not template: raise Exception(Pod.NO_TEMPLATE)
        if isinstance(template, basestring):
            self.template = [template]
        elif isinstance(template, tuple):
            self.template = list(template)
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
        # If p_template contains more than 1 template, "maxPerRow" tells how
        # much templates must appear side by side.
        self.maxPerRow = maxPerRow
        # The context is a dict containing a specific pod context, or a method
        # that returns such a dict.
        self.context = context
        # A global styles mapping that would apply to the whole template
        self.stylesMapping = stylesMapping
        # What are the output formats when generating documents from this pod ?
        self.formats = formats
        if not formats: # Compute default ones
            self.formats = self.getAllFormats(self.template[0])
        # Parameter "getChecked" can specify the name of a Ref field belonging
        # to the same gen class. If it is the case, the context of the pod
        # template will contain an additional object, name "_checked", and
        # "_checked.<name of the Ref field>" will contain the list of the
        # objects linked via the Ref field that are currently selected in the
        # user interface.
        self.getChecked = getChecked
        # Mailing lists can be defined for this pod field. For every visible
        # mailing list, a menu item will be available in the user interface and
        # will allow to send the pod result as attachment to the mailing list
        # recipients. Attribute p_mailing stores a mailing list's id
        # (as a string) or a list of ids.
        self.mailing = mailing
        if isinstance(mailing, basestring):
            self.mailing = [mailing]
        elif isinstance(mailing, tuple):
            self.mailing = list(mailing)
        # "mailingName" returns the name of the mailing as will be shown in the
        # user interface. It must be a method accepting the mailing list id
        # (from self.mailing) as single arg and returning the mailing list's
        # name.
        self.mailingName = mailingName
        # "showMailing" below determines when the mailing list(s) must be shown.
        # It may store a method accepting a mailing list's id (among
        # self.mailing) and a template (among self.template) and returning the
        # list or tuple of formats for which the pod result can be sent to the
        # mailing list. If no such method is defined, the mailing list will be
        # available for all visible templates and formats.
        self.showMailing = showMailing
        # When it it time to send an email, "mailingInfo" gives all the
        # necessary information for this email: recipients, subject, body. It
        # must be a method whose single arg is the mailing id (from
        # self.mailing) and that returns an instance of class Mailing (above).
        self.mailingInfo = mailingInfo
        Field.__init__(self, None, (0,1), default, show, page, group, layouts,
                       move, indexed, searchable, specificReadPermission,
                       specificWritePermission, width, height, None, colspan,
                       master, masterValue, focus, historized, mapping, label,
                       None, None, None, None, True)
        # Param "persist" is set to True but actually, persistence for a pod
        # field is determined by freezing.
        self.validable = False

    def getExtension(self, template):
        '''Gets a p_template's extension (".odt" or ".ods"). Because a template
           can simply be a pointer to another template (ie, "Item.odt.variant"),
           the logic for getting the extension is a bit more tricky.'''
        elems = os.path.splitext(template)
        if elems[1] in Pod.allFormats: return elems[1]
        # p_template must be a pointer to another template and has one more
        # extension.
        return os.path.splitext(elems[0])[1]

    def getAllFormats(self, template):
        '''Gets all the output formats that are available for a given
           p_template.'''
        return Pod.allFormats[self.getExtension(template)]

    def setTemplateFolder(self, folder):
        '''This methods adds a prefix to every template name in
           self.template. This can be useful if a plug-in module needs to
           replace an application template by its own templates. Here is an
           example: imagine a base application has a pod field with:
           
           self.templates = ["Item.odt", "Decision.odt"]
           
           The plug-in module, named "PlugInApp", wants to replace it with its
           own templates Item.odt, Decision.odt and Other.odt, stored in its
           sub-folder "pod". Suppose the base pod field is in <podField>. The
           plug-in will write:
           
           <podField>.templates = ["Item.odt", "Decision.odt", "Other.odt"]
           <podField>.setTemplateFolder('../PlugInApp/pod')
           
           The following code is equivalent, will work, but is precisely the
           kind of things we want to avoid.

           <podField>.templates = ["../PlugInApp/pod/Item.odt",
                                   "../PlugInApp/pod/Decision.odt",
                                   "../PlugInApp/pod/Other.odt"]
        '''
        for i in range(len(self.template)):
            self.template[i] = os.path.join(folder, self.template[i])

    def getTemplateName(self, obj, fileName):
        '''Gets the name of a template given its p_fileName.'''
        res = None
        if self.templateName:
            # Use the method specified in self.templateName
            res = self.templateName(obj, fileName)
        # Else, deduce a nice name from p_fileName
        if not res:
            name = os.path.splitext(os.path.basename(fileName))[0]
            res = gutils.produceNiceMessage(name)
        return res

    def getTemplatePath(self, diskFolder, template):
        '''Return the absolute path to some pod p_template, by prefixing it with
           the application path. p_template can be a pointer to another
           template.'''
        res = sutils.resolvePath(os.path.join(diskFolder, template))
        if not os.path.isfile(res):
            raise Exception(self.TEMPLATE_NOT_FOUND % templatePath)
        # Unwrap the path if the file is simply a pointer to another one.
        elems = os.path.splitext(res)
        if elems[1] not in Pod.allFormats:
            res = self.getTemplatePath(diskFolder, elems[0])
        return res

    def getDownloadName(self, obj, template, format, queryRelated):
        '''Gets the name of the pod result as will be seen by the user that will
           download it. Ensure the returned name is not too long for the OS that
           will store the downloaded file with this name.'''
        norm = obj.tool.normalize
        fileName = norm(self.getTemplateName(obj, template))[:100]
        if not queryRelated:
            # This is a POD for a single object: personalize the file name with
            # the object title.
            fileName = '%s-%s' % (norm(obj.title)[:140], fileName)
        return fileName + '.' + format

    def getVisibleTemplates(self, obj):
        '''Returns, among self.template, the template(s) that can be shown.'''
        res = []
        if not self.showTemplate:
            # Show them all in the formats spoecified in self.formats.
            for template in self.template:
                res.append(Object(template=template, formats=self.formats,
                            freezeFormats=self.getFreezeFormats(obj, template)))
        else:
            isManager = obj.user.has_role('Manager')
            for template in self.template:
                formats = self.showTemplate(obj, template)
                if not formats: continue
                if isManager: formats = self.getAllFormats(template)
                elif isinstance(formats, bool): formats = self.formats
                elif isinstance(formats, basestring): formats = (formats,)
                res.append(Object(template=template, formats=formats,
                           freezeFormats=self.getFreezeFormats(obj, template)))
        return res

    def getVisibleMailings(self, obj, template):
        '''Gets, among self.mailing, the mailing(s) that can be shown for
           p_template, as a dict ~{s_format:[s_id]}~.'''
        if not self.mailing: return
        res = {}
        for mailing in self.mailing:
            # Is this mailing visible ? In which format(s) ?
            if not self.showMailing:
                # By default, the mailing is available in any format
                formats = True
            else:
                formats = self.showMailing(obj, mailing, template)
            if not formats: continue
            if isinstance(formats, bool): formats = self.formats
            elif isinstance(formats, basestring): formats = (formats,)
            # Add this mailing to the result
            for fmt in formats:
                if fmt in res: res[fmt].append(mailing)
                else: res[fmt] = [mailing]
        return res

    def getMailingName(self, obj, mailing):
        '''Gets the name of a particular p_mailing.'''
        res = None
        if self.mailingName:
            # Use the method specified in self.mailingName
            res = self.mailingName(obj, mailing)
        if not res:
            # Deduce a nice name from p_mailing
            res = gutils.produceNiceMessage(mailing)
        return res

    def getMailingInfo(self, obj, template, mailing):
        '''Gets the necessary information for sending an email to
           p_mailing list.'''
        res = self.mailingInfo(obj, mailing)
        subject = res.subject
        if not subject:
            # Give a predefined subject
            mapping = {'site': obj.tool.o.getSiteUrl(),
                       'title':  obj.o.getShownValue('title'),
                       'template': self.getTemplateName(obj, template)}
            subject = obj.translate('podmail_subject', mapping=mapping)
        body = res.body
        if not body:
            # Give a predefined body
            mapping = {'site': obj.tool.o.getSiteUrl()}
            body = obj.translate('podmail_body', mapping=mapping)
        return res.logins, subject, body

    def sendMailing(self, obj, template, mailing, attachment):
        '''Sends the emails for m_mailing.'''
        logins, subject, body = self.getMailingInfo(obj, template, mailing)
        if not logins:
            obj.log('mailing %s contains no recipient.' % mailing)
            return 'action_ko'
        tool = obj.tool
        # Collect logins corresponding to inexistent users and recipients
        missing = []
        recipients = []
        for login in logins:
            user = tool.search1('User', noSecurity=True, login=login)
            if not user:
                missing.append(login)
                continue
            else:
                recipient = user.getMailRecipient()
                if not recipient:
                    missing.append(login)
                else:
                    recipients.append(recipient)
        if missing:
            obj.log('mailing %s: inexistent user or no email for %s.' % \
                    (mailing, str(missing)))
        if not recipients:
            obj.log('mailing %s contains no recipient (after removing wrong ' \
                    'entries, see above).' % mailing)
            msg = 'action_ko'
        else:
            tool.sendMail(recipients, subject, body, [attachment])
            msg = 'action_done'
        return msg

    def getValue(self, obj, template=None, format=None, result=None,
                 queryData=None, customContext=None, noSecurity=False):
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
           * dict p_customContext may be specified and will override any other
             value available in the context, including values from the
             field-specific context.
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
        templatePath = self.getTemplatePath(diskFolder, template)
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
                      '_': obj.translate, 'projectFolder': diskFolder,
                      'template': template, 'request': tool.request}
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
            podContext['queryData'] = queryData.split(';')
        # Add the field-specific and custom contexts if present.
        if specificContext: podContext.update(specificContext)
        if customContext: podContext.update(customContext)
        # Variable "_checked" can be expected by a template but absent (ie,
        # when generating frozen documents).
        if '_checked' not in podContext: podContext['_checked'] = Object()
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
        template = os.path.basename(template)
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
                obj.log('freezing the ODT version...')
                # Freeze the ODT version of the document, which does not require
                # to call LibreOffice: the risk of error is smaller.
                fileName = self.getFreezeName(template, 'odt')
                result = os.path.join(dbFolder, folder, fileName)
                if os.path.exists(result):
                    obj.log('freeze: overwriting %s...' % result)
                doc = self.getValue(obj, template=template, format='odt',
                                    result=result)
                if isinstance(doc, basestring):
                    self.log(self.FREEZE_ERROR % ('odt', self.name, doc),
                             type='error')
                    raise Exception(self.FREEZE_FATAL_ERROR)
                obj.log('freezed at %s.' % result)
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
        if os.path.exists(frozenName):
            os.remove(frozenName)
            obj.log('removed (unfrozen) %s.' % frozenName)

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

    def getCustomContext(self, obj, rq):
        '''Before calling pod to compute a result, if specific elements must be
           added to the context, compute it here. This request-dependent method
           is not called when computing a pod field for freezing it into the
           database.'''
        res = {}
        # Get potential custom params from the request. Custom params must be
        # coded as a string containing a valid Python dict.
        customParams = rq.get('customParams')
        if customParams:
            paramsDict = eval(customParams)
            res.update(paramsDict)
        # Compute the selected linked objects if self.getChecked is specified
        # and if the user can read this Ref field.
        if self.getChecked and \
           obj.allows(obj.getField(self.getChecked).readPermission):
            # Get the UIDs specified in the request
            reqUids = rq['checkedUids'] and rq['checkedUids'].split(',') or []
            unchecked = rq['checkedSem'] == 'unchecked'
            objects = []
            tool = obj.tool
            for uid in getattr(obj.o.aq_base, self.getChecked, ()):
                if unchecked: condition = uid not in reqUids
                else:         condition = uid in reqUids
                if condition:
                    tied = tool.getObject(uid)
                    if tied.allows('read'): objects.append(tied)
            res['_checked'] = Object()
            setattr(res['_checked'], self.getChecked, objects)
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
                                customContext=self.getCustomContext(obj, rq))
            if isinstance(res, basestring):
                # An error has occurred, and p_res contains the error message.
                obj.say(res)
                return tool.goto(rq.get('HTTP_REFERER'))
            # res contains a FileInfo instance.
            # Must we return the res to the ui or send a mail with the res as
            # attachment?
            mailing = rq.get('mailing')
            if not mailing:
                # With disposition=inline, Google Chrome and IE may launch a PDF
                # viewer that triggers one or many additional crashing HTTP GET
                # requests.
                res.writeResponse(rq.RESPONSE, disposition='attachment')
                return
            else:
                # Send the email(s).
                msg = self.sendMailing(obj, template, mailing, res)
                obj.say(obj.translate(msg))
                return tool.goto(rq.get('HTTP_REFERER'))
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
