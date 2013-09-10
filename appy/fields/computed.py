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
from appy.fields import Field
from appy.px import  Px

# ------------------------------------------------------------------------------
class Computed(Field):

    # Ajax-called view content of a non sync Computed field.
    pxViewContent = Px('''
     <x var="name=req['fieldName'];
             field=zobj.getAppyType(name);
             value=zobj.getFieldValue(name);
             sync=True">:field.pxView</x>''')

    pxView = pxCell = pxEdit = Px('''<x>
     <x if="sync">
      <x if="field.plainText">:value</x><x if="not field.plainText">::value></x>
     </x>
     <div if="not sync">
          var2="ajaxHookId=zobj.UID() + name" id="ajaxHookId">
      <script type="text/javascript">:'askComputedField(%s, %s, %s)' % \
        (q(ajaxHookId), q(zobj.absolute_url()), q(name))">
      </script>
     </div>
    </x>''')

    pxSearch = Px('''<x>
     <label lfor=":name">:field.labelId</label><br/>&nbsp;&nbsp;
     <input type="text" name=":'%s*string' % name" maxlength=":field.maxChars"
            size=":field.width" value=":field.sdefault"/>
    </x>''')

    def __init__(self, validator=None, multiplicity=(0,1), default=None,
                 show='view', page='main', group=None, layouts=None, move=0,
                 indexed=False, searchable=False, specificReadPermission=False,
                 specificWritePermission=False, width=None, height=None,
                 maxChars=None, colspan=1, method=None, plainText=True,
                 master=None, masterValue=None, focus=False, historized=False,
                 sync=True, mapping=None, label=None, sdefault='', scolspan=1,
                 swidth=None, sheight=None, context={}):
        # The Python method used for computing the field value
        self.method = method
        # Does field computation produce plain text or XHTML?
        self.plainText = plainText
        if isinstance(method, basestring):
            # When field computation is done with a macro, we know the result
            # will be HTML.
            self.plainText = False
        # The context is a dict (or method returning a dict) that will be given
        # to the macro specified in self.method. If the dict contains key
        # "someKey", it will be available to the macro as "options/someKey".
        self.context = context
        Field.__init__(self, None, multiplicity, default, show, page, group,
                       layouts, move, indexed, searchable,
                       specificReadPermission, specificWritePermission, width,
                       height, None, colspan, master, masterValue, focus,
                       historized, sync, mapping, label, sdefault, scolspan,
                       swidth, sheight)
        self.validable = False

    def callMacro(self, obj, macroPath):
        '''Returns the macro corresponding to p_macroPath. The base folder
           where we search is "ui".'''
        # Get the special page in Appy that allows to call a macro
        macroPage = obj.ui.callMacro
        # Get, from p_macroPath, the page where the macro lies, and the macro
        # name.
        names = self.method.split('/')
        # Get the page where the macro lies
        page = obj.ui
        for name in names[:-1]:
            page = getattr(page, name)
        macroName = names[-1]
        # Compute the macro context.
        ctx = {'contextObj':obj, 'page':page, 'macroName':macroName}
        if callable(self.context):
            ctx.update(self.context(obj.appy()))
        else:
            ctx.update(self.context)
        return macroPage(obj, **ctx)

    def getValue(self, obj):
        '''Computes the value instead of getting it in the database.'''
        if not self.method: return
        if isinstance(self.method, basestring):
            # self.method is a path to a macro that will produce the field value
            return self.callMacro(obj, self.method)
        else:
            # self.method is a method that will return the field value
            return self.callMethod(obj, self.method, cache=False)

    def getFormattedValue(self, obj, value, showChanges=False):
        if not isinstance(value, basestring): return str(value)
        return value
# ------------------------------------------------------------------------------
