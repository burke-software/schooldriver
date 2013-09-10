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

# ------------------------------------------------------------------------------
class Info(Field):
    '''An info is a field whose purpose is to present information
       (text, html...) to the user.'''
    # An info only displays a label. So PX for showing content are empty.
    pxView = pxEdit = pxCell = pxSearch = ''

    def __init__(self, validator=None, multiplicity=(1,1), default=None,
                 show='view', page='main', group=None, layouts=None, move=0,
                 indexed=False, searchable=False, specificReadPermission=False,
                 specificWritePermission=False, width=None, height=None,
                 maxChars=None, colspan=1, master=None, masterValue=None,
                 focus=False, historized=False, mapping=None, label=None):
        Field.__init__(self, None, (0,1), default, show, page, group, layouts,
                       move, indexed, False, specificReadPermission,
                       specificWritePermission, width, height, None, colspan,
                       master, masterValue, focus, historized, False, mapping,
                       label, None, None, None, None)
        self.validable = False
# ------------------------------------------------------------------------------
