# ------------------------------------------------------------------------------
# Appy is a framework for building applications in the Python language.
# Copyright (C) 2007 Gaetan Delannay

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,USA.

# ------------------------------------------------------------------------------
import re, os.path
from UserDict import UserDict
import appy.pod
from appy.pod import *
from appy.pod.odf_parser import OdfEnvironment, OdfParser

# Possible states for the parser
READING = 0 # Default state
PARSING_STYLE = 1 # I am parsing styles definitions

# Error-related constants ------------------------------------------------------
MAPPING_NOT_DICT = 'The styles mapping must be a dictionary or a UserDict ' \
                   'instance.'
MAPPING_ELEM_NOT_STRING = "The styles mapping dictionary's keys and values " \
                          "must be strings."
MAPPING_OUTLINE_DELTA_NOT_INT = 'When specifying "h*" as key in the styles ' \
                                'mapping, you must specify an integer as ' \
                                'value. This integer, which may be positive ' \
                                'or negative, represents a delta that will ' \
                                'be added to the html heading\'s outline ' \
                                'level for finding an ODT style with the ' \
                                'same outline level.'
MAPPING_ELEM_EMPTY = 'In your styles mapping, you inserted an empty key ' \
                     'and/or value.'
UNSTYLABLE_TAG = 'You can\'t associate a style to element "%s". Unstylable ' \
                 'elements are: %s'
STYLE_NOT_FOUND = 'OpenDocument style "%s" was not found in your template. ' \
                  'Note that the styles names ("Heading 1", "Standard"...) ' \
                  'that appear when opening your template with OpenOffice, ' \
                  'for example, are a super-set of the styles that are really '\
                  'recorded into your document. Indeed, only styles that are ' \
                  'in use within your template are actually recorded into ' \
                  'the document. You may consult the list of available ' \
                  'styles programmatically by calling your pod renderer\'s ' \
                  '"getStyles" method.'
HTML_PARA_ODT_TEXT = 'For XHTML element "%s", you must associate a ' \
                     'paragraph-wide OpenDocument style. "%s" is a "text" ' \
                     'style (that applies to only a chunk of text within a ' \
                     'paragraph).'
HTML_TEXT_ODT_PARA = 'For XHTML element "%s", you must associate an ' \
                     'OpenDocument "text" style (that applies to only a chunk '\
                     'of text within a paragraph). "%s" is a paragraph-wide ' \
                     'style.'
# ------------------------------------------------------------------------------
class Style:
    '''Represents a paragraph style as found in styles.xml in a ODT file.'''
    numberRex = re.compile('(\d+)(.*)')
    def __init__(self, name, family):
        self.name = name
        self.family = family # May be 'paragraph', etc.
        self.displayName = name
        self.styleClass = None # May be 'text', 'list', etc.
        self.fontSize = None
        self.fontSizeUnit = None # May be pt, %, ...
        self.outlineLevel = None # Were the styles lies within styles and
        # substyles hierarchy
    def setFontSize(self, fontSize):
        rexRes = self.numberRex.search(fontSize)
        self.fontSize = int(rexRes.group(1))
        self.fontSizeUnit = rexRes.group(2)
    def __repr__(self):
        res = '<Style %s|family %s' % (self.name, self.family)
        if self.displayName != None: res += '|displayName "%s"'%self.displayName
        if self.styleClass != None: res += '|class %s' % self.styleClass
        if self.fontSize != None:
            res += '|fontSize %d%s' % (self.fontSize, self.fontSizeUnit)
        if self.outlineLevel != None: res += '|level %s' % self.outlineLevel
        return ('%s>' % res).encode('utf-8')

# ------------------------------------------------------------------------------
class Styles(UserDict):
    def getParagraphStyleAtLevel(self, level):
        '''Tries to find a style which has level p_level. Returns None if no
           such style exists.'''
        res = None
        for style in self.itervalues():
            if (style.family == 'paragraph') and (style.outlineLevel == level):
                res = style
                break
        return res
    def getStyle(self, displayName):
        '''Gets the style that has this p_displayName. Returns None if not
           found.'''
        res = None
        for style in self.itervalues():
            if style.displayName == displayName:
                res = style
                break
        return res
    def getStyles(self, stylesType='all'):
        '''Returns a list of all the styles of the given p_stylesType.'''
        res = []
        if stylesType == 'all':
            res = self.values()
        else:
            for style in self.itervalues():
                if (style.family == stylesType) and style.displayName:
                    res.append(style)
        return res

# ------------------------------------------------------------------------------
class StylesEnvironment(OdfEnvironment):
    def __init__(self):
        OdfEnvironment.__init__(self)
        self.styles = Styles()
        self.state = READING
        self.currentStyle = None # The style definition currently parsed

