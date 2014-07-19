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
from appy.shared.css import parseStyleAttribute

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
        '''Checks that p_odtStyle may be used for style p_htmlStyle.'''
        if (htmlStyle in XHTML_PARAGRAPH_TAGS_NO_LISTS) and \
            (odtStyle in self.textStyles):
            raise PodError(
                HTML_PARA_ODT_TEXT % (htmlStyle, odtStyle.displayName))
        if (htmlStyle in XHTML_INNER_TAGS) and \
            (odtStyle in self.paragraphStyles):
            raise PodError(HTML_TEXT_ODT_PARA % (
                htmlStyle, odtStyle.displayName))

    def checkStylesMapping(self, stylesMapping):
        '''Checks that the given p_stylesMapping is correct, and returns the
           internal representation of it. p_stylesMapping is a dict where:
           * every key can be:
             (1) the name of a XHTML 'paragraph-like' tag (p, h1, h2...)
             (2) the name of a XHTML 'text-like' tag (span, b, i, em...)
             (3) the name of a CSS class
             (4) string 'h*'
           * every value must be:
             (a) if the key is (1), (2) or (3), value must be the display name
                 of an ODT style
             (b) if the key is (4), value must be an integer indicating how to
                 map the outline level of outlined styles (ie, for mapping XHTML
                 tag "h1" to the OD style with outline-level=2, value must be
                 integer "1". In that case, h2 will be mapped to the ODT style
                 with outline-level=3, etc.). Note that this value can also be
                 negative.
           * Some precision now about about keys. If key is (1) or (2),
             parameters can be given between square brackets. Every such
             parameter represents a CSS attribute and its value. For example, a
             key can be:
                             p[text-align=center,color=blue]

             This feature allows to map XHTML tags having different CSS
             attributes to different ODT styles.

           The method returns a dict which is the internal representation of
           the styles mapping:
           * every key can be:
             (I) the name of a XHTML tag, corresponding to (1) or (2) whose
                 potential parameters have been removed;
             (II) the name of a CSS class (=(3))
             (III) string 'h*' (=(4))
           * every value can be:
             (i) a Styles instance that was found from the specified ODT style
                 display name in p_stylesMapping, if key is (I) and if only one,
                 non-parameterized XHTML tag was defined in p_stylesMapping;
             (ii) a list of the form [ (params, Style), (params, Style),...]
                  if key is (I) and if one or more parameterized (or not) XHTML
                  tags representing the same tag were found in p_stylesMapping.
                  params, which can be None, is a dict whose pairs are of the
                  form (cssAttribute, cssValue).
             (iii) an integer value (=(b)).
        '''
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
            # Separate CSS attributes if any
            cssAttrs = None
            if '[' in xhtmlStyleName:
                xhtmlStyleName, attrs = xhtmlStyleName.split('[')
                xhtmlStyleName = xhtmlStyleName.strip()
                attrs = attrs.strip()[:-1].split(',')
                cssAttrs = {}
                for attr in attrs:
                    name, value = attr.split('=')
                    cssAttrs[name.strip()] = value.strip()
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
                # Store this style mapping in the result.
                alreadyInRes = xhtmlStyleName in res
                if cssAttrs or alreadyInRes:
                    # I must create a complex structure (ii) for this mapping.
                    if not alreadyInRes:
                        res[xhtmlStyleName] = [(cssAttrs, odtStyle)]
                    else:
                        value = res[xhtmlStyleName]
                        if not isinstance(value, list):
                            res[xhtmlStyleName] = [(cssAttrs, odtStyle), \
                                                   (None, value)]
                        else:
                            res.insert(0, (cssAttrs, odtStyle))
                else:
                    # I must create a simple structure (i) for this mapping.
                    res[xhtmlStyleName] = odtStyle
            else:
                # In this case (iii), it is the outline level, not an ODT style
                # name.
                res[xhtmlStyleName] = odtStyleName
        return res

    def styleMatch(self, attrs, matchingAttrs):
        '''p_match is a dict of attributes found on some HTML element.
           p_matchingAttrs is a dict of attributes corresponding to some style.
           This method returns True if p_attrs contains the winning (name,value)
           pairs that match those in p_matchingAttrs. Note that ALL attrs in
           p_matchingAttrs must be present in p_attrs.'''
        for name, value in matchingAttrs.iteritems():
            if name not in attrs: return
            if value != attrs[name]: return
        return True

    def getStyleFromMapping(self, elem, attrs, styles):
        '''p_styles is a Style instance or a list of (cssParams, Style) tuples.
           Depending on CSS attributes found in p_attrs, this method returns
           the relevant Style instance.'''
        if isinstance(styles, Style): return styles
        hasStyleInfo = attrs and ('style' in attrs)
        if not hasStyleInfo:
            # If I have, at the last position in p_styles, the style related to
            # no attribute at all, I return it.
            lastAttrs, lastStyle = styles[-1]
            if lastAttrs == None: return lastStyle
            else: return
        # If I am here, I have style info. Check if it corresponds to some style
        # in p_styles.
        styleInfo = parseStyleAttribute(attrs['style'], asDict=True)
        for matchingAttrs, style in styles:
            if self.styleMatch(styleInfo, matchingAttrs):
                return style

    def findStyle(self, elem, attrs, classValue, localStylesMapping):
        '''Finds the ODT style that must be applied to XHTML p_elem that has
           attrs p_attrs. In some cases, p_attrs is None; the value of the
           "class" attribute is given instead (in p_classValue).

           The global styles mapping is in self.stylesMapping; the local styles
           mapping is in p_localStylesMapping.

           Here are the places where we will search, ordered by
           priority (highest first):
           (1) local styles mapping (CSS style in "class" attr)
           (2)         "            (HTML elem)
           (3) global styles mapping (CSS style in "class" attr)
           (4)          "            (HTML elem)
           (5) ODT style that has the same name as CSS style in "class" attr
           (6) Predefined pod-specific ODT style that has the same name as
               CSS style in "class" attr
           (7) ODT style that has the same outline level as HTML elem.
        '''
        res = None
        cssStyleName = None
        if attrs and attrs.has_key('class'):
            cssStyleName = attrs['class']
        if classValue:
            cssStyleName = classValue
        # (1)
        if localStylesMapping.has_key(cssStyleName):
            res = localStylesMapping[cssStyleName]
        # (2)
        if (not res) and localStylesMapping.has_key(elem):
            styles = localStylesMapping[elem]
            res = self.getStyleFromMapping(elem, attrs, styles)
        # (3)
        if (not res) and self.stylesMapping.has_key(cssStyleName):
            res = self.stylesMapping[cssStyleName]
        # (4)
        if (not res) and self.stylesMapping.has_key(elem):
            styles = self.stylesMapping[elem]
            res = self.getStyleFromMapping(elem, attrs, styles)
        # (5)
        if (not res) and self.styles.has_key(cssStyleName):
            res = self.styles[cssStyleName]
        # (6)
        if (not res) and self.podSpecificStyles.has_key(cssStyleName):
            res = self.podSpecificStyles[cssStyleName]
        # (7)
        if not res:
            # Try to find a style with the correct outline level
            if elem in XHTML_HEADINGS:
                # Is there a delta that must be taken into account ?
                outlineDelta = 0
                if localStylesMapping.has_key('h*'):
                    outlineDelta += localStylesMapping['h*']
                elif self.stylesMapping.has_key('h*'):
                    outlineDelta += self.stylesMapping['h*']
                outlineLevel = int(elem[1]) + outlineDelta
                # Normalize the outline level
                if outlineLevel < 1: outlineLevel = 1
                res = self.styles.getParagraphStyleAtLevel(outlineLevel)
        if res:
            self.checkStylesAdequation(elem, res)
        return res
# ------------------------------------------------------------------------------
