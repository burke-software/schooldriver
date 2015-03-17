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
    WRONG_METHOD = 'Wrong value "%s". Param "method" must contain a method ' \
                   'or a PX.'
    pxView = pxCell = pxEdit = Px('''<x if="field.plainText">:value</x>
      <x if="not field.plainText">::value</x>''')

    pxSearch = Px('''
     <input type="text" name=":'%s*string' % widgetName"
            maxlength=":field.maxChars" size=":field.width"
            value=":field.sdefault"/>''')

    def __init__(self, validator=None, multiplicity=(0,1), default=None,
                 show=('view', 'result'), page='main', group=None,
                 layouts=None, move=0, indexed=False, searchable=False,
                 specificReadPermission=False, specificWritePermission=False,
                 width=None, height=None, maxChars=None, colspan=1, method=None,
                 formatMethod=None, plainText=False, master=None,
                 masterValue=None, focus=False, historized=False, mapping=None,
                 label=None, sdefault='', scolspan=1, swidth=None, sheight=None,
                 context=None):
        # The Python method used for computing the field value, or a PX.
        self.method = method
        # A specific method for producing the formatted value of this field.
        # This way, if, for example, the value is a DateTime instance which is
        # indexed, you can specify in m_formatMethod the way to format it in
        # the user interface while m_method computes the value stored in the
        # catalog.
        self.formatMethod = formatMethod
        if isinstance(self.method, basestring):
            # A legacy macro identifier. Raise an exception
            raise Exception(self.WRONG_METHOD % self.method)
        # Does field computation produce plain text or XHTML?
        self.plainText = plainText
        if isinstance(method, Px):
            # When field computation is done with a PX, the result is XHTML.
            self.plainText = False
        # If method is a PX, its context can be given in p_context.
        self.context = context
        Field.__init__(self, None, multiplicity, default, show, page, group,
                       layouts, move, indexed, searchable,
                       specificReadPermission, specificWritePermission, width,
                       height, None, colspan, master, masterValue, focus,
                       historized, mapping, label, sdefault, scolspan, swidth,
                       sheight, False)
        self.validable = False

    def getValue(self, obj):
        '''Computes the value instead of getting it in the database.'''
        if not self.method: return
        if isinstance(self.method, Px):
            obj = obj.appy()
            tool = obj.tool
            req = obj.request
            # Get the context of the currently executed PX if present
            try:
                ctx = req.pxContext
            except AttributeError:
                # Create some standard context
                ctx = {'obj': obj, 'zobj': obj.o, 'field': self,
                       'req': req, 'tool': tool, 'ztool': tool.o,
                       '_': tool.translate, 'url': tool.o.getIncludeUrl}
            if self.context: ctx.update(self.context)
            return self.method(ctx)
        else:
            # self.method is a method that will return the field value
            return self.callMethod(obj, self.method, cache=False)

    def getFormattedValue(self, obj, value, showChanges=False, language=None):
        if self.formatMethod:
            res = self.formatMethod(obj, value)
        else:
            res = value
        if not isinstance(res, basestring): res = str(res)
        return res
# ------------------------------------------------------------------------------