# ------------------------------------------------------------------------------
class StylesParser(OdfParser):
    def __init__(self, env, caller):
        OdfParser.__init__(self, env, caller)
        self.styleTag = None
    def endDocument(self):
        e = OdfParser.endDocument(self)
        self.caller.styles = e.styles
    def startElement(self, elem, attrs):
        e = OdfParser.startElement(self, elem, attrs)
        self.styleTag = '%s:style' % e.ns(e.NS_STYLE)
        if elem == self.styleTag:
            e.state = PARSING_STYLE
            nameAttr = '%s:name' % e.ns(e.NS_STYLE)
            familyAttr = '%s:family' % e.ns(e.NS_STYLE)
            classAttr = '%s:class' % e.ns(e.NS_STYLE)
            displayNameAttr = '%s:display-name' % e.ns(e.NS_STYLE)
            # Create the style
            style = Style(name=attrs[nameAttr], family=attrs[familyAttr])
            if attrs.has_key(classAttr):
                style.styleClass = attrs[classAttr]
            if attrs.has_key(displayNameAttr):
                style.displayName = attrs[displayNameAttr]
            # Record this style in the environment
            e.styles[style.name] = style
            e.currentStyle = style
            levelKey = '%s:default-outline-level' % e.ns(e.NS_STYLE)
            if attrs.has_key(levelKey) and attrs[levelKey].strip():
                style.outlineLevel = int(attrs[levelKey])
        else:
            if e.state == PARSING_STYLE:
                # I am parsing tags within the style.
                if elem == ('%s:text-properties' % e.ns(e.NS_STYLE)):
                    fontSizeKey = '%s:font-size' % e.ns(e.NS_FO)
                    if attrs.has_key(fontSizeKey):
                        e.currentStyle.setFontSize(attrs[fontSizeKey])
    def endElement(self, elem):
        e = OdfParser.endElement(self, elem)
        if elem == self.styleTag:
            e.state = READING
            e.currentStyle = None

# -------------------------------------------------------------------------------
class StylesManager:
    '''Reads the paragraph styles from styles.xml within an ODT file, and
       updates styles.xml with some predefined POD styles.'''
    podSpecificStyles = {
        'podItemKeepWithNext': Style('podItemKeepWithNext', 'paragraph'),
        # This style is common to bullet and number items. Behing the scenes,
        # there are 2 concrete ODT styles: podBulletItemKeepWithNext and
        # podNumberItemKeepWithNext. pod chooses the right one.
    }
    def __init__(self, stylesString):
        self.stylesString = stylesString
        self.styles = None
        # Global styles mapping
        self.stylesMapping = None
        self.stylesParser = StylesParser(StylesEnvironment(), self)
        self.stylesParser.parse(self.stylesString)
        # Now self.styles contains the styles.
        # List of text styles derived from self.styles
        self.textStyles = self.styles.getStyles('text')
        # List of paragraph styles derived from self.styles
        self.paragraphStyles = self.styles.getStyles('paragraph')

    def checkStylesAdequation(self, htmlStyle, odtStyle):
        '''Checks that p_odtStyle my be used for style p_htmlStyle.'''
        if (htmlStyle in XHTML_PARAGRAPH_TAGS_NO_LISTS) and \
            (odtStyle in self.textStyles):
            raise PodError(
                HTML_PARA_ODT_TEXT % (htmlStyle, odtStyle.displayName))
        if (htmlStyle in XHTML_INNER_TAGS) and \
            (odtStyle in self.paragraphStyles):
            raise PodError(HTML_TEXT_ODT_PARA % (
                htmlStyle, odtStyle.displayName))

    def checkStylesMapping(self, stylesMapping):
        '''Checks that the given p_stylesMapping is correct. Returns the same
           dict as p_stylesMapping, but with Style instances as values, instead
           of strings (style's display names).'''
        res = {}
        if not isinstance(stylesMapping, dict) and \
           not isinstance(stylesMapping, UserDict):
            raise PodError(MAPPING_NOT_DICT)
        for xhtmlStyleName, odtStyleName in stylesMapping.iteritems():
            if not isinstance(xhtmlStyleName, basestring):
                raise PodError(MAPPING_ELEM_NOT_STRING)
            if (xhtmlStyleName == 'h*') and \
                not isinstance(odtStyleName, int):
                raise PodError(MAPPING_OUTLINE_DELTA_NOT_INT)
            if (xhtmlStyleName != 'h*') and \
                not isinstance(odtStyleName, basestring):
                raise PodError(MAPPING_ELEM_NOT_STRING)
            if (xhtmlStyleName != 'h*') and \
               ((not xhtmlStyleName) or (not odtStyleName)):
                raise PodError(MAPPING_ELEM_EMPTY)
            if xhtmlStyleName in XHTML_UNSTYLABLE_TAGS:
                raise PodError(UNSTYLABLE_TAG % (xhtmlStyleName,
                                                 XHTML_UNSTYLABLE_TAGS))
            if xhtmlStyleName != 'h*':
                odtStyle = self.styles.getStyle(odtStyleName)
                if not odtStyle:
                    if self.podSpecificStyles.has_key(odtStyleName):
                        odtStyle = self.podSpecificStyles[odtStyleName]
                    else:
                        raise PodError(STYLE_NOT_FOUND % odtStyleName)
                self.checkStylesAdequation(xhtmlStyleName, odtStyle)
                res[xhtmlStyleName] = odtStyle
            else:
                res[xhtmlStyleName] = odtStyleName # In this case, it is the
                # outline level, not an ODT style name
        return res
# ------------------------------------------------------------------------------
