# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Appy is a framework for building applications in the Python language.
# Copyright (C) 2007-2011 Gaetan Delannay
#
# Distributed under the GNU General Public License.
#
# Thanks to Fabio Marcuzzi and Gauthier Bastien for management of strike and
# underline.

# ------------------------------------------------------------------------------
import xml.sax, time, random
from appy.shared.xml_parser import XmlEnvironment, XmlParser, escapeXml
from appy.pod.odf_parser import OdfEnvironment
from appy.pod.styles_manager import Style
from appy.pod import *

# To which ODT tags do HTML tags correspond ?
HTML_2_ODT = {'h1':'h', 'h2':'h', 'h3':'h', 'h4':'h', 'h5':'h', 'h6':'h',
              'p':'p', 'div': 'p', 'b':'span', 'i':'span', 'strong':'span',
              'strike':'span', 'u':'span', 'em': 'span', 'sub': 'span',
              'sup': 'span', 'br': 'line-break'}
DEFAULT_ODT_STYLES = {'b': 'podBold', 'strong':'podBold', 'i': 'podItalic',
                      'u': 'podUnderline', 'strike': 'podStrike',
                      'em': 'podItalic', 'sup': 'podSup', 'sub':'podSub',
                      'td': 'podCell', 'th': 'podHeaderCell'}
INNER_TAGS = ('b', 'strong', 'i', 'u', 'em', 'sup', 'sub', 'span')
TABLE_CELL_TAGS = ('td', 'th')
OUTER_TAGS = TABLE_CELL_TAGS + ('li',)
# The following elements can't be rendered inside paragraphs
NOT_INSIDE_P = XHTML_HEADINGS + XHTML_LISTS + ('table',)
NOT_INSIDE_P_OR_P = NOT_INSIDE_P + ('p', 'div')
NOT_INSIDE_LIST = ('table',)
IGNORABLE_TAGS = ('meta', 'title', 'style')

