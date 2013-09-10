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
from appy.gen.layout import Table

# ------------------------------------------------------------------------------
class Boolean(Field):
    '''Field for storing boolean values.'''

    pxView = pxCell = Px('''
     <x><x>:value</x>
      <input type="hidden" if="masterCss"
             class=":masterCss" value=":rawValue" name=":name" id=":name"/>
     </x>''')

    pxEdit = Px('''
     <x var="isChecked=field.isChecked(zobj, rawValue)">
      <input type="checkbox" name=":name + '_visible'" id=":name"
             class=":masterCss" checked=":isChecked"
             onclick=":'toggleCheckbox(%s, %s); updateSlaves(this)' % \
                       (q(name), q('%s_hidden' % name))"/>
      <input type="hidden" name=":name" id=":'%s_hidden' % name"
             value=":isChecked and 'True' or 'False')"/>
     </x>''')

    pxSearch = Px('''
     <x var="typedWidget='%s*bool' % widgetName">
      <label lfor=":widgetName">:_(field.labelId)"></label><br/>&nbsp;&nbsp;
      <x var="valueId='%s_yes' % name">
       <input type="radio" value="True" name=":typedWidget" id=":valueId"/>
       <label lfor=":valueId">:_('yes')</label>
      </x>
      <x var="valueId='%s_no' % name">
       <input type="radio" value="False" name=":typedWidget" id=":valueId"/>
       <label lfor=":valueId">:_('no')"></label>
      </x>
      <x var="valueId='%s_whatever' % name">
       <input type="radio" value="" name=":typedWidget" id=":valueId"
              checked="checked"/>
       <label lfor=":valueId">:_('whatever')</label>
      </x><br/>
     </x>''')

    def __init__(self, validator=None, multiplicity=(0,1), default=None,
                 show=True, page='main', group=None, layouts = None, move=0,
                 indexed=False, searchable=False, specificReadPermission=False,
                 specificWritePermission=False, width=None, height=None,
                 maxChars=None, colspan=1, master=None, masterValue=None,
                 focus=False, historized=False, mapping=None, label=None,
                 sdefault=False, scolspan=1, swidth=None, sheight=None):
        Field.__init__(self, validator, multiplicity, default, show, page,
                       group, layouts, move, indexed, searchable,
                       specificReadPermission, specificWritePermission, width,
                       height, None, colspan, master, masterValue, focus,
                       historized, True, mapping, label, sdefault, scolspan,
                       swidth, sheight)
        self.pythonType = bool

    # Layout including a description
    dLayouts = {'view': 'lf', 'edit': Table('flrv;=d', width=None)}
    # Centered layout, no description
    cLayouts = {'view': 'lf|', 'edit': 'flrv|'}

    def getDefaultLayouts(self):
        return {'view': 'lf', 'edit': Table('f;lrv;=', width=None)}

    def getValue(self, obj):
        '''Never returns "None". Returns always "True" or "False", even if
           "None" is stored in the DB.'''
        value = Field.getValue(self, obj)
        if value == None: return False
        return value

    def getFormattedValue(self, obj, value, showChanges=False):
        if value: res = obj.translate('yes')
        else:     res = obj.translate('no')
        return res

    def getStorableValue(self, value):
        if not self.isEmptyValue(value):
            exec 'res = %s' % value
            return res

    def isChecked(self, obj, dbValue):
        '''When rendering this field as a checkbox, must it be checked or
           not?'''
        rq = obj.REQUEST
        # Get the value we must compare (from request or from database)
        if rq.has_key(self.name):
            return  rq.get(self.name) in ('True', 1, '1')
        return dbValue
# ------------------------------------------------------------------------------
