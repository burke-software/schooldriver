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
from appy import Object
from appy.fields import Field
from appy.px import Px
from appy.gen.layout import Table

# ------------------------------------------------------------------------------
class List(Field):
    '''A list.'''

    # PX for rendering a single row.
    pxRow = Px('''
     <tr valign="top" style="(rowIndex==-1) and 'display: none' or ''">
      <td align="center" for="info in field.fields"
          var2="field=info[1];
                tagCss='noStyle';
                widgetName='%s*%d' % (field.name, rowIndex)">:field.pxView</td>
      <!-- Icon for removing the row -->
      <td if="layoutType=='edit'" align=":dright">
       <img class="clickable" src=":url(delete')" title=":_('object_delete')"
            onclick=":'deleteRow(%s, this)' % q('list_%s' % name)"/>
      </td>
     </tr>''')

    # PX for rendering the list (shared between pxView and pxEdit).
    pxTable = Px('''
     <table var="isEdit=layoutType == 'edit'" if="isEdit or value"
            id=":'list_%s' % name" class="isEdit and 'grid' or 'list'">
      <!-- Header -->
      <tr valign="bottom">
       <th for="info in field.fields">::_(info[1].labelId)</th>
       <!-- Icon for adding a new row. -->
       <th if="isEdit">
        <img class="clickable" src=":url('plus')" title=":_('add_ref')"
             onclick=":'insertRow(%s)' % q('list_%s' % name)"/>
       </th>
      </tr>

      <!-- Template row (edit only) -->
      <x var="rowIndex=-1" if="isEdit">:field.pxRow</x>
      <tr height="7px" if="isEdit"><td></td></tr>

      <!-- Rows of data -->
      <x var="rows=inRequest and requestValue or value"
         for="row in rows" var2="rowIndex=loop.row.nb">:field.pxRow</x>
     </table>''')

    pxView = pxCell = Px('''<x>:field.pxTable</x>''')
    pxEdit = Px('''<x>
     <!-- This input makes Appy aware that this field is in the request -->
     <input type="hidden" name=":name" value=""/><x>:field.pxTable</x>
    </x>''')

    pxSearch = ''

    def __init__(self, fields, validator=None, multiplicity=(0,1), default=None,
                 show=True, page='main', group=None, layouts=None, move=0,
                 indexed=False, searchable=False, specificReadPermission=False,
                 specificWritePermission=False, width=None, height=None,
                 maxChars=None, colspan=1, master=None, masterValue=None,
                 focus=False, historized=False, mapping=None, label=None,
                 subLayouts=Table('fv', width=None)):
        Field.__init__(self, validator, multiplicity, default, show, page,
                       group, layouts, move, indexed, False,
                       specificReadPermission, specificWritePermission, width,
                       height, None, colspan, master, masterValue, focus,
                       historized, True, mapping, label, None, None, None, None)
        self.validable = True
        # Tuples of (names, Field instances) determining the format of every
        # element in the list.
        self.fields = fields
        self.fieldsd = [(n, f.__dict__) for (n,f) in self.fields]
        # Force some layouting for sub-fields, if subLayouts are given. So the
        # one who wants freedom on tuning layouts at the field level must
        # specify subLayouts=None.
        if subLayouts:
            for name, field in self.fields:
                field.layouts = field.formatLayouts(subLayouts)

    def getField(self, name):
        '''Gets the field definition whose name is p_name.'''
        for n, field in self.fields:
            if n == name: return field

    def getRequestValue(self, request, requestName=None):
        '''Concatenates the list from distinct form elements in the request.'''
        name = requestName or self.name # A List may be into another List (?)
        prefix = name + '*' + self.fields[0][0] + '*'
        res = {}
        for key in request.keys():
            if not key.startswith(prefix): continue
            # I have found a row. Gets its index
            row = Object()
            if '_' in key: key = key[:key.index('_')]
            rowIndex = int(key.split('*')[-1])
            if rowIndex == -1: continue # Ignore the template row.
            for subName, subField in self.fields:
                keyName = '%s*%s*%s' % (name, subName, rowIndex)
                v = subField.getRequestValue(request, requestName=keyName)
                setattr(row, subName, v)
            res[rowIndex] = row
        # Produce a sorted list.
        keys = res.keys()
        keys.sort()
        res = [res[key] for key in keys]
        # I store in the request this computed value. This way, when individual
        # subFields will need to get their value, they will take it from here,
        # instead of taking it from the specific request key. Indeed, specific
        # request keys contain row indexes that may be wrong after row deletions
        # by the user.
        request.set(name, res)
        return res

    def getStorableValue(self, value):
        '''Gets p_value in a form that can be stored in the database.'''
        res = []
        for v in value:
            sv = Object()
            for name, field in self.fields:
                setattr(sv, name, field.getStorableValue(getattr(v, name)))
            res.append(sv)
        return res

    def getInnerValue(self, outerValue, name, i):
        '''Returns the value of inner field named p_name in row number p_i
           within the whole list of values p_outerValue.'''
        if i == -1: return ''
        if not outerValue: return ''
        if i >= len(outerValue): return ''
        return getattr(outerValue[i], name, '')

    def getCss(self, layoutType, res):
        '''Gets the CSS required by sub-fields if any.'''
        for name, field in self.fields:
            field.getCss(layoutType, res)

    def getJs(self, layoutType, res):
        '''Gets the JS required by sub-fields if any.'''
        for name, field in self.fields:
            field.getJs(layoutType, res)
# ------------------------------------------------------------------------------