# ------------------------------------------------------------------------------
class HtmlElement:
    '''Every time an HTML element is encountered during the SAX parsing,
       an instance of this class is pushed on the stack of currently parsed
       elements.'''
    elemTypes = {'p':'para', 'div':'para', 'li':'para', 'ol':'list',
                 'ul':'list'}
    def __init__(self, elem, attrs):
        self.elem = elem
        # Keep "class" attribute (useful for finding the corresponding ODT
        # style) in some cases. Normally, basic XmlElement class stores attrs,
        # but for a strange reason those attrs are back to None (probably for
        # performance reasons they become inaccessible after a while).
        self.classAttr = None
        if attrs.has_key('class'):
            self.classAttr = attrs['class']
        self.tagsToReopen = [] # When the HTML element corresponding to self
        # is completely dumped, if there was a problem related to tags
        # inclusion, we may need to dump start tags corresponding to
        # tags that we had to close before dumping this element. This list
        # contains HtmlElement instances.
        self.tagsToClose = [] # Before dumping the closing tag corresponding
        # to self, we may need to close other tags (ie closing a paragraph
        # before closing a cell). This list contains HtmlElement instances.
        self.elemType = self.elem
        if self.elemTypes.has_key(self.elem):
            self.elemType = self.elemTypes[self.elem]
        # If a conflict occurs on this element, we will note it.
        self.isConflictual = False

    def setConflictual(self):
        '''Note p_self as conflictual.'''
        self.isConflictual = True
        return self

    def getOdfTag(self, env):
        '''Gets the raw ODF tag that corresponds to me.'''
        res = ''
        if HTML_2_ODT.has_key(self.elem):
            res += '%s:%s' % (env.textNs, HTML_2_ODT[self.elem])
        elif self.elem == 'a':
            res += '%s:a' % env.textNs
        elif self.elem in XHTML_LISTS:
            res += '%s:list' % env.textNs
        elif self.elem == 'li':
            res += '%s:list-item' % env.textNs
        elif self.elem == 'table':
            res += '%s:table' % env.tableNs
        elif self.elem == 'thead':
            res += '%s:table-header-rows' % env.tableNs
        elif self.elem == 'tr':
            res += '%s:table-row' % env.tableNs
        elif self.elem in TABLE_CELL_TAGS:
            res += '%s:table-cell' % env.tableNs
        return res

    def getOdfTags(self, env):
        '''Gets the start and end tags corresponding to p_self.'''
        tag = self.getOdfTag(env)
        if not tag: return (None, None)
        return ('<%s>' % tag, '</%s>' % tag)

    def getConflictualElements(self, env):
        '''self was just parsed. In some cases, this element can't be dumped
           in the result because there are conflictual elements among previously
           parsed opening elements (p_env.currentElements). For example, if we
           just dumped a "p", we can't dump a table within the "p". Such
           constraints do not hold in XHTML code but hold in ODF code.'''
        if not env.currentElements: return ()
        parentElem = env.currentElements[-1]
        # Check elements that can't be found within a paragraph
        if (parentElem.elemType == 'para') and \
           (self.elem in NOT_INSIDE_P_OR_P):
            # Oups, li->p wrongly considered as a conflict.
            if (parentElem.elem == 'li') and (self.elem in ('p', 'div')):
                return ()
            return (parentElem.setConflictual(),)
        # Check inner paragraphs
        if (parentElem.elem in INNER_TAGS) and (self.elemType == 'para'):
            res = [parentElem.setConflictual()]
            if len(env.currentElements) > 1:
                i = 2
                visitParents = True
                while visitParents:
                    try:
                        nextParent = env.currentElements[-i]
                        i += 1
                        res.insert(0, nextParent.setConflictual())
                        if nextParent.elemType == 'para':
                            visitParents = False
                    except IndexError:
                        visitParents = False
            return res
        if parentElem.tagsToClose and \
            (parentElem.tagsToClose[-1].elemType == 'para') and \
            (self.elem in NOT_INSIDE_P):
            return (parentElem.tagsToClose[-1].setConflictual(),)
        # Check elements that can't be found within a list
        if (parentElem.elemType=='list') and (self.elem in NOT_INSIDE_LIST):
            return (parentElem.setConflictual(),)
        return ()

    def addInnerParagraph(self, env):
        '''Dump an inner paragraph inside self (if not already done).'''
        if not self.tagsToClose:
            # We did not do it yet
            env.dumpString('<%s:p' % env.textNs)
            if self.elem == 'li':
                itemStyle = env.getCurrentElement(isList=True).elem # ul or ol
                # Which 'li'-related style must I use?
                if self.classAttr:
                    odtStyle = env.parser.caller.findStyle(
                        self.elem, classValue=self.classAttr)
                    if odtStyle and (odtStyle.name == 'podItemKeepWithNext'):
                        itemStyle += '_kwn'
                    styleName = env.itemStyles[itemStyle]
                else:
                    # Check if a style must be applied on 'p' tags
                    odtStyle = env.parser.caller.findStyle('p')
                    if odtStyle:
                        styleName = odtStyle.name
                    else:
                        styleName = env.itemStyles[itemStyle]
                env.dumpString(' %s:style-name="%s"' % (env.textNs, styleName))
            else:
                # Check if a style must be applied on 'p' tags
                odtStyle = env.parser.caller.findStyle('p')
                if odtStyle:
                    env.dumpString(' %s:style-name="%s"' % (env.textNs,
                                                            odtStyle.name))
            env.dumpString('>')
            self.tagsToClose.append(HtmlElement('p', {}))

    def dump(self, start, env):
        '''Dumps the start or end (depending on p_start) tag of this HTML
           element. We must take care of potential innerTags.'''
        # Compute the tag in itself
        tag = ''
        prefix = '<'
        if not start: prefix += '/'
        # Compute tag attributes
        attrs = ''
        if start:
            if self.elemType == 'list':
                # I must specify the list style
                attrs += ' %s:style-name="%s"' % (
                    env.textNs, env.listStyles[self.elem])
                if self.elem == 'ol':
                    # I have interrupted a numbered list. I need to continue
                    # the numbering.
                    attrs += ' %s:continue-numbering="true"' % env.textNs
            else:
                attrs = env.getOdtAttributes(self)
        tag = prefix + self.getOdfTag(env) + attrs + '>'
        # Close/open subTags if any
        for subElem in self.tagsToClose:
            subTag = subElem.dump(start, env)
            if start: tag += subTag
            else: tag = subTag + tag
        return tag

    def __repr__(self):
        return '<Html "%s">' % self.elem

