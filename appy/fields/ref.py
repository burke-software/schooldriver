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
import sys, re
from appy import Object
from appy.fields import Field
from appy.px import Px
from appy.gen.layout import Table
from appy.gen import utils as gutils
from appy.shared import utils as sutils

# ------------------------------------------------------------------------------
class Ref(Field):
    # Some default layouts. "w" stands for "wide": those layouts produce tables
    # of Ref objects whose width is 100%.
    wLayouts = Table('lrv-f', width='100%')
    # "d" stands for "description": a description label is added.
    wdLayouts = {'view': Table('l-d-f', width='100%')}

    # This PX displays the title of a referenced object, with a link on it to
    # reach the consult view for this object. If we are on a back reference, the
    # link allows to reach the correct page where the forward reference is
    # defined. If we are on a forward reference, the "nav" parameter is added to
    # the URL for allowing to navigate from one object to the next/previous one.
    pxObjectTitle = Px('''
     <x var="includeShownInfo=includeShownInfo|False;
             navInfo='ref.%s.%s:%s.%d.%d' % (zobj.id, field.name, \
               field.pageName, loop.tied.nb + 1 + startNumber, totalNumber);
             navInfo=(not field.isBack and not inPickList) and navInfo or '';
             cssClass=tied.o.getCssFor('title')">
      <x>::tied.o.getSupTitle(navInfo)</x>
      <a var="pageName=field.isBack and field.back.pageName or 'main';
              linkInPopup=inPopup or (target.target != '_self');
              fullUrl=tied.o.getUrl(page=pageName, nav=navInfo, \
                                    inPopup=linkInPopup)"
         href=":fullUrl" class=":cssClass" target=":target.target"
         onclick=":target.openPopup">:(not includeShownInfo) and \
         tied.title or field.getReferenceLabel(tied)
      </a><span name="subTitle" style=":showSubTitles and 'display:inline' or \
            'display:none'">::tied.o.getSubTitle()</span></x>''')

    # This PX displays buttons for triggering global actions on several linked
    # objects (delete many, unlink many,...)
    pxGlobalActions = Px('''
     <!-- Insert several objects (if in pick list) -->
     <input if="inPickList" type="button" class="button"
            var2="action='link'; label=_('object_link_many')" value=":label"
            onclick=":'onLinkMany(%s,%s)' % (q(action), q(ajaxHookId))"
            style=":'%s; %s' % (url('linkMany', bg=True), \
                                ztool.getButtonWidth(label))"/>
     <!-- Unlink several objects -->
     <input if="mayUnlink"
            var2="imgName=linkList and 'unlinkManyUp' or 'unlinkMany';
                  action='unlink'; label=_('object_unlink_many')"
            type="button" class="button" value=":label"
            onclick=":'onLinkMany(%s,%s)' % (q(action), q(ajaxHookId))"
            style=":'%s; %s' % (url(imgName, bg=True), \
                                ztool.getButtonWidth(label))"/>
     <!-- Delete several objects -->
     <input if="mayEdit and field.delete"
            var2="action='delete'; label=_('object_delete_many')"
            type="button" class="button" value=":label"
            onclick=":'onLinkMany(%s,%s)' % (q(action), q(ajaxHookId))"
            style=":'%s; %s' % (url('deleteMany', bg=True), \
                                ztool.getButtonWidth(label))"/>
     ''')

    # This PX displays icons for triggering actions on a given referenced object
    # (edit, delete, etc).
    pxObjectActions = Px('''
     <table class="noStyle">
      <tr>
       <!-- Arrows for moving objects up or down -->
       <td if="(totalNumber &gt;1) and changeOrder and not inPickList \
               and not inMenu"
          var2="ajaxBaseCall=navBaseCall.replace('**v**','%s,%s,{%s:%s,%s:%s}'%\
                  (q(startNumber), q('doChangeOrder'), q('refObjectUid'),
                   q(tiedUid), q('move'), q('**v**')))">
        <!-- Move to top -->
        <img if="objectIndex &gt; 1" class="clickable"
             src=":url('arrowsUp')" title=":_('move_top')"
             onclick=":ajaxBaseCall.replace('**v**', 'top')"/>
        <!-- Move to bottom -->
        <img if="objectIndex &lt; (totalNumber-2)" class="clickable"
             src=":url('arrowsDown')" title=":_('move_bottom')"
             onclick=":ajaxBaseCall.replace('**v**', 'bottom')"/>
        <!-- Move up -->
        <img if="objectIndex &gt; 0" class="clickable" src=":url('arrowUp')"
             title=":_('move_up')"
             onclick=":ajaxBaseCall.replace('**v**', 'up')"/>
        <!-- Move down -->
        <img if="objectIndex &lt; (totalNumber-1)" class="clickable"
             src=":url('arrowDown')" title=":_('move_down')"
             onclick=":ajaxBaseCall.replace('**v**', 'down')"/>
       </td>
       <!-- Edit -->
       <td if="not field.noForm and tied.o.mayEdit()">
        <a var="navInfo='ref.%s.%s:%s.%d.%d' % (zobj.id, field.name, \
                   field.pageName, loop.tied.nb + 1 + startNumber, totalNumber);
                linkInPopup=inPopup or (target.target != '_self')"
           href=":tied.o.getUrl(mode='edit', page='main', nav=navInfo, \
                                inPopup=linkInPopup)"
           target=":target.target" onclick=":target.openPopup">
         <img src=":url('edit')" title=":_('object_edit')"/></a>
       </td>
       <!-- Delete -->
       <td if="mayEdit and field.delete and tied.o.mayDelete()">
        <img class="clickable" title=":_('object_delete')" src=":url('delete')"
             onclick=":'onDeleteObject(%s)' % q(tiedUid)"/>
       </td>
       <!-- Unlink -->
       <td if="mayUnlink">
        <img var="imgName=linkList and 'unlinkUp' or 'unlink'; action='unlink'"
             class="clickable" title=":_('object_unlink')" src=":url(imgName)"
             onclick=":'onLink(%s,%s,%s,%s)' % (q(action), q(zobj.id), \
                        q(field.name), q(tiedUid))"/>
       </td>
       <!-- Insert (if in pick list) -->
       <td if="inPickList">
        <img var="action='link'" class="clickable" title=":_('object_link')"
             src=":url(action)"
             onclick=":'onLink(%s,%s,%s,%s)' % (q(action), q(zobj.id), \
                        q(field.name), q(tiedUid))"/>
       </td>
       <!-- Workflow transitions -->
       <td if="tied.o.showTransitions('result')"
           var2="targetObj=tied.o; buttonsMode='small'">:tied.pxTransitions</td>
      </tr>
     </table>''')

    # Displays the button allowing to add a new object through a Ref field, if
    # it has been declared as addable and if multiplicities allow it.
    pxAdd = Px('''
      <form if="mayAdd and not inPickList"
            class=":inMenu and 'addFormMenu' or 'addForm'"
            var2="formName='%s_%s_add' % (zobj.id, field.name)"
            name=":formName" id=":formName" target=":target.target"
            action=":'%s/do' % folder.absolute_url()">
       <input type="hidden" name="action" value="Create"/>
       <input type="hidden" name="className" value=":tiedClassName"/>
       <input type="hidden" name="nav"
              value=":'ref.%s.%s:%s.%d.%d' % (zobj.id, field.name, \
                                              field.pageName, 0, totalNumber)"/>
       <input type="hidden" name="popup"
              value=":(inPopup or (target.target != '_self')) and '1' or '0'"/>
       <input
        type=":(field.addConfirm or field.noForm) and 'button' or 'submit'"
        class="buttonSmall button"
        var="label=_('add_ref')" value=":label"
             style=":'%s; %s' % (url('add', bg=True), \
                                 ztool.getButtonWidth(label))"
             onclick=":field.getOnAdd(q, formName, addConfirmMsg, target, \
                                      navBaseCall, startNumber)"/>
      </form>''')

    # This PX displays, in a cell header from a ref table, icons for sorting the
    # ref field according to the field that corresponds to this column.
    pxSortIcons = Px('''
     <x if="changeOrder and ztool.isSortable(refField.name,tiedClassName,'ref')"
        var2="ajaxBaseCall=navBaseCall.replace('**v**', '%s,%s,{%s:%s,%s:%s}'% \
               (q(startNumber), q('sort'), q('sortKey'), q(refField.name), \
                q('reverse'), q('**v**')))">
      <img class="clickable" src=":url('sortAsc')"
           onclick=":ajaxBaseCall.replace('**v**', 'False')"/>
      <img class="clickable" src=":url('sortDesc')"
           onclick=":ajaxBaseCall.replace('**v**', 'True')"/>
     </x>''')

    # Shows the object number in a numbered list of tied objects.
    pxNumber = Px('''
     <x if="not changeNumber">:objectIndex+1</x>
     <div if="changeNumber" class="dropdownMenu"
          var2="id='%s_%d' % (ajaxHookId, objectIndex);
                dropdownId='%s_dd' % id"
          onmouseover=":'toggleDropdown(%s)' % q(dropdownId)"
          onmouseout=":'toggleDropdown(%s,%s)' % (q(dropdownId), q('none'))">
      <input type="text" size=":numberWidth" id=":id" value=":objectIndex+1"/>
      <!-- The menu -->
      <div id=":dropdownId" class="dropdown">
       <img class="clickable" src=":url('move')" id=":id + '_img'"
            title=":_('move_number')"
            onclick=":navBaseCall.replace('**v**','%s,%s,{%s:%s,%s:this}' % \
                      (q(startNumber), q('doChangeOrder'), q('refObjectUid'),
                       q(tiedUid), q('move')))"/>
      </div>
     </div>''')

    # PX that displays referred objects as a list.
    pxViewList = Px('''
     <div if="not innerRef or mayAdd" style="margin-bottom: 4px">
      <span if="subLabel" class="discreet">:_(subLabel)</span>
      (<span class="discreet">:totalNumber</span>) 
      <x>:field.pxAdd</x>
      <!-- The search button if field is queryable -->
      <input if="objects and field.queryable" type="button"
             class="buttonSmall button"
             var2="label=_('search_button')" value=":label"
             style=":'%s; %s' % (url('search', bg=True), \
                                 ztool.getButtonWidth(label))"
             onclick=":'goto(%s)' % \
              q('%s/search?className=%s&amp;ref=%s:%s' % \
              (ztool.absolute_url(), tiedClassName, zobj.id, field.name))"/>
     </div>

     <!-- (Top) navigation -->
     <x>:tool.pxNavigate</x>

     <!-- No object is present -->
     <p class="discreet"
        if="not objects and (innerRef and mayAdd)">:_('no_ref')</p>

     <!-- Linked objects -->
     <table if="objects" class=":not innerRef and 'list' or ''"
            width=":innerRef and '100%' or field.layouts['view'].width"
            var2="columns=ztool.getColumnsSpecifiers(tiedClassName, \
                   field.shownInfo, dir)">
      <tr if="field.showHeaders">
       <th if="not inPickList and numbered" width=":numbered"></th>
       <th for="column in columns" width=":column.width"
           align=":column.align" var2="refField=column.field">
        <span>:_(refField.labelId)</span>
        <x>:field.pxSortIcons</x>
        <x var="className=tiedClassName;
                field=refField">:tool.pxShowDetails</x>
       </th>
       <th if="checkboxes" class="cbCell">
        <img src=":url('checkall')" class="clickable"
             title=":_('check_uncheck')"
             onclick=":'toggleAllRefCbs(%s)' % q(ajaxHookId)"/>
       </th>
      </tr>
      <!-- Loop on every (tied or selectable) object. -->
      <tr for="tied in objects" valign="top"
          class=":loop.tied.odd and 'even' or 'odd'"
          var2="tiedUid=tied.o.id;
                objectIndex=field.getIndexOf(zobj, tiedUid)|None;
                mayView=tied.o.mayView()">
       <td if="not inPickList and numbered">:field.pxNumber</td>
       <td for="column in columns" width=":column.width" align=":column.align"
           var2="refField=column.field">
        <!-- The "title" field -->
        <x if="refField.name == 'title'">
         <x if="mayView">
          <x>:field.pxObjectTitle</x>
          <div if="tied.o.mayAct()">:field.pxObjectActions</div>
         </x>
         <div if="not mayView">
          <img src=":url('fake')" style="margin-right: 5px"/>
          <x>:_('unauthorized')</x></div>
        </x>
        <!-- Any other field -->
        <x if="(refField.name != 'title') and mayView">
         <x var="zobj=tied.o; obj=tied; layoutType='cell';
                 innerRef=True; field=refField"
            if="field.isShowable(zobj, 'result')">:field.pxRender</x>
        </x>
       </td>
       <td if="checkboxes" class="cbCell">
        <input if="mayView" type="checkbox" name=":ajaxHookId" checked="checked"
               value=":tiedUid" onclick="toggleRefCb(this)"/>
       </td>
      </tr>
     </table>

     <!-- Global actions -->
     <div if="mayEdit and (totalNumber &gt; 1)"
          align=":dright">:field.pxGlobalActions</div>

     <!-- (Bottom) navigation -->
     <x>:tool.pxNavigate</x>

     <!-- Init checkboxes if present. -->
     <script if="checkboxes"
             type="text/javascript">:'initRefCbs(%s)' % q(ajaxHookId)
     </script>''')

    # PX that displays the list of objects the user may select to insert into a
    # ref field with link="list".
    pxViewPickList = Px('''
     <x var="innerRef=False;
             ajaxHookId=ajaxHookId|'%s_%s_poss' % (zobj.id, field.name);
             inPickList=True;
             startNumber=field.getStartNumber('list', req, ajaxHookId);
             info=field.getPossibleValues(zobj, startNumber=startNumber, \
                                          someObjects=True, removeLinked=True);
             objects=info.objects;
             totalNumber=info.totalNumber;
             batchSize=info.batchSize;
             batchNumber=len(objects);
             tiedClassName=tiedClassName|ztool.getPortalType(field.klass);
             mayEdit=mayEdit|\
                     not field.isBack and zobj.mayEdit(field.writePermission);
             mayUnlink=False;
             mayAdd=False;
             navBaseCall='askRefField(%s,%s,%s,%s,**v**)' % \
                          (q(ajaxHookId), q(zobj.absolute_url()), \
                           q(field.name), q(innerRef));
             changeOrder=False;
             changeNumber=False;
             checkboxes=field.getAttribute(zobj, 'checkboxes') and \
                        (totalNumber &gt; 1);
             showSubTitles=showSubTitles|\
                           req.get('showSubTitles', 'true') == 'true';
             subLabel='selectable_objects'">:field.pxViewList</x>''')

    # PX that displays referred objects as dropdown menus.
    pxMenu = Px('''
     <img if="menu.icon" src=":menu.icon" title=":menu.text"/><x
          if="not menu.icon">:menu.text</x>
     <!-- Nb of objects in the menu -->
     <x>:len(menu.objects)</x>''')

    pxViewMenus = Px('''
     <x var2="dtc='display: table-cell'; inMenu=True">
      <!-- No object is present -->
      <div if="not objects" style=":'padding-left: 3px; %s' % dtc"
           class="discreet">-</div>

      <!-- One menu for every object type -->
      <div for="menu in field.getLinkedObjectsByMenu(obj, objects)"
          style=":not loop.menu.last and ('%s;padding-right:4px') % dtc or dtc">
       <div class="dropdownMenu"
            var2="dropdownId='%s_%s_%d' % (zobj.id, name, loop.menu.nb);
                  singleObject=len(menu.objects) == 1"
            onmouseover=":'toggleDropdown(%s)' % q(dropdownId)"
            onmouseout=":'toggleDropdown(%s,%s)' % (q(dropdownId), q('none'))">

        <!-- The menu name and/or icon, that is clickable if there is a single
             object in the menu. -->
        <x if="singleObject" var2="tied=menu.objects[0]">
         <a if="field.menuUrlMethod" class="dropdownMenu"
            href=":field.getMenuUrl(zobj, tied)"
            title=":tied.title">:field.pxMenu</a>
         <a if="not field.menuUrlMethod" class="dropdownMenu"
            var2="linkInPopup=inPopup or (target.target != '_self')"
            target=":target.target" onclick=":target.openPopup"
            href=":tied.o.getUrl(nav='',inPopup=linkInPopup)"
            title=":tied.title">:field.pxMenu</a>
        </x>
        <x if="not singleObject">:field.pxMenu</x>

        <!-- The dropdown menu containing tied objects -->
        <div id=":dropdownId" class="dropdown" style="width:150px">
         <div for="tied in menu.objects"
              var2="startNumber=0;
                    totalNumber=len(menu.objects);
                    tiedUid=tied.uid"
              class=":not loop.tied.first and 'refMenuItem' or ''">
          <!-- A specific link may have to be computed from
               field.menuUrlMethod -->
          <a if="field.menuUrlMethod"
             href=":field.getMenuUrl(zobj, tied)">:tied.title</a>
          <!-- Show standard pxObjectTitle else -->
          <x if="not field.menuUrlMethod">:field.pxObjectTitle</x>
          <div if="tied.o.mayAct()">:field.pxObjectActions</div>
         </div>
        </div>
       </div>
      </div><x>:field.pxAdd</x></x> ''')

    # Simplified widget showing minimal info about tied objects.
    pxViewMinimal = Px('''
     <x var2="infos=[field.getReferenceLabel(o, True) \
                     for o in objects]">:', '.join(infos) or _('no_ref')</x>''')

    # PX that displays referred objects through this field. In mode link="list",
    # if, in the request, key "scope" is present and holds value "objs", the
    # pick list (containing possible values) will not be rendered.
    pxView = Px('''
     <x var="innerRef=req.get('innerRef', False) == 'True';
             ajaxHookId='%s_%s_objs' % (zobj.id, field.name);
             layoutType=layoutType|'view';
             render=field.getRenderMode(layoutType);
             linkList=field.link == 'list';
             renderAll=req.get('scope') != 'objs';
             inPickList=False;
             inMenu=False;
             startNumber=field.getStartNumber(render, req, ajaxHookId);
             info=field.getValue(zobj,startNumber=startNumber,someObjects=True);
             objects=info.objects;
             totalNumber=info.totalNumber;
             numberWidth=len(str(totalNumber));
             batchSize=info.batchSize;
             batchNumber=len(objects);
             folder=zobj.getCreateFolder();
             tiedClassName=ztool.getPortalType(field.klass);
             target=ztool.getLinksTargetInfo(field.klass);
             mayEdit=not field.isBack and zobj.mayEdit(field.writePermission);
             mayUnlink=mayEdit and field.getAttribute(zobj, 'unlink');
             mayAdd=mayEdit and field.mayAdd(zobj, checkMayEdit=False);
             addConfirmMsg=field.addConfirm and \
                           _('%s_addConfirm' % field.labelId) or '';
             navBaseCall='askRefField(%s,%s,%s,%s,**v**)' % \
                          (q(ajaxHookId), q(zobj.absolute_url()), \
                           q(field.name), q(innerRef));
             changeOrder=mayEdit and field.getAttribute(zobj, 'changeOrder');
             numbered=field.isNumbered(zobj);
             changeNumber=not inPickList and numbered and changeOrder and \
                          (totalNumber &gt; 3);
             checkboxesEnabled=field.getAttribute(zobj, 'checkboxes') and \
                               (layoutType != 'cell');
             checkboxes=checkboxesEnabled and (totalNumber &gt; 1);
             showSubTitles=req.get('showSubTitles', 'true') == 'true'">
      <!-- JS tables storing checkbox statuses if checkboxes are enabled -->
      <script if="checkboxesEnabled and renderAll and (render == 'list')"
              type="text/javascript">:field.getCbJsInit(zobj)</script>
      <div if="linkList and renderAll and mayEdit"
           var2="ajaxHookId='%s_%s_poss' % (zobj.id, field.name)"
           id=":ajaxHookId">:field.pxViewPickList</div>
      <x if="render == 'list'"
         var2="subLabel=linkList and 'selected_objects' or None">
       <div if="renderAll" id=":ajaxHookId">:field.pxViewList</div>
       <x if="not renderAll">:field.pxViewList</x>
      </x>
      <x if="render in ('menus','minimal')">:getattr(field, 'pxView%s' % \
         render.capitalize())</x>
     </x>''')

    pxCell = pxView
    pxEdit = Px('''
     <select if="field.link"
             var2="objects=field.getPossibleValues(zobj);
                   uids=[o.id for o in field.getValue(zobj, appy=False)]"
             name=":name" id=":name" size=":isMultiple and field.height or ''"
             onchange=":field.getOnChange(zobj, layoutType)"
             multiple=":isMultiple">
      <option value="" if="not isMultiple">:_('choose_a_value')</option>
      <option for="tied in objects"
              var2="uid=tied.uid;
                    title=field.getReferenceLabel(tied, unlimited=True)"
              selected=":inRequest and (uid in requestValue) or \
                                       (uid in uids)" value=":uid"
              title=":title">:ztool.truncateValue(title, field.width)</option>
     </select>''')

    pxSearch = Px('''
     <!-- The "and" / "or" radio buttons -->
     <x if="field.multiplicity[1] != 1"
        var2="operName='o_%s' % name;
              orName='%s_or' % operName;
              andName='%s_and' % operName">
      <input type="radio" name=":operName" id=":orName" checked="checked"
             value="or"/>
      <label lfor=":orName">:_('search_or')</label>
      <input type="radio" name=":operName" id=":andName" value="and"/>
      <label lfor=":andName">:_('search_and')</label><br/>
     </x>
     <!-- The list of values -->
     <select var="objects=field.getPossibleValues(ztool);
                  selectAll='masterValues' in req"
             name=":widgetName" size=":field.sheight" multiple="multiple"
             onchange=":field.getOnChange(ztool, 'search', className)">
      <option for="tied in objects" value=":tied.uid" selected=":selectAll"
              var2="title=field.getReferenceLabel(tied, unlimited=True)"
              title=":title">:ztool.truncateValue(title, field.swidth)</option>
     </select>''')

    def __init__(self, klass=None, attribute=None, validator=None,
                 multiplicity=(0,1), default=None, add=False, addConfirm=False,
                 delete=None, noForm=False, link=True, unlink=None, back=None,
                 show=True, page='main', group=None, layouts=None,
                 showHeaders=False, shownInfo=(), select=None, maxPerPage=30,
                 move=0, indexed=False, searchable=False,
                 specificReadPermission=False, specificWritePermission=False,
                 width=None, height=5, maxChars=None, colspan=1, master=None,
                 masterValue=None, focus=False, historized=False, mapping=None,
                 label=None, queryable=False, queryFields=None, queryNbCols=1,
                 navigable=False, changeOrder=True, numbered=False,
                 checkboxes=True, checkboxesDefault=None, sdefault='',
                 scolspan=1, swidth=None, sheight=None, sselect=None,
                 persist=True, render='list', menuIdMethod=None,
                 menuInfoMethod=None, menuUrlMethod=None):
        self.klass = klass
        self.attribute = attribute
        # May the user add new objects through this ref ?
        self.add = add
        # When the user adds a new object, must a confirmation popup be shown?
        self.addConfirm = addConfirm
        # May the user delete objects via this Ref?
        self.delete = delete
        if delete == None:
            # By default, one may delete objects via a Ref for which one can
            # add objects.
            self.delete = bool(self.add)
        # If noForm is True, when clicking to create an object through this ref,
        # the object will be created automatically, and no creation form will
        # be presented to the user.
        self.noForm = noForm
        # May the user link existing objects through this ref? If "link" is;
        # True,    the user will, on the edit page, choose objects from a
        #          dropdown menu;
        # "list",  the user will, on the view page, choose objects from a list
        #          of objects which is similar to those rendered in pxViewList;
        # "popup", the user will, on the edit page, choose objects from a popup
        #          menu.
        self.link = link
        # May the user unlink existing objects?
        self.unlink = unlink
        if unlink == None:
            # By default, one may unlink objects via a Ref for which one can
            # link objects.
            self.unlink = bool(self.link)
        self.back = None
        if back:
            # It is a forward reference
            self.isBack = False
            # Initialise the backward reference
            self.back = back
            back.isBack = True
            back.back = self
            # klass may be None in the case we are defining an auto-Ref to the
            # same class as the class where this field is defined. In this case,
            # when defining the field within the class, write
            # myField = Ref(None, ...)
            # and, at the end of the class definition (name it K), write:
            # K.myField.klass = K
            # setattr(K, K.myField.back.attribute, K.myField.back)
            if klass: setattr(klass, back.attribute, back)
        # When displaying a tabular list of referenced objects, must we show
        # the table headers?
        self.showHeaders = showHeaders
        # When displaying referenced object(s), we will display its title + all
        # other fields whose names are listed in the following attribute.
        self.shownInfo = list(shownInfo)
        if not self.shownInfo: self.shownInfo.append('title')
        # If a method is defined in this field "select", it will be used to
        # return the list of possible tied objects. Be careful: this method can
        # receive, in its first argument ("self"), the tool instead of an
        # instance of the class where this field is defined. This little cheat
        # is:
        #  - not really a problem: in this method you will mainly use methods
        #    that are available on a tool as well as on any object (like
        #    "search");
        #  - necessary because in some cases we do not have an instance at our
        #    disposal, ie, when we need to compute a list of objects on a
        #    search screen.
        # NOTE that when a method is defined in field "masterValue" (see parent
        # class "Field"), it will be used instead of select (or sselect below).
        self.select = select
        # If you want to specify, for the search screen, a list of objects that
        # is different from the one produced by self.select, define an
        # alternative method in field "sselect" below.
        self.sselect = sselect or self.select
        # Maximum number of referenced objects shown at once.
        self.maxPerPage = maxPerPage
        # If param p_queryable is True, the user will be able to perform queries
        # from the UI within referenced objects.
        self.queryable = queryable
        # Here is the list of fields that will appear on the search screen.
        # If None is specified, by default we take every indexed field
        # defined on referenced objects' class.
        self.queryFields = queryFields
        # The search screen will have this number of columns
        self.queryNbCols = queryNbCols
        # Within the portlet, will referred elements appear ?
        self.navigable = navigable
        # If "changeOrder" is or returns False, it even if the user has the
        # right to modify the field, it will not be possible to move objects or
        # sort them.
        self.changeOrder = changeOrder
        # If "numbered" is or returns True, a leading column will show the
        # number of every tied object. Moreover, if the user can change order of
        # tied objects, an input field will allow him to enter a new number for
        # the tied object. If "numbered" is or returns a string, it will be used
        # as width for the column containing the number. Else, a default width
        # will be used.
        self.numbered = numbered
        # If "checkboxes" is or returns True, every linked object will be
        # "selectable" via a checkbox. Global actions will be activated and will
        # act on the subset of selected objects: delete, unlink, etc.
        self.checkboxes = checkboxes
        # Default value for checkboxes, if enabled.
        if checkboxesDefault == None:
            self.checkboxesDefault = bool(self.link)
        else:
            self.checkboxesDefault = checkboxesDefault
        # There are different ways to render a bunch of linked objects:
        # - "list" (the default) renders them as a list (=a XHTML table);
        # - "menus" renders them as a series of popup menus, grouped by type.
        # Note that render mode "menus" will only be applied in "cell" layouts.
        # Indeed, we need to keep the "list" rendering in the "view" layout
        # because the "menus" rendering is minimalist and does not allow to
        # perform all operations on linked objects (add, move, delete, edit...);
        # - "minimal" renders a list of comma-separated, not-even-clickable,
        # data about the tied objects (according to shownInfo).
        self.render = render
        # If render is 'menus', 2 methods must be provided.
        # "menuIdMethod" will be called, with every linked object as single arg,
        # and must return an ID that identifies the menu into which the object
        # will be inserted.
        self.menuIdMethod = menuIdMethod
        # "menuInfoMethod" will be called with every collected menu ID (from
        # calls to the previous method) to get info about this menu. This info
        # must be a tuple (text, icon):
        # - "text" is the menu name;
        # - "icon" (can be None) gives the URL of an icon, if you want to render
        #   the menu as an icon instead of a text.
        self.menuInfoMethod = menuInfoMethod
        # "menuUrlMethod" is an optional method that allows to compute an
        # alternative URL for the tied object that is shown within the menu.
        self.menuUrlMethod = menuUrlMethod
        Field.__init__(self, validator, multiplicity, default, show, page,
                       group, layouts, move, indexed, False,
                       specificReadPermission, specificWritePermission, width,
                       height, None, colspan, master, masterValue, focus,
                       historized, mapping, label, sdefault, scolspan, swidth,
                       sheight, persist)
        self.validable = bool(self.link)

    def getDefaultLayouts(self):
        return {'view': Table('l-f', width='100%'), 'edit': 'lrv-f'}

    def isShowable(self, obj, layoutType):
        res = Field.isShowable(self, obj, layoutType)
        if not res: return res
        # We add here specific Ref rules for preventing to show the field under
        # some inappropriate circumstances.
        if layoutType == 'edit':
            if self.mayAdd(obj): return
            if self.link in (False, 'list'): return
        if self.isBack:
            if layoutType == 'edit': return
            else: return getattr(obj.aq_base, self.name, None)
        return res

    def getValue(self, obj, appy=True, noListIfSingleObj=False,
                 startNumber=None, someObjects=False):
        '''Returns the objects linked to p_obj through this Ref field. It
           returns Appy wrappers if p_appy is True, the Zope objects else.

           * If p_startNumber is None, it returns all referred objects;
           * if p_startNumber is a number, it returns self.maxPerPage objects,
             starting at p_startNumber.

           If p_noListIfSingleObj is True, it returns the single reference as
           an object and not as a list.

           If p_someObjects is True, it returns an instance of SomeObjects
           instead of returning a list of references.'''
        uids = getattr(obj.aq_base, self.name, [])
        if not uids:
            # Maybe is there a default value?
            defValue = Field.getValue(self, obj)
            if defValue:
                if type(defValue) in sutils.sequenceTypes:
                    uids = [o.o.id for o in defValue]
                else:
                    uids = [defValue.o.id]
        # Prepare the result: an instance of SomeObjects, that will be unwrapped
        # if not required.
        res = gutils.SomeObjects()
        res.totalNumber = res.batchSize = len(uids)
        batchNeeded = startNumber != None
        if batchNeeded:
            res.batchSize = self.maxPerPage
        if startNumber != None:
            res.startNumber = startNumber
        # Get the objects given their uids
        i = res.startNumber
        while i < (res.startNumber + res.batchSize):
            if i >= res.totalNumber: break
            # Retrieve every reference in the correct format according to p_type
            tied = obj.getTool().getObject(uids[i])
            if appy: tied = tied.appy()
            res.objects.append(tied)
            i += 1
        # Manage parameter p_noListIfSingleObj
        if res.objects and noListIfSingleObj:
            if self.multiplicity[1] == 1:
                res.objects = res.objects[0]
        if someObjects: return res
        return res.objects

    def getPossibleValues(self, obj, startNumber=None, someObjects=False,
                          removeLinked=False):
        '''This method returns the list of all objects that can be selected
           to be linked as references to p_obj via p_self. It is applicable only
           for Ref fields with link!=False. If master values are present in the
           request, we use field.masterValues method instead of self.select.

           If p_startNumber is a number, it returns self.maxPerPage objects,
           starting at p_startNumber. If p_someObjects is True, it returns an
           instance of SomeObjects instead of returning a list of objects.

           If p_removeLinked is True, we remove, from the result, objects which
           are already linked. For example, for Ref fields rendered as a
           dropdown menu or a multi-selection box (with link=True), on the edit
           page, we need to display all possible values: those that are already
           linked appear to be selected in the widget. But for Ref fields
           rendered as pick lists (link="list"), once an object is linked, it
           must disappear from the "pick list".
        '''
        req = obj.REQUEST
        obj = obj.appy()
        if 'masterValues' in req:
            # Convert masterValue(s) from id(s) to real object(s).
            masterValues = req['masterValues'].strip()
            if not masterValues: masterValues = None
            else:
                masterValues = masterValues.split('*')
                tool = obj.tool
                if len(masterValues) == 1:
                    masterValues = tool.getObject(masterValues[0])
                else:
                    masterValues = [tool.getObject(v) for v in masterValues]
            objects = self.masterValue(obj, masterValues)
        else:
            # If this field is an ajax-updatable slave, no need to compute
            # possible values: it will be overridden by method self.masterValue
            # by a subsequent ajax request (=the "if" statement above).
            if self.masterValue and callable(self.masterValue):
                objects = []
            else:
                if not self.select:
                    # No select method has been defined: we must retrieve all
                    # objects of the referred type that the user is allowed to
                    # access.
                    objects = obj.search(self.klass)
                else:
                    objects = self.select(obj)
        # Remove already linked objects if required.
        if removeLinked:
            uids = getattr(obj.o.aq_base, self.name, None)
            if uids:
                # Browse objects in reverse order and remove linked objects.
                i = len(objects) - 1
                while i >= 0:
                    if objects[i].uid in uids: del objects[i]
                    i -= 1
        # Restrict, if required, the result to self.maxPerPage starting at
        # p_startNumber. Unlike m_getValue, we already have all objects in
        # "objects": we can't limit objects "waking up" to at most
        # self.maxPerPage.
        total = len(objects)
        if startNumber != None:
            objects = objects[startNumber:startNumber + self.maxPerPage]
        # Return the result, wrapped in a SomeObjects instance if required.
        if not someObjects: return objects
        res = gutils.SomeObjects()
        res.totalNumber = total
        res.batchSize = self.maxPerPage
        res.startNumber = startNumber
        res.objects = objects
        return res

    def getLinkedObjectsByMenu(self, obj, objects):
        '''This method groups p_objects into sub-lists of objects, grouped by
           menu (happens when self.render == 'menus').'''
        if not objects: return ()
        res = []
        # We store in "menuIds" the already encountered menus:
        # ~{s_menuId : i_indexInRes}~
        menuIds = {}
        # Browse every object from p_objects and put them in their menu
        # (within "res").
        for tied in objects:
            menuId = self.menuIdMethod(obj, tied)
            if menuId in menuIds:
                # We have already encountered this menu.
                menuIndex = menuIds[menuId]
                res[menuIndex].objects.append(tied)
            else:
                # A new menu.
                menu = Object(id=menuId, objects=[tied])
                res.append(menu)
                menuIds[menuId] = len(res) - 1
        # Complete information about every menu by calling self.menuInfoMethod
        for menu in res:
            text, icon = self.menuInfoMethod(obj, menu.id)
            menu.text = text
            menu.icon = icon
        return res

    def isNumbered(self, obj):
        '''Must we show the order number of every tied object?'''
        res = self.getAttribute(obj, 'numbered')
        if not res: return res
        # Returns the column width.
        if not isinstance(res, basestring): return '15px'
        return res

    def getMenuUrl(self, zobj, tied):
        '''We must provide the URL of the p_tied object, when shown in a Ref
           field in render mode 'menus'. If self.menuUrlMethod is specified,
           use it. Else, returns the "normal" URL of the view page for the tied
           object, but without any navigation information, because in this
           render mode, tied object's order is lost and navigation is
           impossible.'''
        if self.menuUrlMethod:
            return self.menuUrlMethod(zobj.appy(), tied)
        return tied.o.getUrl(nav='')

    def getStartNumber(self, render, req, ajaxHookId):
        '''This method returns the index of the first linked object that must be
           shown, or None if all linked objects must be shown at once (it
           happens when p_render is "menus").'''
        # When using 'menus' render mode, all linked objects must be shown.
        if render == 'menus': return
        # When using 'list' (=default) render mode, the index of the first
        # object to show is in the request.
        return int(req.get('%s_startNumber' % ajaxHookId, 0))

    def getFormattedValue(self, obj, value, showChanges=False):
        return value

    def getIndexType(self): return 'ListIndex'

    def getIndexValue(self, obj, forSearch=False):
        '''Value for indexing is the list of UIDs of linked objects. If
           p_forSearch is True, it will return a list of the linked objects'
           titles instead.'''
        if not forSearch:
            res = getattr(obj.aq_base, self.name, [])
            if res:
                # The index does not like persistent lists.
                res = list(res)
            else:
                # Ugly catalog: if I return an empty list, the previous value
                # is kept.
                res.append('')
            return res
        else:
            # For the global search: return linked objects' titles.
            res = [o.title for o in self.getValue()]
            if not res: res.append('')
            return res

    def validateValue(self, obj, value):
        if not self.link: return
        # We only check "link" Refs because in edit views, "add" Refs are
        # not visible. So if we check "add" Refs, on an "edit" view we will
        # believe that that there is no referred object even if there is.
        # Also ensure that multiplicities are enforced.
        if not value:
            nbOfRefs = 0
        elif isinstance(value, basestring):
            nbOfRefs = 1
        else:
            nbOfRefs = len(value)
        minRef = self.multiplicity[0]
        maxRef = self.multiplicity[1]
        if maxRef == None:
            maxRef = sys.maxint
        if nbOfRefs < minRef:
            return obj.translate('min_ref_violated')
        elif nbOfRefs > maxRef:
            return obj.translate('max_ref_violated')

    def linkObject(self, obj, value, back=False, noSecurity=True):
        '''This method links p_value (which can be a list of objects) to p_obj
           through this Ref field.'''
        # Security check
        if not noSecurity: obj.mayEdit(self.writePermission, raiseError=True)
        # p_value can be a list of objects
        if type(value) in sutils.sequenceTypes:
            for v in value: self.linkObject(obj, v, back=back)
            return
        # Gets the list of referred objects (=list of uids), or create it.
        obj = obj.o
        refs = getattr(obj.aq_base, self.name, None)
        if refs == None:
            refs = obj.getProductConfig().PersistentList()
            setattr(obj, self.name, refs)
        # Insert p_value into it.
        uid = value.o.id
        if uid not in refs:
            # Where must we insert the object? At the start? At the end?
            if callable(self.add):
                add = self.callMethod(obj, self.add)
            else:
                add = self.add
            if add == 'start':
                refs.insert(0, uid)
            else:
                refs.append(uid)
            # Update the back reference
            if not back: self.back.linkObject(value, obj, back=True)

    def unlinkObject(self, obj, value, back=False, noSecurity=True):
        '''This method unlinks p_value (which can be a list of objects) from
           p_obj through this Ref field.'''
        # Security check
        if not noSecurity: obj.mayEdit(self.writePermission, raiseError=True)
        # p_value can be a list of objects
        if type(value) in sutils.sequenceTypes:
            for v in value: self.unlinkObject(obj, v, back=back)
            return
        obj = obj.o
        refs = getattr(obj.aq_base, self.name, None)
        if not refs: return
        # Unlink p_value
        uid = value.o.UID()
        if uid in refs:
            refs.remove(uid)
            # Update the back reference
            if not back: self.back.unlinkObject(value, obj, back=True)

    def store(self, obj, value):
        '''Stores on p_obj, the p_value, which can be:
           * None;
           * an object UID (=string);
           * a list of object UIDs (=list of strings). Generally, UIDs or lists
             of UIDs come from Ref fields with link:True edited through the web;
           * a Zope object;
           * a Appy object;
           * a list of Appy or Zope objects.'''
        if not self.persist: return
        # Standardize p_value into a list of Zope objects
        objects = value
        if not objects: objects = []
        if type(objects) not in sutils.sequenceTypes: objects = [objects]
        tool = obj.getTool()
        for i in range(len(objects)):
            if isinstance(objects[i], basestring):
                # We have a UID here
                objects[i] = tool.getObject(objects[i])
            else:
                # Be sure to have a Zope object
                objects[i] = objects[i].o
        uids = [o.UID() for o in objects]
        # Unlink objects that are not referred anymore
        refs = getattr(obj.aq_base, self.name, None)
        if refs:
            i = len(refs)-1
            while i >= 0:
                if refs[i] not in uids:
                    # Object having this UID must unlink p_obj
                    self.back.unlinkObject(tool.getObject(refs[i]), obj)
                i -= 1
        # Link new objects
        if objects:
            self.linkObject(obj, objects)

    def mayAdd(self, obj, checkMayEdit=True):
        '''May the user create a new referred object from p_obj via this Ref?
           If p_checkMayEdit is False, it means that the condition of being
           allowed to edit this Ref field has already been checked somewhere
           else (it is always required, we just want to avoid checking it
           twice).'''
        # We can't (yet) do that on back references.
        if self.isBack: return gutils.No('is_back')
        # Check if this Ref is addable
        if callable(self.add):
            add = self.callMethod(obj, self.add)
        else:
            add = self.add
        if not add: return gutils.No('no_add')
        # Have we reached the maximum number of referred elements?
        if self.multiplicity[1] != None:
            refCount = len(getattr(obj, self.name, ()))
            if refCount >= self.multiplicity[1]: return gutils.No('max_reached')
        # May the user edit this Ref field?
        if checkMayEdit:
            if not obj.mayEdit(self.writePermission):
                return gutils.No('no_write_perm')
        # May the user create instances of the referred class?
        if not obj.getTool().userMayCreate(self.klass):
            return gutils.No('no_create_perm')
        return True

    def checkAdd(self, obj):
        '''Compute m_mayAdd above, and raise an Unauthorized exception if
           m_mayAdd returns False.'''
        may = self.mayAdd(obj)
        if not may:
            obj.raiseUnauthorized("User can't write Ref field '%s' (%s)." % \
                                  (self.name, may.msg))

    def getOnAdd(self, q, formName, addConfirmMsg, target, navBaseCall,
                 startNumber):
        '''Computes the JS code to execute when button "add" is clicked.'''
        if self.noForm:
            # Ajax-refresh the Ref with a special param to link a newly created
            # object.
            res = navBaseCall.replace('**v**',
                                      "%d,'doCreateWithoutForm'" % startNumber)
            if self.addConfirm:
                res = "askConfirm('script', %s, %s)" % \
                      (q(res, False), q(addConfirmMsg))
        else:
            # In the basic case, no JS code is executed: target.openPopup is
            # empty and the button-related form is submitted in the main page.
            res = target.openPopup
            if self.addConfirm and not target.openPopup:
                res = "askConfirm('form','%s',%s)" % (formName,q(addConfirmMsg))
            elif self.addConfirm and target.openPopup:
                res = "askConfirm('form+script',%s,%s)" % \
                      (q(formName + '+' + target.openPopup, False), \
                       q(addConfirmMsg))
        return res

    def getCbJsInit(self, obj):
        '''When checkboxes are enabled, this method defines a JS associative
           array (named "_appy_objs_cbs") that will store checkboxes' statuses.
           This array is needed because all linked objects are not visible at
           the same time (pagination).

           Moreover, if self.link is "list", an additional array (named
           "_appy_poss_cbs") is defined for possible values.

           Semantics of this (those) array(s) can be as follows: if a key is
           present in it for a given linked object, it means that the
           checkbox is unchecked. In this case, all linked objects are selected
           by default. But the semantics can be inverted: presence of a key may
           mean that the checkbox is checked. The current array semantics is
           stored in a variable named "_appy_objs_sem" (or "_appy_poss_sem")
           and may hold "unchecked" (initial semantics) or "checked" (inverted
           semantics). Inverting semantics allows to keep the array small even
           when checking/unchecking all checkboxes.
           
           The mentioned JS arrays and variables are stored as attributes of the
           DOM node representing this field.'''
        # The initial semantics depends on the checkboxes default value.
        default = self.getAttribute(obj, 'checkboxesDefault') and \
                  'unchecked' or 'checked'
        code = "\nnode['_appy_%%s_cbs']={};\nnode['_appy_%%s_sem']='%s';" % \
               default
        poss = (self.link == 'list') and (code % ('poss', 'poss')) or ''
        return "var node=document.getElementById('%s_%s');%s%s" % \
               (obj.id, self.name, code % ('objs', 'objs'), poss)

    def doChangeOrder(self, obj):
        '''Moves a referred object up/down/top/bottom.'''
        rq = obj.REQUEST
        # How to move the item?
        move = rq['move']
        # Get the UID of the tied object to move
        uid = rq['refObjectUid']
        uids = getattr(obj.aq_base, self.name)
        oldIndex = uids.index(uid)
        if move == 'up':
            newIndex = oldIndex - 1
        elif move == 'down':
            newIndex = oldIndex + 1
        elif move == 'top':
            newIndex = 0
        elif move == 'bottom':
            newIndex = len(uids) - 1
        elif move.startswith('index'):
            # New index starts at 1 (oldIndex starts at 0).
            try:
                newIndex = int(move.split('_')[1]) - 1
            except ValueError:
                newIndex = -1
        # If newIndex is negative, it means that the move can't occur.
        if newIndex > -1:
            uids.remove(uid)
            uids.insert(newIndex, uid)

    def doCreateWithoutForm(self, obj):
        '''This method is called when a user wants to create a object from a
           reference field, automatically (without displaying a form).'''
        obj.appy().create(self.name)

    xhtmlToText = re.compile('<.*?>', re.S)
    def getReferenceLabel(self, refObject, unlimited=False):
        '''p_self must have link=True. I need to display, on an edit view, the
           p_refObject in the listbox that will allow the user to choose which
           object(s) to link through the Ref. The information to display may
           only be the object title or more if self.shownInfo is used.'''
        res = ''
        for fieldName in self.shownInfo:
            refType = refObject.o.getAppyType(fieldName)
            value = getattr(refObject, fieldName)
            value = refType.getFormattedValue(refObject.o, value)
            if refType.type == 'String':
                if refType.format == 2:
                    value = self.xhtmlToText.sub(' ', value)
                elif type(value) in sutils.sequenceTypes:
                    value = ', '.join(value)
            prefix = res and ' | ' or ''
            res += prefix + value
        if unlimited: return res
        maxWidth = self.width or 30
        if len(res) > maxWidth:
            res = refObject.tool.o.truncateValue(res, maxWidth)
        return res

    def getIndexOf(self, obj, tiedUid, raiseError=True):
        '''Gets the position of tied object identified by p_tiedUid within this
           field on p_obj.'''
        uids = getattr(obj.aq_base, self.name, None)
        if not uids:
            if raiseError: raise IndexError()
            else: return
        if tiedUid in uids:
            return uids.index(tiedUid)
        else:
            if raiseError: raise IndexError()
            else: return

    def sort(self, obj):
        '''Called when the user wants to sort the content of this field.'''
        rq = obj.REQUEST
        sortKey = rq.get('sortKey')
        reverse = rq.get('reverse') == 'True'
        obj.appy().sort(self.name, sortKey=sortKey, reverse=reverse)

    def getRenderMode(self, layoutType):
        '''Gets the render mode, determined by self.render and some
           exceptions.'''
        if (layoutType == 'view') and (self.render == 'menus'): return 'list'
        return self.render

    def onUiRequest(self, obj, rq):
        '''This method is called when an action tied to this Ref field is
           triggered from the user interface (link, unlink, link_many,
           unlink_many, delete_many).'''
        action = rq['linkAction']
        tool = obj.getTool()
        msg = None
        if not action.endswith('_many'):
            # "link" or "unlink"
            tied = tool.getObject(rq['targetUid'])
            exec 'self.%sObject(obj, tied, noSecurity=False)' % action
        else:
            # "link_many", "unlink_many", "delete_many". As a preamble, perform
            # a security check once, instead of doing it on every object-level
            # operation.
            obj.mayEdit(self.writePermission, raiseError=True)
            # Get the (un-)checked objects from the request.
            uids = rq['targetUid'].strip(',') or ();
            if uids: uids = uids.split(',')
            unchecked = rq['semantics'] == 'unchecked'
            if action == 'link_many':
                # Get possible values (objects)
                values = self.getPossibleValues(obj, removeLinked=True)
                isObj = True
            else:
                # Get current values (uids)
                values = getattr(obj.aq_base, self.name, ())
                isObj = False
            # Collect the objects onto which the action must be performed.
            targets = []
            for value in values:
                uid = not isObj and value or value.uid
                if unchecked:
                    # Keep only objects not among uids.
                    if uid in uids: continue
                else:
                    # Keep only objects being in uids.
                    if uid not in uids: continue
                # Collect this object
                target = not isObj and tool.getObject(value) or value.o
                targets.append(target)
            if not targets:
                msg = obj.translate('action_null')
            else:
                # Perform the action on every target. Count the number of failed
                # operations.
                failed = 0
                mustDelete = action == 'delete_many'
                for target in targets:
                    if mustDelete:
                        # Delete
                        if target.mayDelete(): target.delete()
                        else: failed += 1
                    else:
                        # Link or unlink
                        exec 'self.%sObject(obj, target)' % action.split('_')[0]
                if failed:
                    msg = obj.translate('action_partial', mapping={'nb':failed})
        urlBack = obj.getUrl(rq['HTTP_REFERER'])
        if not msg: msg = obj.translate('action_done')
        obj.say(msg)
        tool.goto(urlBack)

