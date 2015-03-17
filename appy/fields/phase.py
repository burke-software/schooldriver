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
from appy.px import Px

# ------------------------------------------------------------------------------
class Phase:
    '''A group of pages.'''

    pxView = Px('''
     <table class="phase"
            var="singlePage=len(phase.pages) == 1;
                 label='%s_phase_%s' % (zobj.meta_type, phase.name)">
      <tr valign="top">
       <!-- The page(s) within the phase -->
       <td for="aPage in phase.pages"
           var2="aPageInfo=phase.pagesInfo[aPage]"
           class=":(aPage == page) and 'currentPage' or ''">
        <!-- First line: page name and icons -->
        <span if="not (singlePhase and singlePage)">
         <x var="label=aPageInfo.page.getLabel(zobj)">
          <a if="aPageInfo.showOnView"
             href=":zobj.getUrl(page=aPage, inPopup=inPopup)">::label</a>
          <x if="not aPageInfo.showOnView">:label</x>
         </x>
         <x var="locked=zobj.isLocked(user, aPage);
                 editable=mayEdit and aPageInfo.showOnEdit and \
                          aPageInfo.showEdit">
          <a if="editable and not locked"
             href=":zobj.getUrl(mode='edit', page=aPage, inPopup=inPopup)">
           <img src=":url('edit')" title=":_('object_edit')"/></a>
          <a if="editable and locked">
           <img style="cursor: help"
                var="lockDate=ztool.formatDate(locked[1]);
                     lockMap={'user':ztool.getUserName(locked[0]), \
                              'date':lockDate};
                     lockMsg=_('page_locked', mapping=lockMap)"
                src=":url('locked')" title=":lockMsg"/></a>
          <a if="editable and locked and user.has_role('Manager')">
           <img class="clickable" title=":_('page_unlock')" src=":url('unlock')"
                onclick=":'onUnlockPage(%s,%s)' % (q(zobj.id), q(aPage))"/></a>
         </x>
        </span>
        <!-- Next lines: links -->
        <x var="links=aPageInfo.links" if="links">
         <div for="link in links" class="refLink">
          <a href=":link.url">:link.title</a></div>
        </x>
       </td>
      </tr>
     </table>''')

    # "Static" PX that displays all phases of a given object.
    pxAllPhases = Px('''
     <x var="singlePhase=len(phases)==1;
             page=req.get('page', '');
             uid=zobj.id;
             mayEdit=zobj.mayEdit()">
      <x if="singlePhase" var2="phase=phases[0]">:phase.pxView</x>
      <!-- Display several phases in tabs. -->
      <x if="not singlePhase">
       <table cellpadding="0" cellspacing="0">
        <!-- First row: the tabs. -->
        <tr><td style="border-bottom: 1px solid #ff8040; padding-bottom: 1px">
         <table cellpadding="0" cellspacing="0" class="tabs">
          <tr valign="middle">
           <x for="phase in phases"
              var2="nb=loop.phase.nb + 1;
                    suffix='%s_%d_%d' % (uid, nb, len(phases));
                    tabId='tab_%s' % suffix">
            <td><img src=":url('tabLeft')" id=":'%s_left' % tabId"/></td>
            <td style=":url('tabBg',bg=True)" id=":tabId" class="tab">
             <a onclick=":'showTab(%s)' % q(suffix)"
                class="clickable">:_('%s_phase_%s' % (zobj.meta_type, \
                                                      phase.name))</a>
            </td>
            <td><img id=":'%s_right' % tabId" src=":url('tabRight')"/></td>
           </x>
          </tr>
         </table>
        </td></tr>
        <!-- Other rows: the fields -->
        <tr for="phase in phases"
            var2="nb=loop.phase.nb + 1"
            id=":'tabcontent_%s_%d_%d' % (uid, nb, len(phases))"
            style=":(nb == 1) and 'display:table-row' or 'display:none'">
         <td>:phase.pxView</td>
        </tr>
       </table>
       <script type="text/javascript">:'initTab(%s,%s)' % \
        (q('tab_%s' % uid), q('%s_1_%d' % (uid, len(phases))))
       </script>
      </x>
     </x>''')

    def __init__(self, name, obj):
        self.name = name
        self.obj = obj
        # The list of names of pages in this phase
        self.pages = []
        # The list of hidden pages in this phase
        self.hiddenPages = []
        # The dict below stores info about every page listed in self.pages.
        self.pagesInfo = {}
        self.totalNbOfPhases = None
        # The following attributes allows to browse, from a given page, to the
        # last page of the previous phase and to the first page of the following
        # phase if allowed by phase state.
        self.previousPhase = None
        self.nextPhase = None

    def addPageLinks(self, field, obj):
        '''If p_field is a navigable Ref, we must add, within self.pagesInfo,
           objects linked to p_obj through this Ref as links.'''
        if field.page.name in self.hiddenPages: return
        infos = []
        for ztied in field.getValue(obj, appy=False):
            infos.append(Object(title=ztied.title, url=ztied.absolute_url()))
        self.pagesInfo[field.page.name].links = infos

    def addPage(self, field, obj, layoutType):
        '''Adds page-related information in the phase.'''
        # If the page is already there, we have nothing more to do.
        if (field.page.name in self.pages) or \
           (field.page.name in self.hiddenPages): return
        # Add the page only if it must be shown.
        showOnView = field.page.isShowable(obj, 'view')
        showOnEdit = field.page.isShowable(obj, 'edit')
        if showOnView or showOnEdit:
            # The page must be added
            self.pages.append(field.page.name)
            # Create the dict about page information and add it in self.pageInfo
            pageInfo = Object(page=field.page, showOnView=showOnView,
                              showOnEdit=showOnEdit, links=None)
            pageInfo.update(field.page.getInfo(obj, layoutType))
            self.pagesInfo[field.page.name] = pageInfo
        else:
            self.hiddenPages.append(field.page.name)

    def computeNextPrevious(self, allPhases):
        '''This method also fills fields "previousPhase" and "nextPhase"
           if relevant, based on list of p_allPhases.'''
        # Identify previous and next phases
        for phase in allPhases:
            if phase.name == self.name:
                i = allPhases.index(phase)
                if i > 0:
                    self.previousPhase = allPhases[i-1]
                if i < (len(allPhases)-1):
                    self.nextPhase = allPhases[i+1]

    def getPreviousPage(self, page):
        '''Returns the page that precedes p_page in this phase.'''
        try:
            pageIndex = self.pages.index(page)
        except ValueError:
            # The current page is probably not visible anymore. Return the
            # first available page in current phase.
            res = self.pages[0]
            return res, self.pagesInfo[res]
        if pageIndex > 0:
            # We stay on the same phase, previous page
            res = self.pages[pageIndex-1]
            return res, self.pagesInfo[res]
        else:
            if self.previousPhase:
                # We go to the last page of previous phase
                previousPhase = self.previousPhase
                res = previousPhase.pages[-1]
                return res, previousPhase.pagesInfo[res]
            else:
                return None, None

    def getNextPage(self, page):
        '''Returns the page that follows p_page in this phase.'''
        try:
            pageIndex = self.pages.index(page)
        except ValueError:
            # The current page is probably not visible anymore. Return the
            # first available page in current phase.
            res = self.pages[0]
            return res, self.pagesInfo[res]
        if pageIndex < (len(self.pages)-1):
            # We stay on the same phase, next page
            res = self.pages[pageIndex+1]
            return res, self.pagesInfo[res]
        else:
            if self.nextPhase:
                # We go to the first page of next phase
                nextPhase = self.nextPhase
                res = nextPhase.pages[0]
                return res, nextPhase.pagesInfo[res]
            else:
                return None, None

    def getPageInfo(self, page, layoutType):
        '''Return the page info corresponding to the given p_page. If this page
           cannot be shown on p_layoutType, this method returns page info about
           the first showable page on p_layoutType, or None if no page is
           showable at all.'''
        res = self.pagesInfo[page]
        showAttribute = 'showOn%s' % layoutType.capitalize()
        if getattr(res, showAttribute): return res
        # Find the first showable page in this phase on p_layoutType.
        for pageName in self.pages:
            if pageName == page: continue
            pageInfo = self.pagesInfo[pageName]
            if getattr(pageInfo, showAttribute): return pageInfo
# ------------------------------------------------------------------------------