# ------------------------------------------------------------------------------
class HtmlTable:
    '''Represents an HTML table, and also a sub-buffer. When parsing elements
       corresponding to an HTML table (<table>, <tr>, <td>, etc), we can't dump
       corresponding ODF elements directly into the global result buffer
       (XhtmlEnvironment.res). Indeed, when dumping an ODF table, we must
       dump columns declarations at the beginning of the table. So before
       dumping rows and cells, we must know how much columns will be present
       in the table. It means that we must first parse the first <tr> entirely
       in order to know how much columns are present in the HTML table before
       dumping the ODF table. So we use this class as a sub-buffer that will
       be constructed as we parse the HTML table; when encountering the end
       of the HTML table, we will dump the result of this sub-buffer into
       the parent buffer, which may be the global buffer or another table
       buffer.'''
    def __init__(self, env):
        elems = str(time.time()).split('.')
        self.name= 'AppyTable%s%s%d' % (elems[0],elems[1],random.randint(1,100))
        self.styleNs = env.ns[OdfEnvironment.NS_STYLE]
        self.res = u'' # The sub-buffer.
        self.tempRes = u'' # The temporary sub-buffer, into which we will
        # dump all table sub-elements, until we encounter the end of the first
        # row. Then, we will know how much columns are defined in the table;
        # we will dump columns declarations into self.res and dump self.tempRes
        # into self.res.
        self.firstRowParsed = False # Was the first table row completely parsed?
        self.nbOfColumns = 0
        # Are we currently within a table cell? Instead of a boolean, the field
        # stores an integer. The integer is > 1 if the cell spans more than one
        # column.
        self.inCell = 0
        # The index, within the current row, of the current cell
        self.cellIndex = -1
        # The size of the content of the currently parsed table cell
        self.cellContentSize = 0
        # The following list stores, for every column, the size of the biggest
        # content of all its cells.
        self.columnContentSizes = []
        # The following list stores, for every column, its width, if specified.
        # If widths are found, self.columnContentSizes will not be used:
        # self.columnWidths will be used instead.
        self.columnWidths = []

    def computeColumnStyles(self, renderer):
        '''Once the table has been completely parsed, self.columnContentSizes
           should be correctly filled. Based on this, we can deduce the width
           of every column and create the corresponding style declarations, in
           p_renderer.dynamicStyles.'''
        total = 65000.0 # A number representing the total width of the table
        # Use (a) self.columnWidths if complete, or
        #     (b) self.columnContentSizes if complete, or
        #     (c) a fixed width else.
        if self.columnWidths and (len(self.columnWidths) == self.nbOfColumns) \
           and (None not in self.columnWidths):
            # Use self.columnWidths
            toUse = self.columnWidths
        # Use self.columnContentSizes if complete
        elif (len(self.columnContentSizes) == self.nbOfColumns) and \
           (None not in self.columnContentSizes):
            # Use self.columnContentSizes
            toUse = self.columnContentSizes
        else:
            toUse = None
        if toUse:
            widths = []
            # Compute the sum of all column content sizes
            contentTotal = 0
            for size in toUse: contentTotal += size
            contentTotal = float(contentTotal)
            for size in toUse:
                width = int((size/contentTotal) * total)
                widths.append(width)
        else:
            # There was a problem while parsing the table. Set every column
            # with the same width.
            widths = [int(total/self.nbOfColumns)] * self.nbOfColumns
        # Compute style declaration corresponding to every column.
        s = self.styleNs
        i = 0
        for width in widths:
            i += 1
            # Compute the width of this column, relative to "total".
            decl = '<%s:style %s:name="%s.%d" %s:family="table-column">' \
                   '<%s:table-column-properties %s:rel-column-width="%d*"' \
                   '/></%s:style>' % (s, s, self.name, i, s, s, s, width, s)
            renderer.dynamicStyles.append(decl.encode('utf-8'))

