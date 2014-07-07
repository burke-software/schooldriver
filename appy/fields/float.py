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
from appy.px import Px
from appy.shared import utils as sutils

# ------------------------------------------------------------------------------
class Float(Field):
    allowedDecimalSeps = (',', '.')
    allowedThousandsSeps = (' ', '')

    pxView = pxCell = Px('''
     <x><x>:value</x>
      <input type="hidden" if="masterCss" class=":masterCss" value=":value"
             name=":name" id=":name"/>
     </x>''')

    pxEdit = Px('''
     <input id=":name" name=":name" size=":field.width"
            maxlength=":field.maxChars"
            value=":inRequest and requestValue or value" type="text"/>''')

    pxSearch = Px('''
     <!-- From -->
     <x var="fromName='%s*float' % widgetName">
      <label lfor=":fromName">:_('search_from')</label>
      <input type="text" name=":fromName" maxlength=":field.maxChars"
             value=":field.sdefault[0]" size=":field.swidth"/>
     </x>
     <!-- To -->
     <x var="toName='%s_to' % name">
      <label lfor=":toName">:_('search_to')</label>
      <input type="text" name=":toName" maxlength=":field.maxChars"
             value=":field.sdefault[1]" size="field.swidth"/>
     </x><br/>''')

    def __init__(self, validator=None, multiplicity=(0,1), default=None,
                 show=True, page='main', group=None, layouts=None, move=0,
                 indexed=False, searchable=False, specificReadPermission=False,
                 specificWritePermission=False, width=5, height=None,
                 maxChars=13, colspan=1, master=None, masterValue=None,
                 focus=False, historized=False, mapping=None, label=None,
                 sdefault=('',''), scolspan=1, swidth=None, sheight=None,
                 persist=True, precision=None, sep=(',', '.'), tsep=' '):
        # The precision is the number of decimal digits. This number is used
        # for rendering the float, but the internal float representation is not
        # rounded.
        self.precision = precision
        # The decimal separator can be a tuple if several are allowed, ie
        # ('.', ',')
        if type(sep) not in sutils.sequenceTypes:
            self.sep = (sep,)
        else:
            self.sep = sep
        # Check that the separator(s) are among allowed decimal separators
        for sep in self.sep:
            if sep not in Float.allowedDecimalSeps:
                raise Exception('Char "%s" is not allowed as decimal ' \
                                'separator.' % sep)
        self.tsep = tsep
        Field.__init__(self, validator, multiplicity, default, show, page,
                       group, layouts, move, indexed, False,
                       specificReadPermission, specificWritePermission, width,
                       height, maxChars, colspan, master, masterValue, focus,
                       historized, mapping, label, sdefault, scolspan, swidth,
                       sheight, persist)
        self.pythonType = float

    def getFormattedValue(self, obj, value, showChanges=False):
        return sutils.formatNumber(value, sep=self.sep[0],
                                   precision=self.precision, tsep=self.tsep)

    def validateValue(self, obj, value):
        # Replace used separator with the Python separator '.'
        for sep in self.sep: value = value.replace(sep, '.')
        value = value.replace(self.tsep, '')
        try:
            value = self.pythonType(value)
        except ValueError:
            return obj.translate('bad_%s' % self.pythonType.__name__)

    def getStorableValue(self, value):
        if not self.isEmptyValue(value):
            for sep in self.sep: value = value.replace(sep, '.')
            value = value.replace(self.tsep, '')
            return self.pythonType(value)
# ------------------------------------------------------------------------------
