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
import copy, types, re
from appy.gen.layout import Table, defaultFieldLayouts
from appy.gen import utils as gutils
from appy.shared import utils as sutils

# ------------------------------------------------------------------------------
nullValues = (None, '', [])
validatorTypes = (types.FunctionType, types.UnboundMethodType,
                  type(re.compile('')))
labelTypes = ('label', 'descr', 'help')

def initMasterValue(v):
    '''Standardizes p_v as a list of strings.'''
    if not isinstance(v, bool) and not v: res = []
    elif type(v) not in sutils.sequenceTypes: res = [v]
    else: res = v
    return [str(v) for v in res]

class No:
    '''When you write a workflow condition method and you want to return False
       but you want to give to the user some explanations about why a transition
       can't be triggered, do not return False, return an instance of No
       instead. When creating such an instance, you can specify an error
       message.'''
    def __init__(self, msg):
        self.msg = msg
    def __nonzero__(self):
        return False

# ------------------------------------------------------------------------------
# Page. Every field lives into a Page.
# ------------------------------------------------------------------------------
class Page:
    '''Used for describing a page, its related phase, show condition, etc.'''
    subElements = ('save', 'cancel', 'previous', 'next', 'edit')
    def __init__(self, name, phase='main', show=True, showSave=True,
                 showCancel=True, showPrevious=True, showNext=True,
                 showEdit=True):
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
        '''Gets information about this page, for p_obj, as a dict.'''
        res = {}
        for elem in Page.subElements:
            res['show%s' % elem.capitalize()] = self.isShowable(obj, layoutType,
                                                                elem=elem)
        return res