# ------------------------------------------------------------------------------
class XhtmlEnvironment(XmlEnvironment):
    itemStyles = {'ul': 'podBulletItem', 'ol': 'podNumberItem',
                  'ul_kwn': 'podBulletItemKeepWithNext',
                  'ol_kwn': 'podNumberItemKeepWithNext'}
    listStyles = {'ul': 'podBulletedList', 'ol': 'podNumberedList'}
    def __init__(self, renderer):
        XmlEnvironment.__init__(self)
        self.renderer = renderer
        self.ns = renderer.currentParser.env.namespaces
        self.res = u''
        self.currentContent = u''
        self.currentElements = [] # Stack of currently walked elements
        self.currentLists = [] # Stack of currently walked lists (ul or ol)
        self.currentTables = [] # Stack of currently walked tables
        self.textNs = self.ns[OdfEnvironment.NS_TEXT]
        self.linkNs = self.ns[OdfEnvironment.NS_XLINK]
        self.tableNs = self.ns[OdfEnvironment.NS_TABLE]
        # The following attr will be True when parsing parts of the XHTML that
        # must be ignored.
        self.ignore = False

    def getCurrentElement(self, isList=False):
        '''Gets the element that is on the top of self.currentElements or
           self.currentLists.'''
        res = None
        if isList:
            elements = self.currentLists # Stack of list elements only
        else:
            elements = self.currentElements # Stack of all elements (including
            # elements also pushed on other stacks, like lists and tables).
        if elements:
            res = elements[-1]
        return res

    def anElementIsMissing(self, previousElem, currentElem):
        res = False
        if previousElem and (previousElem.elem in OUTER_TAGS) and \
           ((not currentElem) or (currentElem.elem in INNER_TAGS)):
            res = True
        return res

    def dumpCurrentContent(self):
        '''Dumps content that was temporarily stored in self.currentContent
           into the result.'''
        contentSize = 0
        if self.currentContent.strip(' \n\r\t'): # NBSP must not be in this list
            # Manage missing elements
            currentElem = self.getCurrentElement()
            if self.anElementIsMissing(currentElem, None):
                currentElem.addInnerParagraph(self)
            # Dump and reinitialize the current content
            content = self.currentContent.strip('\n\t')
            # We remove leading and trailing carriage returns, but not
            # whitespace because whitespace may be part of the text to dump.
            contentSize = len(content)
            # We do not escape carriage returns, because, in XHTML, carriage
            # returns are just ignorable white space.
            self.dumpString(escapeXml(content))
            self.currentContent = u''
        # If we are within a table cell, update the total size of cell content.
        if self.currentTables and self.currentTables[-1].inCell:
            for table in self.currentTables:
                table.cellContentSize += contentSize

    def getOdtAttributes(self, htmlElem, htmlAttrs={}):
        '''Gets the ODT attributes to dump for p_currentElem. p_htmlAttrs are
           the parsed attributes from the XHTML p_currentElem.'''
        odtStyle = self.parser.caller.findStyle(htmlElem.elem, htmlAttrs)
        styleName = None
        if odtStyle:
            styleName = odtStyle.name
        elif DEFAULT_ODT_STYLES.has_key(htmlElem.elem):
            styleName = DEFAULT_ODT_STYLES[htmlElem.elem]
        res = ''
        if styleName:
            res += ' %s:style-name="%s"' % (self.textNs, styleName)
            if (htmlElem.elem in XHTML_HEADINGS) and \
               (odtStyle.outlineLevel != None):
                res += ' %s:outline-level="%d"' % (self.textNs, \
                                                   odtStyle.outlineLevel)
        return res

    def dumpStyledElement(self, htmlElem, odfTag, attrs):
        '''Dumps an element that potentially has associated style
           information.'''
        self.dumpString('<' + odfTag)
        self.dumpString(self.getOdtAttributes(htmlElem, attrs))
        self.dumpString('>')

    def getTags(self, elems, start=True):
        '''This method returns a series of start or end tags (depending on
           p_start) that correspond to HtmlElement instances in p_elems.'''
        res = ''
        for elem in elems:
            tag = elem.dump(start, self)
            if start: res += tag
            else: res = tag + res
        return res

    def closeConflictualElements(self, conflictElems):
        '''This method dumps end tags for p_conflictElems, excepted if those
           tags would be empty. In this latter case, tags are purely removed
           from the result.'''
        startTags = self.getTags(conflictElems, start=True)
        if self.res.endswith(startTags):
            # In this case I would dump an empty (series of) tag(s). Instead, I
            # will remove those tags.
            self.res = self.res[:-len(startTags)]
        else:
            self.dumpString(self.getTags(conflictElems, start=False))

    def dumpString(self, s):
        '''Dumps arbitrary content p_s.
           If the table stack is not empty, we must dump p_s into the buffer
           corresponding to the last parsed table. Else, we must dump p_s
           into the global buffer (self.res).'''
        if self.currentTables:
            currentTable = self.currentTables[-1]
            if (not currentTable.res) or currentTable.firstRowParsed:
                currentTable.res += s
            else:
                currentTable.tempRes += s
        else:
            self.res += s

    def getTagsToReopen(self, conflictElems):
        '''Normally, tags to reopen are equal to p_conflictElems. But we have a
           special case. Indeed, if a conflict elem has itself tagsToClose,
           the last tag to close may not be needed anymore on the tag to
           reopen, so we remove it.'''
        conflictElems[-1].tagsToClose = []
        return conflictElems

    def onElementStart(self, elem, attrs):
        previousElem = self.getCurrentElement()
        self.dumpCurrentContent()
        currentElem = HtmlElement(elem, attrs)
        # Manage conflictual elements
        conflictElems = currentElem.getConflictualElements(self)
        if conflictElems:
            # We must close the conflictual elements, and once the currentElem
            # will be dumped, we will re-open the conflictual elements.
            self.closeConflictualElements(conflictElems)
            currentElem.tagsToReopen = self.getTagsToReopen(conflictElems)
        # Manage missing elements
        if self.anElementIsMissing(previousElem, currentElem):
            previousElem.addInnerParagraph(self)
        # Add the current element on the stack of walked elements
        self.currentElements.append(currentElem)
        if elem in XHTML_LISTS:
            # Update stack of current lists
            self.currentLists.append(currentElem)
        elif elem == 'table':
            # Update stack of current tables
            if not self.currentTables:
                # We are within a table. If no local style mapping is defined
                # for paragraphs, add a specific style mapping for a better
                # rendering of cells' content.
                caller = self.parser.caller
                map = caller.localStylesMapping
                if 'p' not in map:
                    map['p'] = Style('Appy_Table_Content', 'paragraph')
            self.currentTables.append(HtmlTable(self))
        elif elem in TABLE_CELL_TAGS:
            # Determine colspan
            colspan = 1
            if attrs.has_key('colspan'): colspan = int(attrs['colspan'])
            table = self.currentTables[-1]
            table.inCell = colspan
            table.cellIndex += colspan
            # If we are in the first row of a table, update columns count
            if not table.firstRowParsed:
                table.nbOfColumns += colspan
            if attrs.has_key('width') and (colspan == 1):
                # Get the width, keep figures only.
                width = ''
                for c in attrs['width']:
                    if c.isdigit(): width += c
                width = int(width)
                # Ensure self.columnWidths is long enough
                while (len(table.columnWidths)-1) < table.cellIndex:
                    table.columnWidths.append(None)
                table.columnWidths[table.cellIndex] = width
        return currentElem

    def onElementEnd(self, elem):
        res = None
        self.dumpCurrentContent()
        currentElem = self.currentElements.pop()
        if elem in XHTML_LISTS:
            self.currentLists.pop()
        elif elem == 'table':
            table = self.currentTables.pop()
            # Computes the column styles required by the table
            table.computeColumnStyles(self.parser.caller.renderer)
            # Dumps the content of the last parsed table into the parent buffer
            self.dumpString(table.res)
            # Remove cell-paragraph from local styles mapping if it was added.
            map = self.parser.caller.localStylesMapping
            if not self.currentTables and ('p' in map):
                mapValue = map['p']
                if isinstance(mapValue, Style) and \
                   (mapValue.name == 'Appy_Table_Content'):
                    del map['p']
        elif elem == 'tr':
            table = self.currentTables[-1]
            table.cellIndex = -1
            if not table.firstRowParsed:
                table.firstRowParsed = True
                # First row is parsed. I know the number of columns in the
                # table: I can dump the columns declarations.
                for i in range(1, table.nbOfColumns + 1):
                    table.res+= '<%s:table-column %s:style-name="%s.%d"/>' % \
                                (self.tableNs, self.tableNs, table.name, i)
                table.res += table.tempRes
                table.tempRes = u''
        elif elem in TABLE_CELL_TAGS:
            # Update attr "columnContentSizes" of the currently parsed table,
            # excepted if the cell spans several columns.
            table = self.currentTables[-1]
            if table.inCell == 1:
                sizes = table.columnContentSizes
                # Insert None values if the list is too small
                while (len(sizes)-1) < table.cellIndex: sizes.append(None)
                highest = max(sizes[table.cellIndex], table.cellContentSize, 5)
                # Put a maximum
                highest = min(highest, 100)
                sizes[table.cellIndex] = highest
            table.inCell = 0
            table.cellContentSize = 0
        if currentElem.tagsToClose:
            self.closeConflictualElements(currentElem.tagsToClose)
        if currentElem.tagsToReopen:
            res = currentElem.tagsToReopen
        return currentElem, res

