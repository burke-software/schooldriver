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
class Action(Field):
    '''An action is a Python method that can be triggered by the user on a
       given gen-class. An action is rendered as a button.'''

    # PX for viewing the Action button.
    pxView = pxCell = Px('''
     <form name="executeAppyAction"
           var="formId='%s_%s_form' % (zobj.UID(), name);
                label=_(field.labelId)"
           id=":formId" action=":ztool.absolute_url() + '/do'">
      <input type="hidden" name="action" value="ExecuteAppyAction"/>
      <input type="hidden" name="objectUid" value=":zobj.UID()"/>
      <input type="hidden" name="fieldName" value=":name"/>
      <input if="field.confirm" type="button" class="button"
         var="labelConfirm=_(field.labelId + '_confirm')"
         value=":ztool.truncateValue(label)" title=":label"
         style=":url('buttonAction', bg=True)"
         onclick=":'askConfirm(%s,%s,%s)' % (q('form'), q(formId), \
                                             q(labelConfirm))"/>
      <input if="not field.confirm" type="submit" class="button" name="do"
             value=":ztool.truncateValue(label)" title=":label"
             style=":url('buttonAction', bg=True)"/>
     </form>''')

    # It is not possible to edit an action, not to search it.
    pxEdit = pxSearch = ''

    def __init__(self, validator=None, multiplicity=(1,1), default=None,
                 show=True, page='main', group=None, layouts=None, move=0,
                 indexed=False, searchable=False, specificReadPermission=False,
                 specificWritePermission=False, width=None, height=None,
                 maxChars=None, colspan=1, action=None, result='computation',
                 confirm=False, master=None, masterValue=None, focus=False,
                 historized=False, mapping=None, label=None):
        # Can be a single method or a list/tuple of methods
        self.action = action
        # For the 'result' param:
        #  * value 'computation' means that the action will simply compute
        #    things and redirect the user to the same page, with some status
        #    message about execution of the action;
        #  * 'file' means that the result is the binary content of a file that
        #    the user will download.
        #  * 'filetmp' is similar to file, but the file is a temp file and Appy
        #    will delete it as soon as it will be served to the browser.
        #  * 'redirect' means that the action will lead to the user being
        #    redirected to some other page.
        self.result = result
        # If following field "confirm" is True, a popup will ask the user if
        # she is really sure about triggering this action.
        self.confirm = confirm
        Field.__init__(self, None, (0,1), default, show, page, group, layouts,
                       move, indexed, False, specificReadPermission,
                       specificWritePermission, width, height, None, colspan,
                       master, masterValue, focus, historized, False, mapping,
                       label, None, None, None, None)
        self.validable = False

    def getDefaultLayouts(self): return {'view': 'l-f', 'edit': 'lrv-f'}

    def __call__(self, obj):
        '''Calls the action on p_obj.'''
        if type(self.action) in sutils.sequenceTypes:
            # There are multiple Python methods
            res = [True, '']
            for act in self.action:
                actRes = act(obj)
                if type(actRes) in sutils.sequenceTypes:
                    res[0] = res[0] and actRes[0]
                    if self.result.startswith('file'):
                        res[1] = res[1] + actRes[1]
                    else:
                        res[1] = res[1] + '\n' + actRes[1]
                else:
                    res[0] = res[0] and actRes
        else:
            # There is only one Python method
            actRes = self.action(obj)
            if type(actRes) in sutils.sequenceTypes:
                res = list(actRes)
            else:
                res = [actRes, '']
        # If res is None (ie the user-defined action did not return anything),
        # we consider the action as successfull.
        if res[0] == None: res[0] = True
        return res

    def isShowable(self, obj, layoutType):
        if layoutType == 'edit': return False
        else: return Field.isShowable(self, obj, layoutType)
# ------------------------------------------------------------------------------