def autoref(klass, field):
    '''klass.field is a Ref to p_klass. This kind of auto-reference can't be
       declared in the "normal" way, like this:

       class A:
           attr1 = Ref(A)

       because at the time Python encounters the static declaration
       "attr1 = Ref(A)", class A is not completely defined yet.

       This method allows to overcome this problem. You can write such
       auto-reference like this:

       class A:
           attr1 = Ref(None)
       autoref(A, A.attr1)

       This function can also be used to avoid circular imports between 2
       classes from 2 different packages. Imagine class P1 in package p1 has a
       Ref to class P2 in package p2; and class P2 has another Ref to p1.P1
       (which is not the back Ref of the previous one: it is another,
       independent Ref).

       In p1, you have

       from p2 import P2
       class P1:
           ref1 = Ref(P2)

       Then, if you write the following in p2, python will complain because of a
       circular import:

       from p1 import P1
       class P2:
           ref2 = Ref(P1)

       The solution is to write this. In p1:

       from p2 import P2
       class P1:
           ref1 = Ref(P2)
       autoref(P1, P2.ref2)

       And, in p2:
       class P2:
           ref2 = Ref(None)
    '''
    field.klass = klass
    setattr(klass, field.back.attribute, field.back)
# ------------------------------------------------------------------------------