# ------------------------------------------------------------------------------
class XhtmlParser(XmlParser):
    def lowerizeInput(self, elem, attrs=None):
        '''Because (X)HTML is case insensitive, we may receive input p_elem and
           p_attrs in lower-, upper- or mixed-case. So here we produce lowercase
           versions that will be used throughout our parser.'''
        resElem = elem.lower()
        resAttrs = attrs
        if attrs:
            resAttrs = {}
            for attrName in attrs.keys():
                resAttrs[attrName.lower()] = attrs[attrName]
        if attrs == None:
            return resElem
        else:
            return resElem, resAttrs

    def startElement(self, elem, attrs):
        elem, attrs = self.lowerizeInput(elem, attrs)
        e = XmlParser.startElement(self, elem, attrs)
        currentElem = e.onElementStart(elem, attrs)
        odfTag = currentElem.getOdfTag(e)

        if HTML_2_ODT.has_key(elem):
            e.dumpStyledElement(currentElem, odfTag, attrs)
        elif elem == 'a':
            e.dumpString('<%s %s:type="simple"' % (odfTag, e.linkNs))
            if attrs.has_key('href'):
                e.dumpString(' %s:href="%s"' % (e.linkNs,
                                                escapeXml(attrs['href'])))
            e.dumpString('>')
        elif elem in XHTML_LISTS:
            prologue = ''
            if len(e.currentLists) >= 2:
                # It is a list into another list. In this case the inner list
                # must be surrounded by a list-item element.
                prologue = '<%s:list-item>' % e.textNs
            numbering = ''
            if elem == 'ol':
                numbering = ' %s:continue-numbering="false"' % e.textNs
            e.dumpString('%s<%s %s:style-name="%s"%s>' % (
                prologue, odfTag, e.textNs, e.listStyles[elem], numbering))
        elif elem in ('li', 'thead', 'tr'):
            e.dumpString('<%s>' % odfTag)
        elif elem == 'table':
            # Here we must call "dumpString" only once
            table = e.currentTables[-1]
            e.dumpString('<%s %s:name="%s" %s:style-name="podTable">' % \
                         (odfTag, e.tableNs, table.name, e.tableNs))
        elif elem in TABLE_CELL_TAGS:
            e.dumpString('<%s %s:style-name="%s"' % \
                (odfTag, e.tableNs, DEFAULT_ODT_STYLES[elem]))
            if attrs.has_key('colspan'):
                e.dumpString(' %s:number-columns-spanned="%s"' % \
                             (e.tableNs, attrs['colspan']))
            e.dumpString('>')
        elif elem == 'img':
            style = None
            if attrs.has_key('style'): style = attrs['style']
            imgCode = e.renderer.importDocument(at=attrs['src'],
                                                wrapInPara=False, style=style)
            e.dumpString(imgCode)
        elif elem in IGNORABLE_TAGS:
            e.ignore = True

    def endElement(self, elem):
        elem = self.lowerizeInput(elem)
        e = XmlParser.endElement(self, elem)
        currentElem, elemsToReopen = e.onElementEnd(elem)
        # Determine the tag to dump
        startTag, endTag = currentElem.getOdfTags(e)
        if currentElem.isConflictual:
            # Compute the start tag, with potential styles applied
            startTag = e.getTags((currentElem,), start=True)
        if currentElem.isConflictual and e.res.endswith(startTag):
            # We will not dump it, it would constitute a silly empty tag.
            e.res = e.res[:-len(startTag)]
        else:
            # Dump the end tag. But dump some additional stuff if required.
            if elem in XHTML_LISTS:
                if len(e.currentLists) >= 1:
                    # We were in an inner list. So we must close the list-item
                    # tag that surrounds it.
                    endTag = '%s</%s:list-item>' % (endTag, e.textNs)
            if endTag:
                e.dumpString(endTag)
        if elem in IGNORABLE_TAGS:
            e.ignore = False
        if elemsToReopen:
            e.dumpString(e.getTags(elemsToReopen, start=True))

    def characters(self, content):
        e = XmlParser.characters(self, content)
        if not e.ignore:
            e.currentContent += content

# -------------------------------------------------------------------------------
class Xhtml2OdtConverter:
    '''Converts a chunk of XHTML into a chunk of ODT.'''
    def __init__(self, xhtmlString, encoding, stylesManager, localStylesMapping,
                 renderer):
        self.renderer = renderer
        self.xhtmlString = xhtmlString
        self.encoding = encoding # Todo: manage encoding that is not utf-8
        self.stylesManager = stylesManager
        self.localStylesMapping = localStylesMapping
        self.odtChunk = None
        self.xhtmlParser = XhtmlParser(XhtmlEnvironment(renderer), self)

    def run(self):
        self.xhtmlParser.parse(self.xhtmlString)
        return self.xhtmlParser.env.res

    def findStyle(self, elem, attrs=None, classValue=None):
        return self.stylesManager.findStyle(elem, attrs, classValue,
                                            self.localStylesMapping)
# ------------------------------------------------------------------------------
