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
import time, os, os.path, StringIO
from appy.fields import Field
from appy.px import Px
from file import File
from appy.gen.layout import Table
from appy.pod import PodError
from appy.pod.renderer import Renderer
from appy.shared import utils as sutils

# ------------------------------------------------------------------------------
class Pod(Field):
    '''A pod is a field allowing to produce a (PDF, ODT, Word, RTF...) document
       from data contained in Appy class and linked objects or anything you
       want to put in it. It is the way gen uses pod.'''
    # Layout for rendering a POD field for exporting query results.
    rLayouts = {'view': Table('fl', width=None)}
    POD_ERROR = 'An error occurred while generating the document. Please ' \
                'contact the system administrator.'
    DELETE_TEMP_DOC_ERROR = 'A temporary document could not be removed. %s.'

    pxView = pxCell = Px('''<x>
     <!-- Ask action -->
     <x if="field.askAction"
        var2="doLabel='%s_askaction' % field.labelId;
              chekboxId='%s_%s_cb' % (zobj.UID(), name)">
      <input type="checkbox" name=":doLabel" id=":chekboxId"/>
      <label lfor=":chekboxId" class="discreet">:_(doLabel)"></label>
     </x>
     <img for="fmt in field.getToolInfo(obj)[1]" src=":url(fmt)"
          onclick=":'generatePodDocument(%s, %s, %s, %s)' % \
            (q(zobj.UID()), q(name), q(fmt), q(ztool.getQueryInfo()))"
          title=":fmt.capitalize()" class="clickable"/>
    </x>''')

    pxEdit = pxSearch = ''

    def __init__(self, validator=None, default=None, show=('view', 'result'),
                 page='main', group=None, layouts=None, move=0, indexed=False,
                 searchable=False, specificReadPermission=False,
                 specificWritePermission=False, width=None, height=None,
                 maxChars=None, colspan=1, master=None, masterValue=None,
                 focus=False, historized=False, mapping=None, label=None,
                 template=None, context=None, action=None, askAction=False,
                 stylesMapping={}, freezeFormat='pdf'):
        # The following param stores the path to a POD template
        self.template = template
        # The context is a dict containing a specific pod context, or a method
        # that returns such a dict.
        self.context = context
        # Next one is a method that will be triggered after the document has
        # been generated.
        self.action = action
        # If askAction is True, the action will be triggered only if the user
        # checks a checkbox, which, by default, will be unchecked.
        self.askAction = askAction
        # A global styles mapping that would apply to the whole template
        self.stylesMapping = stylesMapping
        # Freeze format is by PDF by default
        self.freezeFormat = freezeFormat
        Field.__init__(self, None, (0,1), default, show, page, group, layouts,
                       move, indexed, searchable, specificReadPermission,
                       specificWritePermission, width, height, None, colspan,
                       master, masterValue, focus, historized, False, mapping,
                       label, None, None, None, None)
        self.validable = False

    def isFrozen(self, obj):
        '''Is there a frozen document for p_self on p_obj?'''
        value = getattr(obj.o.aq_base, self.name, None)
        return isinstance(value, obj.o.getProductConfig().File)

    def getToolInfo(self, obj):
        '''Gets information related to this field (p_self) that is available in
           the tool: the POD template and the available output formats. If this
           field is frozen, available output formats are not available anymore:
           only the format of the frozen doc is returned.'''
        tool = obj.tool
        appyClass = tool.o.getAppyClass(obj.o.meta_type)
        # Get the output format(s)
        if self.isFrozen(obj):
            # The only available format is the one from the frozen document
            fileName = getattr(obj.o.aq_base, self.name).filename
            formats = (os.path.splitext(fileName)[1][1:],)
        else:
            # Available formats are those which are selected in the tool.
            name = tool.getAttributeName('formats', appyClass, self.name)
            formats = getattr(tool, name)
        # Get the POD template
        name = tool.getAttributeName('podTemplate', appyClass, self.name)
        template = getattr(tool, name)
        return (template, formats)

    def getValue(self, obj):
        '''Gets, on_obj, the value conforming to self's type definition. For a
           Pod field, if a file is stored in the field, it means that the
           field has been frozen. Else, it means that the value must be
           retrieved by calling pod to compute the result.'''
        rq = getattr(obj, 'REQUEST', None)
        res = getattr(obj.aq_base, self.name, None)
        if res and res.size:
            # Return the frozen file.
            return sutils.FileWrapper(res)
        # If we are here, it means that we must call pod to compute the file.
        # A Pod field differs from other field types because there can be
        # several ways to produce the field value (ie: output file format can be
        # odt, pdf,...; self.action can be executed or not...). We get those
        # precisions about the way to produce the file from the request object
        # and from the tool. If we don't find the request object (or if it does
        # not exist, ie, when Zope runs in test mode), we use default values.
        obj = obj.appy()
        tool = obj.tool
        # Get POD template and available formats from the tool.
        template, availFormats = self.getToolInfo(obj)
        # Get the output format
        defaultFormat = 'pdf'
        if defaultFormat not in availFormats: defaultFormat = availFormats[0]
        outputFormat = getattr(rq, 'podFormat', defaultFormat)
        # Get or compute the specific POD context
        specificContext = None
        if callable(self.context):
            specificContext = self.callMethod(obj, self.context)
        else:
            specificContext = self.context
        # Temporary file where to generate the result
        tempFileName = '%s/%s_%f.%s' % (
            sutils.getOsTempFolder(), obj.uid, time.time(), outputFormat)
        # Define parameters to give to the appy.pod renderer
        podContext = {'tool': tool, 'user': obj.user, 'self': obj, 'field':self,
                      'now': obj.o.getProductConfig().DateTime(),
                      '_': obj.translate, 'projectFolder': tool.getDiskFolder()}
        # If the POD document is related to a query, get it from the request,
        # execute it and put the result in the context.
        isQueryRelated = rq.get('queryData', None)
        if isQueryRelated:
            # Retrieve query params from the request
            cmd = ', '.join(tool.o.queryParamNames)
            cmd += " = rq['queryData'].split(';')"
            exec cmd
            # (re-)execute the query, but without any limit on the number of
            # results; return Appy objects.
            objs = tool.o.executeQuery(obj.o.portal_type, searchName=search,
                     sortBy=sortKey, sortOrder=sortOrder, filterKey=filterKey,
                     filterValue=filterValue, maxResults='NO_LIMIT')
            podContext['objects'] = [o.appy() for o in objs['objects']]
        # Add the field-specific context if present.
        if specificContext:
            podContext.update(specificContext)
        # If a custom param comes from the request, add it to the context. A
        # custom param must have format "name:value". Custom params override any
        # other value in the request, including values from the field-specific
        # context.
        customParams = rq.get('customParams', None)
        if customParams:
            paramsDict = eval(customParams)
            podContext.update(paramsDict)
        # Define a potential global styles mapping
        if callable(self.stylesMapping):
            stylesMapping = self.callMethod(obj, self.stylesMapping)
        else:
            stylesMapping = self.stylesMapping
        rendererParams = {'template': StringIO.StringIO(template.content),
                          'context': podContext, 'result': tempFileName,
                          'stylesMapping': stylesMapping,
                          'imageResolver': tool.o.getApp()}
        if tool.unoEnabledPython:
            rendererParams['pythonWithUnoPath'] = tool.unoEnabledPython
        if tool.openOfficePort:
            rendererParams['ooPort'] = tool.openOfficePort
        # Launch the renderer
        try:
            renderer = Renderer(**rendererParams)
            renderer.run()
        except PodError, pe:
            if not os.path.exists(tempFileName):
                # In some (most?) cases, when OO returns an error, the result is
                # nevertheless generated.
                obj.log(str(pe), type='error')
                return Pod.POD_ERROR
        # Give a friendly name for this file
        fileName = obj.translate(self.labelId)
        if not isQueryRelated:
            # This is a POD for a single object: personalize the file name with
            # the object title.
            fileName = '%s-%s' % (obj.title, fileName)
        fileName = tool.normalize(fileName) + '.' + outputFormat
        # Get a FileWrapper instance from the temp file on the filesystem
        res = File.getFileObject(tempFileName, fileName)
        # Execute the related action if relevant
        doAction = getattr(rq, 'askAction', False) in ('True', True)
        if doAction and self.action: self.action(obj, podContext)
        # Returns the doc and removes the temp file
        try:
            os.remove(tempFileName)
        except OSError, oe:
            obj.log(Pod.DELETE_TEMP_DOC_ERROR % str(oe), type='warning')
        except IOError, ie:
            obj.log(Pod.DELETE_TEMP_DOC_ERROR % str(ie), type='warning')
        return res

    def store(self, obj, value):
        '''Stores (=freezes) a document (in p_value) in the field.'''
        if isinstance(value, sutils.FileWrapper):
            value = value._zopeFile
        setattr(obj, self.name, value)
# ------------------------------------------------------------------------------