# ------------------------------------------------------------------------------
# Group. Fields can be grouped.
# ------------------------------------------------------------------------------
class Group:
    '''Used for describing a group of widgets within a page.'''
    def __init__(self, name, columns=['100%'], wide=True, style='section2',
                 hasLabel=True, hasDescr=False, hasHelp=False,
                 hasHeaders=False, group=None, colspan=1, align='center',
                 valign='top', css_class='', master=None, masterValue=None,
                 cellpadding=1, cellspacing=1, cellgap='0.6em', label=None,
                 translated=None):
        self.name = name
        # In its simpler form, field "columns" below can hold a list or tuple
        # of column widths expressed as strings, that will be given as is in
        # the "width" attributes of the corresponding "td" tags. Instead of
        # strings, within this list or tuple, you may give Column instances
        # (see below).
        self.columns = columns
        self._setColumns()
        # If field "wide" below is True, the HTML table corresponding to this
        # group will have width 100%. You can also specify some string value,
        # which will be used for HTML param "width".
        if wide == True:
            self.wide = '100%'
        elif isinstance(wide, basestring):
            self.wide = wide
        else:
            self.wide = ''
        # If style = 'fieldset', all widgets within the group will be rendered
        # within an HTML fieldset. If style is 'section1' or 'section2', widgets
        # will be rendered after the group title.
        self.style = style
        # If hasLabel is True, the group will have a name and the corresponding
        # i18n label will be generated.
        self.hasLabel = hasLabel
        # If hasDescr is True, the group will have a description and the
        # corresponding i18n label will be generated.
        self.hasDescr = hasDescr
        # If hasHelp is True, the group will have a help text associated and the
        # corresponding i18n label will be generated.
        self.hasHelp = hasHelp
        # If hasheaders is True, group content will begin with a row of headers,
        # and a i18n label will be generated for every header.
        self.hasHeaders = hasHeaders
        self.nbOfHeaders = len(columns)
        # If this group is himself contained in another group, the following
        # attribute is filled.
        self.group = Group.get(group)
        # If the group is rendered into another group, we can specify the number
        # of columns that this group will span.
        self.colspan = colspan
        self.align = align
        self.valign = valign
        self.cellpadding = cellpadding
        self.cellspacing = cellspacing
        # Beyond standard cellpadding and cellspacing, cellgap can define an
        # additional horizontal gap between cells in a row. So this value does
        # not add space before the first cell or after the last one.
        self.cellgap = cellgap
        if style == 'tabs':
            # Group content will be rendered as tabs. In this case, some
            # param combinations have no sense.
            self.hasLabel = self.hasDescr = self.hasHelp = False
            # The rendering is forced to a single column
            self.columns = self.columns[:1]
            # Header labels will be used as labels for the tabs.
            self.hasHeaders = True
        self.css_class = css_class
        self.master = master
        self.masterValue = initMasterValue(masterValue)
        if master: master.slaves.append(self)
        self.label = label # See similar attr of Type class.
        # If a translated name is already given here, we will use it instead of
        # trying to translate the group label.
        self.translated = translated

    def _setColumns(self):
        '''Standardizes field "columns" as a list of Column instances. Indeed,
           the initial value for field "columns" may be a list or tuple of
           Column instances or strings.'''
        for i in range(len(self.columns)):
            columnData = self.columns[i]
            if not isinstance(columnData, Column):
                self.columns[i] = Column(self.columns[i])

    @staticmethod
    def get(groupData):
        '''Produces a Group instance from p_groupData. User-defined p_groupData
           can be a string or a Group instance; this method returns always a
           Group instance.'''
        res = groupData
        if res and isinstance(res, basestring):
            # Group data is given as a string. 2 more possibilities:
            # (a) groupData is simply the name of the group;
            # (b) groupData is of the form <groupName>_<numberOfColumns>.
            groupElems = groupData.rsplit('_', 1)
            if len(groupElems) == 1:
                res = Group(groupElems[0])
            else:
                try:
                    nbOfColumns = int(groupElems[1])
                except ValueError:
                    nbOfColumns = 1
                width = 100.0 / nbOfColumns
                res = Group(groupElems[0], ['%.2f%%' % width] * nbOfColumns)
        return res

    def getMasterData(self):
        '''Gets the master of this group (and masterValue) or, recursively, of
           containing groups when relevant.'''
        if self.master: return (self.master, self.masterValue)
        if self.group: return self.group.getMasterData()

    def generateLabels(self, messages, classDescr, walkedGroups,
                       forSearch=False):
        '''This method allows to generate all the needed i18n labels related to
           this group. p_messages is the list of i18n p_messages (a PoMessages
           instance) that we are currently building; p_classDescr is the
           descriptor of the class where this group is defined. If p_forSearch
           is True, this group is used for grouping searches, and not fields.'''
        # A part of the group label depends on p_forSearch.
        if forSearch: gp = 'searchgroup'
        else:         gp = 'group'
        if self.hasLabel:
            msgId = '%s_%s_%s' % (classDescr.name, gp, self.name)
            messages.append(msgId, self.name)
        if self.hasDescr:
            msgId = '%s_%s_%s_descr' % (classDescr.name, gp, self.name)
            messages.append(msgId, ' ', nice=False)
        if self.hasHelp:
            msgId = '%s_%s_%s_help' % (classDescr.name, gp, self.name)
            messages.append(msgId, ' ', nice=False)
        if self.hasHeaders:
            for i in range(self.nbOfHeaders):
                msgId = '%s_%s_%s_col%d' % (classDescr.name, gp, self.name, i+1)
                messages.append(msgId, ' ', nice=False)
        walkedGroups.add(self)
        if self.group and (self.group not in walkedGroups) and \
           not self.group.label:
            # We remember walked groups for avoiding infinite recursion.
            self.group.generateLabels(messages, classDescr, walkedGroups,
                                      forSearch=forSearch)

    def insertInto(self, widgets, groupDescrs, page, metaType, forSearch=False):
        '''Inserts the GroupDescr instance corresponding to this Group instance
           into p_widgets, the recursive structure used for displaying all
           widgets in a given p_page (or all searches), and returns this
           GroupDescr instance.'''
        # First, create the corresponding GroupDescr if not already in
        # p_groupDescrs.
        if self.name not in groupDescrs:
            groupDescr = groupDescrs[self.name] = gutils.GroupDescr(\
                self, page, metaType, forSearch=forSearch).get()
            # Insert the group at the higher level (ie, directly in p_widgets)
            # if the group is not itself in a group.
            if not self.group:
                widgets.append(groupDescr)
            else:
                outerGroupDescr = self.group.insertInto(widgets, groupDescrs,
                                            page, metaType, forSearch=forSearch)
                gutils.GroupDescr.addWidget(outerGroupDescr, groupDescr)
        else:
            groupDescr = groupDescrs[self.name]
        return groupDescr

