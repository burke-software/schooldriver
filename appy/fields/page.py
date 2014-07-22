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

# ------------------------------------------------------------------------------
class Page:
    '''Used for describing a page, its related phase, show condition, etc.'''
    subElements = ('save', 'cancel', 'previous', 'next', 'edit')
    def __init__(self, name, phase='main', show=True, showSave=True,
                 showCancel=True, showPrevious=True, showNext=True,
                 showEdit=True, label=None):
        self.name = name
        self.phase = phase
        self.show = show
        # When editing the page, must I show the "save" button?
        self.showSave = showSave
        # When editing the page, must I show the "cancel" button?
        self.showCancel = showCancel
        # When editing the page, and when a previous page exists, must I show
        # the "previous" button?
        self.showPrevious = showPrevious
        # When editing the page, and when a next page exists, must I show the
        # "next" button?
        self.showNext = showNext
        # When viewing the page, must I show the "edit" button?
        self.showEdit = showEdit
        # Instead of computing a translated label, one may give p_label, a
        # fixed label which will not be translated.
        self.label = label

    @staticmethod
    def get(pageData):
        '''Produces a Page instance from p_pageData. User-defined p_pageData
           can be:
           (a) a string containing the name of the page;
           (b) a string containing <pageName>_<phaseName>;
           (c) a Page instance.
           This method returns always a Page instance.'''
        res = pageData
        if res and isinstance(res, basestring):
            # Page data is given as a string.
            pageElems = pageData.rsplit('_', 1)
            if len(pageElems) == 1: # We have case (a)
                res = Page(pageData)
            else: # We have case (b)
                res = Page(pageData[0], phase=pageData[1])
        return res

    def isShowable(self, obj, layoutType, elem='page'):
        '''Must this page be shown for p_obj? "Show value" can be True, False
           or 'view' (page is available only in "view" mode).

           If p_elem is not "page", this method returns the fact that a
           sub-element is viewable or not (buttons "save", "cancel", etc).'''
        # Define what attribute to test for "showability".
        showAttr = 'show'
        if elem != 'page':
            showAttr = 'show%s' % elem.capitalize()
        # Get the value of the show attribute as identified above.
        show = getattr(self, showAttr)
        if callable(show):
            show = show(obj.appy())
        # Show value can be 'view', for example. Thanks to p_layoutType,
        # convert show value to a real final boolean value.
        res = show
        if res == 'view': res = layoutType == 'view'
        return res

    def getInfo(self, obj, layoutType):
        '''Gets information about this page, for p_obj, as an object.'''
        res = Object()
        for elem in Page.subElements:
            setattr(res, 'show%s' % elem.capitalize(), \
                    self.isShowable(obj, layoutType, elem=elem))
        return res

    def getLabel(self, zobj):
        '''Returns the i18n label for this page, or a fixed label if self.label
           is not empty.'''
        if self.label: return self.label
        return zobj.translate('%s_page_%s' % (zobj.meta_type, self.name))
# ------------------------------------------------------------------------------