class Column:
    '''Used for describing a column within a Group like defined above.'''
    def __init__(self, width, align="left"):
        self.width = width
        self.align = align

# ------------------------------------------------------------------------------
# Abstract base class for every field.
# ------------------------------------------------------------------------------
class Field:
    '''Basic abstract class for defining any field.'''
    # Those attributes can be overridden by subclasses for defining,
    # respectively, names of CSS and Javascript files that are required by this
    # field, keyed by layoutType.
    cssFiles = {}
    jsFiles = {}
    dLayouts = 'lrv-d-f'

    def __init__(self, validator, multiplicity, default, show, page, group,
                 layouts, move, indexed, searchable, specificReadPermission,
                 specificWritePermission, width, height, maxChars, colspan,
                 master, masterValue, focus, historized, sync, mapping, label,
                 sdefault, scolspan, swidth, sheight):
        # The validator restricts which values may be defined. It can be an
        # interval (1,None), a list of string values ['choice1', 'choice2'],
        # a regular expression, a custom function, a Selection instance, etc.
        self.validator = validator
        # Multiplicity is a 2-tuple indicating the minimum and maximum
        # occurrences of values.
        self.multiplicity = multiplicity
        # Is the field required or not ? (derived from multiplicity)
        self.required = self.multiplicity[0] > 0
        # Default value
        self.default = default
        # Must the field be visible or not?
        self.show = show
        # When displaying/editing the whole object, on what page and phase must
        # this field value appear?
        self.page = Page.get(page)
        self.pageName = self.page.name
        # Within self.page, in what group of fields must this one appear?
        self.group = Group.get(group)
        # The following attribute allows to move a field back to a previous
        # position (useful for moving fields above predefined ones).
        self.move = move
        # If indexed is True, a database index will be set on the field for
        # fast access.
        self.indexed = indexed
        # If specified "searchable", the field will be added to some global
        # index allowing to perform application-wide, keyword searches.
        self.searchable = searchable
        # Normally, permissions to read or write every attribute in a type are
        # granted if the user has the global permission to read or
        # edit instances of the whole type. If you want a given attribute
        # to be protected by specific permissions, set one or the 2 next boolean
        # values to "True". In this case, you will create a new "field-only"
        # read and/or write permission. If you need to protect several fields
        # with the same read/write permission, you can avoid defining one
        # specific permission for every field by specifying a "named"
        # permission (string) instead of assigning "True" to the following
        # arg(s). A named permission will be global to your whole Zope site, so
        # take care to the naming convention. Typically, a named permission is
        # of the form: "<yourAppName>: Write|Read ---". If, for example, I want
        # to define, for my application "MedicalFolder" a specific permission
        # for a bunch of fields that can only be modified by a doctor, I can
        # define a permission "MedicalFolder: Write medical information" and
        # assign it to the "specificWritePermission" of every impacted field.
        self.specificReadPermission = specificReadPermission
        self.specificWritePermission = specificWritePermission
        # Widget width and height
        self.width = width
        self.height = height
        # While width and height refer to widget dimensions, maxChars hereafter
        # represents the maximum number of chars that a given input field may
        # accept (corresponds to HTML "maxlength" property). "None" means
        # "unlimited".
        self.maxChars = maxChars or ''
        # If the widget is in a group with multiple columns, the following
        # attribute specifies on how many columns to span the widget.
        self.colspan = colspan
        # The list of slaves of this field, if it is a master
        self.slaves = []
        # The behaviour of this field may depend on another, "master" field
        self.master = master
        if master: self.master.slaves.append(self)
        # When master has some value(s), there is impact on this field.
        self.masterValue = initMasterValue(masterValue)
        # If a field must retain attention in a particular way, set focus=True.
        # It will be rendered in a special way.
        self.focus = focus
        # If we must keep track of changes performed on a field, "historized"
        # must be set to True.
        self.historized = historized
        # self.sync below determines if the field representations will be
        # retrieved in a synchronous way by the browser or not (Ajax).
        self.sync = self.formatSync(sync)
        # Mapping is a dict of contexts that, if specified, are given when
        # translating the label, descr or help related to this field.
        self.mapping = self.formatMapping(mapping)
        self.id = id(self)
        self.type = self.__class__.__name__
        self.pythonType = None # The True corresponding Python type
        # Get the layouts. Consult layout.py for more info about layouts.
        self.layouts = self.formatLayouts(layouts)
        # Can we filter this field?
        self.filterable = False
        # Can this field have values that can be edited and validated?
        self.validable = True
        # The base label for translations is normally generated automatically.
        # It is made of 2 parts: the prefix, based on class name, and the name,
        # which is the field name by default. You can change this by specifying
        # a value for param "label". If this value is a string, it will be
        # understood as a new prefix. If it is a tuple, it will represent the
        # prefix and another name. If you want to specify a new name only, and
        # not a prefix, write (None, newName).
        self.label = label
        # When you specify a default value "for search" (= "sdefault"), on a
        # search screen, in the search field corresponding to this field, this
        # default value will be present.
        self.sdefault = sdefault
        # Colspan for rendering the search widget corresponding to this field.
        self.scolspan = scolspan
        # Width and height for the search widget
        self.swidth = swidth or width
        self.sheight = sheight or height

    def init(self, name, klass, appName):
        '''When the application server starts, this secondary constructor is
           called for storing the name of the Appy field (p_name) and other
           attributes that are based on the name of the Appy p_klass, and the
           application name (p_appName).'''
        if hasattr(self, 'name'): return # Already initialized
        self.name = name
        # Determine prefix for this class
        if not klass: prefix = appName
        else:         prefix = gutils.getClassName(klass, appName)
        # Recompute the ID (and derived attributes) that may have changed if
        # we are in debug mode (because we recreate new Field instances).
        self.id = id(self)
        # Remember master name on every slave
        for slave in self.slaves: slave.masterName = name
        # Determine ids of i18n labels for this field
        labelName = name
        trPrefix = None
        if self.label:
            if isinstance(self.label, basestring): trPrefix = self.label
            else: # It is a tuple (trPrefix, name)
                if self.label[1]: labelName = self.label[1]
                if self.label[0]: trPrefix = self.label[0]
        if not trPrefix:
            trPrefix = prefix
        # Determine name to use for i18n
        self.labelId = '%s_%s' % (trPrefix, labelName)
        self.descrId = self.labelId + '_descr'
        self.helpId  = self.labelId + '_help'
        # Determine read and write permissions for this field
        rp = self.specificReadPermission
        if rp and not isinstance(rp, basestring):
            self.readPermission = '%s: Read %s %s' % (appName, prefix, name)
        elif rp and isinstance(rp, basestring):
            self.readPermission = rp
        else:
            self.readPermission = 'View'
        wp = self.specificWritePermission
        if wp and not isinstance(wp, basestring):
            self.writePermission = '%s: Write %s %s' % (appName, prefix, name)
        elif wp and isinstance(wp, basestring):
            self.writePermission = wp
        else:
            self.writePermission = 'Modify portal content'
        if (self.type == 'Ref') and not self.isBack:
            # We must initialise the corresponding back reference
            self.back.klass = klass
            self.back.init(self.back.attribute, self.klass, appName)
        if self.type == "List":
            for subName, subField in self.fields:
                fullName = '%s_%s' % (name, subName)
                subField.init(fullName, klass, appName)
                subField.name = '%s*%s' % (name, subName)

    def reload(self, klass, obj):
        '''In debug mode, we want to reload layouts without restarting Zope.
           So this method will prepare a "new", reloaded version of p_self,
           that corresponds to p_self after a "reload" of its containing Python
           module has been performed.'''
        res = getattr(klass, self.name, None)
        if not res: return self
        if (self.type == 'Ref') and self.isBack: return self
        res.init(self.name, klass, obj.getProductConfig().PROJECTNAME)
        return res

    def isMultiValued(self):
        '''Does this type definition allow to define multiple values?'''
        res = False
        maxOccurs = self.multiplicity[1]
        if (maxOccurs == None) or (maxOccurs > 1):
            res = True
        return res

    def isSortable(self, usage):
        '''Can fields of this type be used for sorting purposes (when sorting
           search results (p_usage="search") or when sorting reference fields
           (p_usage="ref")?'''
        if usage == 'search':
            return self.indexed and not self.isMultiValued() and not \
                   ((self.type == 'String') and self.isSelection())
        elif usage == 'ref':
            return self.type in ('Integer', 'Float', 'Boolean', 'Date') or \
                   ((self.type == 'String') and (self.format == 0))

    def isShowable(self, obj, layoutType):
        '''When displaying p_obj on a given p_layoutType, must we show this
           field?'''
        # Check if the user has the permission to view or edit the field
        if layoutType == 'edit': perm = self.writePermission
        else:                    perm = self.readPermission
        if not obj.allows(perm): return False
        # Evaluate self.show
        if callable(self.show):
            res = self.callMethod(obj, self.show)
        else:
            res = self.show
        # Take into account possible values 'view', 'edit', 'result'...
        if type(res) in sutils.sequenceTypes:
            for r in res:
                if r == layoutType: return True
            return False
        elif res in ('view', 'edit', 'result'):
            return res == layoutType
        return bool(res)

    def isClientVisible(self, obj):
        '''This method returns True if this field is visible according to
           master/slave relationships.'''
        masterData = self.getMasterData()
        if not masterData: return True
        else:
            master, masterValue = masterData
            reqValue = master.getRequestValue(obj.REQUEST)
            # reqValue can be a list or not
            if type(reqValue) not in sutils.sequenceTypes:
                return reqValue in masterValue
            else:
                for m in masterValue:
                    for r in reqValue:
                        if m == r: return True

    def formatSync(self, sync):
        '''Creates a dictionary indicating, for every layout type, if the field
           value must be retrieved synchronously or not.'''
        if isinstance(sync, bool):
            sync = {'edit': sync, 'view': sync, 'cell': sync}
        for layoutType in ('edit', 'view', 'cell'):
            if layoutType not in sync:
                sync[layoutType] = False
        return sync

    def formatMapping(self, mapping):
        '''Creates a dict of mappings, one entry by label type (label, descr,
           help).'''
        if isinstance(mapping, dict):
            # Is it a dict like {'label':..., 'descr':...}, or is it directly a
            # dict with a mapping?
            for k, v in mapping.iteritems():
                if (k not in labelTypes) or isinstance(v, basestring):
                    # It is already a mapping
                    return {'label':mapping, 'descr':mapping, 'help':mapping}
            # If we are here, we have {'label':..., 'descr':...}. Complete
            # it if necessary.
            for labelType in labelTypes:
                if labelType not in mapping:
                    mapping[labelType] = None # No mapping for this value.
            return mapping
        else:
            # Mapping is a method that must be applied to any i18n message.
            return {'label':mapping, 'descr':mapping, 'help':mapping}

    def formatLayouts(self, layouts):
        '''Standardizes the given p_layouts. .'''
        # First, get the layouts as a dictionary, if p_layouts is None or
        # expressed as a simple string.
        areDefault = False
        if not layouts:
            # Get the default layouts as defined by the subclass
            areDefault = True
            layouts = self.computeDefaultLayouts()
        else:
            if isinstance(layouts, basestring):
                # The user specified a single layoutString (the "edit" one)
                layouts = {'edit': layouts}
            elif isinstance(layouts, Table):
                # Idem, but with a Table instance
                layouts = {'edit': Table(other=layouts)}
            else:
                # Here, we make a copy of the layouts, because every layout can
                # be different, even if the user decides to reuse one from one
                # field to another. This is because we modify every layout for
                # adding master/slave-related info, focus-related info, etc,
                # which can be different from one field to the other.
                layouts = copy.deepcopy(layouts)
                if 'edit' not in layouts:
                    defEditLayout = self.computeDefaultLayouts()
                    if type(defEditLayout) == dict:
                        defEditLayout = defEditLayout['edit']
                    layouts['edit'] = defEditLayout
        # We have now a dict of layouts in p_layouts. Ensure now that a Table
        # instance is created for every layout (=value from the dict). Indeed,
        # a layout could have been expressed as a simple layout string.
        for layoutType in layouts.iterkeys():
            if isinstance(layouts[layoutType], basestring):
                layouts[layoutType] = Table(layouts[layoutType])
        # Derive "view" and "cell" layouts from the "edit" layout when relevant
        if 'view' not in layouts:
            layouts['view'] = Table(other=layouts['edit'], derivedType='view')
        # Create the "cell" layout from the 'view' layout if not specified.
        if 'cell' not in layouts:
            layouts['cell'] = Table(other=layouts['view'], derivedType='cell')
        # Put the required CSS classes in the layouts
        layouts['cell'].addCssClasses('noStyle')
        if self.focus:
            # We need to make it flashy
            layouts['view'].addCssClasses('focus')
            layouts['edit'].addCssClasses('focus')
        # If layouts are the default ones, set width=None instead of width=100%
        # for the field if it is not in a group (excepted for rich texts).
        if areDefault and not self.group and \
           not ((self.type == 'String') and (self.format == self.XHTML)):
            for layoutType in layouts.iterkeys():
                layouts[layoutType].width = ''
        # Remove letters "r" from the layouts if the field is not required.
        if not self.required:
            for layoutType in layouts.iterkeys():
                layouts[layoutType].removeElement('r')
        # Derive some boolean values from the layouts.
        self.hasLabel = self.hasLayoutElement('l', layouts)
        self.hasDescr = self.hasLayoutElement('d', layouts)
        self.hasHelp  = self.hasLayoutElement('h', layouts)
        # Store Table instance's dicts instead of instances: this way, they can
        # be manipulated in ZPTs.
        for layoutType in layouts.iterkeys():
            layouts[layoutType] = layouts[layoutType].get()
        return layouts

    def hasLayoutElement(self, element, layouts):
        '''This method returns True if the given layout p_element can be found
           at least once among the various p_layouts defined for this field.'''
        for layout in layouts.itervalues():
            if element in layout.layoutString: return True
        return False

    def getDefaultLayouts(self):
        '''Any subclass can define this for getting a specific set of
           default layouts. If None is returned, a global set of default layouts
           will be used.'''

    def getInputLayouts(self):
        '''Gets, as a string, the layouts as could have been specified as input
           value for the Field constructor.'''
        res = '{'
        for k, v in self.layouts.iteritems():
            res += '"%s":"%s",' % (k, v['layoutString'])
        res += '}'
        return res

    def computeDefaultLayouts(self):
        '''This method gets the default layouts from an Appy type, or a copy
           from the global default field layouts when they are not available.'''
        res = self.getDefaultLayouts()
        if not res:
            # Get the global default layouts
            res = copy.deepcopy(defaultFieldLayouts)
        return res

    def getCss(self, layoutType, res):
        '''This method completes the list p_res with the names of CSS files
           that are required for displaying widgets of self's type on a given
           p_layoutType. p_res is not a set because order of inclusion of CSS
           files may be important and may be loosed by using sets.'''
        if layoutType in self.cssFiles:
            for fileName in self.cssFiles[layoutType]:
                if fileName not in res:
                    res.append(fileName)

    def getJs(self, layoutType, res):
        '''This method completes the list p_res with the names of Javascript
           files that are required for displaying widgets of self's type on a
           given p_layoutType. p_res is not a set because order of inclusion of
           CSS files may be important and may be loosed by using sets.'''
        if layoutType in self.jsFiles:
            for fileName in self.jsFiles[layoutType]:
                if fileName not in res:
                    res.append(fileName)

    def getValue(self, obj):
        '''Gets, on_obj, the value conforming to self's type definition.'''
        value = getattr(obj.aq_base, self.name, None)
        if self.isEmptyValue(value):
            # If there is no value, get the default value if any: return
            # self.default, of self.default() if it is a method.
            if callable(self.default):
                try:
                    return self.callMethod(obj, self.default)
                except Exception, e:
                    # Already logged. Here I do not raise the exception,
                    # because it can be raised as the result of reindexing
                    # the object in situations that are not foreseen by
                    # method in self.default.
                    return
            else:
                return self.default
        return value

    def getFormattedValue(self, obj, value, showChanges=False):
        '''p_value is a real p_obj(ect) value from a field from this type. This
           method returns a pretty, string-formatted version, for displaying
           purposes. Needs to be overridden by some child classes. If
           p_showChanges is True, the result must also include the changes that
           occurred on p_value across the ages.'''
        if self.isEmptyValue(value): return ''
        return value

    def getIndexType(self):
        '''Returns the name of the technical, Zope-level index type for this
           field.'''
        # Normally, self.indexed contains a Boolean. If a string value is given,
        # we consider it to be an index type. It allows to bypass the standard
        # way to decide what index type must be used.
        if isinstance(self.indexed, str): return self.indexed
        if self.name == 'title': return 'TextIndex'
        return 'FieldIndex'

    def getIndexValue(self, obj, forSearch=False):
        '''This method returns a version for this field value on p_obj that is
           ready for indexing purposes. Needs to be overridden by some child
           classes.

           If p_forSearch is True, it will return a "string" version of the
           index value suitable for a global search.'''
        value = self.getValue(obj)
        if forSearch and (value != None):
            if isinstance(value, unicode):
                res = value.encode('utf-8')
            elif type(value) in sutils.sequenceTypes:
                res = []
                for v in value:
                    if isinstance(v, unicode): res.append(v.encode('utf-8'))
                    else: res.append(str(v))
                res = ' '.join(res)
            else:
                res = str(value)
            return res
        return value

    def getRequestValue(self, request, requestName=None):
        '''Gets a value for this field as carried in the request object. In the
           simplest cases, the request value is a single value whose name in the
           request is the name of the field.

           Sometimes (ie: a Date: see the overriden method in the Date class),
           several request values must be combined.

           Sometimes (ie, a field which is a sub-field in a List), the name of
           the request value(s) representing the field value do not correspond
           to the field name (ie: the request name includes information about
           the container field). In this case, p_requestName must be used for
           searching into the request, instead of the field name (self.name).'''
        name = requestName or self.name
        return request.get(name, None)

    def getStorableValue(self, value):
        '''p_value is a valid value initially computed through calling
           m_getRequestValue. So, it is a valid string (or list of strings)
           representation of the field value coming from the request.
           This method computes the real (potentially converted or manipulated
           in some other way) value as can be stored in the database.'''
        if self.isEmptyValue(value): return None
        return value

    def getMasterData(self):
        '''Gets the master of this field (and masterValue) or, recursively, of
           containing groups when relevant.'''
        if self.master: return (self.master, self.masterValue)
        if self.group: return self.group.getMasterData()

    def isEmptyValue(self, value, obj=None):
        '''Returns True if the p_value must be considered as an empty value.'''
        return value in nullValues

    def validateValue(self, obj, value):
        '''This method may be overridden by child classes and will be called at
           the right moment by m_validate defined below for triggering
           type-specific validation. p_value is never empty.'''
        return None

    def securityCheck(self, obj, value):
        '''This method performs some security checks on the p_value that
           represents user input.'''
        if not isinstance(value, basestring): return
        # Search Javascript code in the value (prevent XSS attacks).
        if '<script' in value:
            obj.log('Detected Javascript in user input.', type='error')
            raise Exception('Your behaviour is considered a security ' \
                            'attack. System administrator has been warned.')

    def validate(self, obj, value):
        '''This method checks that p_value, coming from the request (p_obj is
           being created or edited) and formatted through a call to
           m_getRequestValue defined above, is valid according to this type
           definition. If it is the case, None is returned. Else, a translated
           error message is returned.'''
        # Check that a value is given if required.
        if self.isEmptyValue(value, obj):
            if self.required and self.isClientVisible(obj):
                # If the field is required, but not visible according to
                # master/slave relationships, we consider it not to be required.
                return obj.translate('field_required')
            else:
                return None
        # Perform security checks on p_value
        self.securityCheck(obj, value)
        # Triggers the sub-class-specific validation for this value
        message = self.validateValue(obj, value)
        if message: return message
        # Evaluate the custom validator if one has been specified
        value = self.getStorableValue(value)
        if self.validator and (type(self.validator) in validatorTypes):
            obj = obj.appy()
            if type(self.validator) != validatorTypes[-1]:
                # It is a custom function. Execute it.
                try:
                    validValue = self.validator(obj, value)
                    if isinstance(validValue, basestring) and validValue:
                        # Validation failed; and p_validValue contains an error
                        # message.
                        return validValue
                    else:
                        if not validValue:
                            return obj.translate('field_invalid')
                except Exception, e:
                    return str(e)
                except:
                    return obj.translate('field_invalid')
            else:
                # It is a regular expression
                if not self.validator.match(value):
                    # If the regular expression is among the default ones, we
                    # generate a specific error message.
                    if self.validator == String.EMAIL:
                        return obj.translate('bad_email')
                    elif self.validator == String.URL:
                        return obj.translate('bad_url')
                    elif self.validator == String.ALPHANUMERIC:
                        return obj.translate('bad_alphanumeric')
                    else:
                        return obj.translate('field_invalid')

    def store(self, obj, value):
        '''Stores the p_value (produced by m_getStorableValue) that complies to
           p_self type definition on p_obj.'''
        setattr(obj, self.name, value)

    def callMethod(self, obj, method, cache=True):
        '''This method is used to call a p_method on p_obj. p_method is part of
           this type definition (ie a default method, the method of a Computed
           field, a method used for showing or not a field...). Normally, those
           methods are called without any arg. But one may need, within the
           method, to access the related field. This method tries to call
           p_method with no arg *or* with the field arg.'''
        obj = obj.appy()
        try:
            return gutils.callMethod(obj, method, cache=cache)
        except TypeError, te:
            # Try a version of the method that would accept self as an
            # additional parameter. In this case, we do not try to cache the
            # value (we do not call gutils.callMethod), because the value may
            # be different depending on the parameter.
            tb = sutils.Traceback.get()
            try:
                return method(obj, self)
            except Exception, e:
                obj.log(tb, type='error')
                # Raise the initial error.
                raise te
        except Exception, e:
            obj.log(sutils.Traceback.get(), type='error')
            raise e

    def process(self, obj):
        '''This method is a general hook allowing a field to perform some
           processing after an URL on an object has been called, of the form
           <objUrl>/onProcess.'''
        return obj.goto(obj.absolute_url())
# ------------------------------------------------------------------------------
