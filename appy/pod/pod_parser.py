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
import re
from appy.shared.xml_parser import XmlElement
from appy.pod.buffers import FileBuffer, MemoryBuffer
from appy.pod.odf_parser import OdfEnvironment, OdfParser
from appy.pod.elements import *

# ------------------------------------------------------------------------------
class OdTable:
    '''Informations about the currently parsed Open Document (Od)table.'''
    def __init__(self):
        self.nbOfColumns = 0
        self.nbOfRows = 0
        self.curColIndex = None
        self.curRowAttrs = None
    def isOneCell(self):
        return (self.nbOfColumns == 1) and (self.nbOfRows == 1)

class OdInsert:
    '''While parsing an odt/pod file, we may need to insert a specific odt chunk
       at a given place in the odt file (ie: add the pod-specific fonts and
       styles). OdInsert instances define such 'inserts' (what to insert and
       when).'''
    def __init__(self, odtChunk, elem, nsUris={}):
        self.odtChunk = odtChunk.decode('utf-8') # The odt chunk to insert
        self.elem = elem # The p_odtChunk will be inserted just after the p_elem
        # start, which must be an XmlElement instance. If more than one p_elem
        # is present in the odt file, the p_odtChunk will be inserted only at
        # the first p_elem occurrence.
        self.nsUris = nsUris # The URI replacements that need to be done in
        # p_odtChunk. It is a dict whose keys are names used in p_odtChunk (in
        # the form @name@) to refer to XML namespaces, and values are URIs of
        # those namespaces.
    def resolve(self, namespaces):
        '''Replaces all unresolved namespaces in p_odtChunk, thanks to the dict
           of p_namespaces.'''
        for nsName, nsUri in self.nsUris.iteritems():
            self.odtChunk = re.sub('@%s@' % nsName, namespaces[nsUri],
                                   self.odtChunk)
        return self.odtChunk

class PodEnvironment(OdfEnvironment):
    '''Contains all elements representing the current parser state during
       parsing.'''
    # Possibles modes
    # ADD_IN_BUFFER: when encountering an impactable element, we must
    #                continue to dump it in the current buffer
    ADD_IN_BUFFER = 0
    # ADD_IN_SUBBUFFER: when encountering an impactable element, we must
    #                   create a new sub-buffer and dump it in it.
    ADD_IN_SUBBUFFER = 1
    # Possible states
    IGNORING = 0 # We are ignoring what we are currently reading
    READING_CONTENT = 1 # We are reading "normal" content
    READING_STATEMENT = 2 # We are reading a POD statement (for, if...)
    READING_EXPRESSION = 3 # We are reading a POD expression.
    def __init__(self, context, inserts=[]):
        OdfEnvironment.__init__(self)
        # Buffer where we must dump the content we are currently reading
        self.currentBuffer = None
        # XML element content we are currently reading
        self.currentContent = ''
        # Current statement (a list of lines) that we are currently reading
        self.currentStatement = []
        # Current mode
        self.mode = self.ADD_IN_SUBBUFFER
        # Current state
        self.state = self.READING_CONTENT
        # Elements we must ignore (they will not be included in the result)
        self.ignorableElements = None # Will be set after namespace propagation
        # Elements that may be impacted by POD statements
        self.impactableElements = None # Idem
        # Stack of currently visited tables
        self.tableStack = []
        self.tableIndex = -1
        # Evaluation context
        self.context = context
        # For the currently read expression, is there style-related information
        # associated with it?
        self.exprHasStyle = False
        # Namespace definitions are not already encountered.
        self.gotNamespaces = False
        # Store inserts
        self.inserts = inserts
        # Currently walked "if" actions
        self.ifActions = []
        # Currently walked named "if" actions
        self.namedIfActions = {} #~{s_statementName: IfAction}~
        # Currently parsed expression within an ODS template
        self.currentOdsExpression = None
        self.currentOdsHook = None
        # Names of some tags, that we will compute after namespace propagation
        self.tags = None

    def getTable(self):
        '''Gets the currently parsed table.'''
        res = None
        if self.tableIndex != -1:
            res = self.tableStack[self.tableIndex]
        return res

    def transformInserts(self):
        '''Now the namespaces were parsed; I can put p_inserts in the form of a
           dict for easier and more performant access while parsing.'''
        res = {}
        for insert in self.inserts:
            elemName = insert.elem.getFullName(self.namespaces)
            if not res.has_key(elemName):
                res[elemName] = insert
        return res

    def manageInserts(self):
        '''We just dumped the start of an elem. Here we will insert any odt
           chunk if needed.'''
        if self.inserts.has_key(self.currentElem.elem):
            insert = self.inserts[self.currentElem.elem]
            self.currentBuffer.write(insert.resolve(self.namespaces))
            # The insert is destroyed after single use
            del self.inserts[self.currentElem.elem]

    def onStartElement(self):
        ns = self.namespaces
        if not self.gotNamespaces:
            # We suppose that all the interesting (from the POD point of view)
            # XML namespace definitions are defined at the root XML element.
            # Here we propagate them in XML element definitions that we use
            # throughout POD.
            self.gotNamespaces = True
            self.propagateNamespaces()
        elem = self.currentElem.elem
        tableNs = self.ns(self.NS_TABLE)
        if elem == Table.OD.elem:
            self.tableStack.append(OdTable())
            self.tableIndex += 1
        elif elem == Row.OD.elem:
            self.getTable().nbOfRows += 1
            self.getTable().curColIndex = -1
            self.getTable().curRowAttrs = self.currentElem.attrs
        elif elem == Cell.OD.elem:
            colspan = 1
            attrSpan = self.tags['number-columns-spanned']
            if self.currentElem.attrs.has_key(attrSpan):
                colspan = int(self.currentElem.attrs[attrSpan])
            self.getTable().curColIndex += colspan
        elif elem == self.tags['table-column']:
            attrs = self.currentElem.attrs
            if attrs.has_key(self.tags['number-columns-repeated']):
                self.getTable().nbOfColumns += int(
                    attrs[self.tags['number-columns-repeated']])
            else:
                self.getTable().nbOfColumns += 1
        return ns

    def onEndElement(self):
        ns = self.namespaces
        if self.currentElem.elem == Table.OD.elem:
            self.tableStack.pop()
            self.tableIndex -= 1
        return ns

    def addSubBuffer(self):
        subBuffer = self.currentBuffer.addSubBuffer()
        self.currentBuffer = subBuffer
        self.mode = self.ADD_IN_BUFFER

    def propagateNamespaces(self):
        '''Propagates the namespaces in all XML element definitions that are
           used throughout POD.'''
        ns = self.namespaces
        for elemName in PodElement.POD_ELEMS:
            xmlElemDef = eval(elemName[0].upper() + elemName[1:]).OD
            elemFullName = xmlElemDef.getFullName(ns)
            xmlElemDef.__init__(elemFullName)
        # Create a table of names of used tags and attributes (precomputed,
        # including namespace, for performance).
        self.tags = {
          'tracked-changes': '%s:tracked-changes' % ns[self.NS_TEXT],
          'change': '%s:change' % ns[self.NS_TEXT],
          'annotation': '%s:annotation' % ns[self.NS_OFFICE],
          'change-start': '%s:change-start' % ns[self.NS_TEXT],
          'change-end': '%s:change-end' % ns[self.NS_TEXT],
          'conditional-text': '%s:conditional-text' % ns[self.NS_TEXT],
          'table-cell': '%s:table-cell' % ns[self.NS_TABLE],
          'formula': '%s:formula' % ns[self.NS_TABLE],
          'value-type': '%s:value-type' % ns[self.NS_OFFICE],
          'value': '%s:value' % ns[self.NS_OFFICE],
          'string-value': '%s:string-value' % ns[self.NS_OFFICE],
          'span': '%s:span' % ns[self.NS_TEXT],
          'number-columns-spanned': '%s:number-columns-spanned' % \
                                    ns[self.NS_TABLE],
          'number-columns-repeated': '%s:number-columns-repeated' % \
                                    ns[self.NS_TABLE],
          'table-column': '%s:table-column' % ns[self.NS_TABLE],
        }
        self.ignorableElements = (self.tags['tracked-changes'],
                                  self.tags['change'])
        self.impactableElements = (
           Text.OD.elem, Title.OD.elem, Table.OD.elem, Row.OD.elem,
           Cell.OD.elem, Section.OD.elem)
        self.inserts = self.transformInserts()

# ------------------------------------------------------------------------------
class PodParser(OdfParser):
    def __init__(self, env, caller):
        OdfParser.__init__(self, env, caller)

    def endDocument(self):
        self.env.currentBuffer.content.close()

    def startElement(self, elem, attrs):
        e = OdfParser.startElement(self, elem, attrs)
        ns = e.onStartElement()
        officeNs = ns[e.NS_OFFICE]
        textNs = ns[e.NS_TEXT]
        tableNs = ns[e.NS_TABLE]
        if elem in e.ignorableElements:
            e.state = e.IGNORING
        elif elem == e.tags['annotation']:
            # Be it in an ODT or ODS template, an annotation is considered to
            # contain a POD statement.
            e.state = e.READING_STATEMENT
        elif elem in (e.tags['change-start'], e.tags['conditional-text']):
            # In an ODT template, any text in track-changes or any conditional
            # field is considered to contain a POD expression.
            e.state = e.READING_EXPRESSION
            e.exprHasStyle = False
        elif (elem == e.tags['table-cell']) and \
             attrs.has_key(e.tags['formula']) and \
             attrs.has_key(e.tags['value-type']) and \
             (attrs[e.tags['value-type']] == 'string') and \
             attrs[e.tags['formula']].startswith('of:="'):
            # In an ODS template, any cell containing a formula of type "string"
            # and whose content is expressed as a string between double quotes
            # (="...") is considered to contain a POD expression. But here it
            # is a special case: we need to dump the cell; the expression is not
            # directly contained within this cell; the expression will be
            # contained in the next inner paragraph. So we must here dump the
            # cell, but without some attributes, because the "formula" will be
            # converted to the result of evaluating the POD expression.
            if e.mode == e.ADD_IN_SUBBUFFER:
                e.addSubBuffer()
            e.currentBuffer.addElement(e.currentElem.name)
            hook = e.currentBuffer.dumpStartElement(elem, attrs,
                     ignoreAttrs=(e.tags['formula'], e.tags['string-value'],
                                  e.tags['value-type']),
                     hook=True)
            # We already have the POD expression: remember it on the env.
            e.currentOdsExpression = attrs[e.tags['string-value']]
            e.currentOdsHook = hook
        else:
            if e.state == e.IGNORING:
                pass
            elif e.state == e.READING_CONTENT:
                if elem in e.impactableElements:
                    if e.mode == e.ADD_IN_SUBBUFFER:
                        e.addSubBuffer()
                    e.currentBuffer.addElement(e.currentElem.name)
                e.currentBuffer.dumpStartElement(elem, attrs)
            elif e.state == e.READING_STATEMENT:
                pass
            elif e.state == e.READING_EXPRESSION:
                if (elem == (e.tags['span'])) and not e.currentContent.strip():
                    e.currentBuffer.dumpStartElement(elem, attrs)
                    e.exprHasStyle = True
        e.manageInserts()

    def endElement(self, elem):
        e = OdfParser.endElement(self, elem)
        ns = e.onEndElement()
        officeNs = ns[e.NS_OFFICE]
        textNs = ns[e.NS_TEXT]
        if elem in e.ignorableElements:
            e.state = e.READING_CONTENT
        elif elem == e.tags['annotation']:
            # Manage statement
            oldCb = e.currentBuffer
            actionElemIndex = oldCb.createAction(e.currentStatement)
            e.currentStatement = []
            if actionElemIndex != -1:
                e.currentBuffer = oldCb.\
                    transferActionIndependentContent(actionElemIndex)
                if e.currentBuffer == oldCb:
                    e.mode = e.ADD_IN_SUBBUFFER
                else:
                    e.mode = e.ADD_IN_BUFFER
            e.state = e.READING_CONTENT
        else:
            if e.state == e.IGNORING:
                pass
            elif e.state == e.READING_CONTENT:
                # Dump the ODS POD expression if any
                if e.currentOdsExpression:
                    e.currentBuffer.addExpression(e.currentOdsExpression,
                                                  tiedHook=e.currentOdsHook)
                    e.currentOdsExpression = None
                    e.currentOdsHook = None
                # Dump the ending tag
                e.currentBuffer.dumpEndElement(elem)
                if elem in e.impactableElements:
                    if isinstance(e.currentBuffer, MemoryBuffer):
                        isMainElement = e.currentBuffer.isMainElement(elem)
                        # Unreference the element among buffer.elements
                        e.currentBuffer.unreferenceElement(elem)
                        if isMainElement:
                            parent = e.currentBuffer.parent
                            if not e.currentBuffer.action:
                                # Delete this buffer and transfer content to
                                # parent.
                                e.currentBuffer.transferAllContent()
                                parent.removeLastSubBuffer()
                                e.currentBuffer = parent
                            else:
                                if isinstance(parent, FileBuffer):
                                    # Execute buffer action and delete the
                                    # buffer.
                                    e.currentBuffer.action.execute(parent,
                                                                   e.context)
                                    parent.removeLastSubBuffer()
                                e.currentBuffer = parent
                            e.mode = e.ADD_IN_SUBBUFFER
            elif e.state == e.READING_STATEMENT:
                if e.currentElem.elem == Text.OD.elem:
                    statementLine = e.currentContent.strip()
                    if statementLine:
                        e.currentStatement.append(statementLine)
                    e.currentContent = ''
            elif e.state == e.READING_EXPRESSION:
                if (elem == e.tags['change-end']) or \
                   (elem == e.tags['conditional-text']):
                    expression = e.currentContent.strip()
                    e.currentContent = ''
                    # Manage expression
                    e.currentBuffer.addExpression(expression)
                    if e.exprHasStyle:
                        e.currentBuffer.dumpEndElement(e.tags['span'])
                    e.state = e.READING_CONTENT

    def characters(self, content):
        e = OdfParser.characters(self, content)
        if e.state == e.IGNORING:
            pass
        elif e.state == e.READING_CONTENT:
            if e.currentOdsExpression:
                # Do not write content if we have encountered an ODS expression:
                # we will replace this content with the expression's result.
                pass
            else:
                e.currentBuffer.dumpContent(content)
        elif e.state == e.READING_STATEMENT:
            if e.currentElem.elem.startswith(e.namespaces[e.NS_TEXT]):
                e.currentContent += content
        elif e.state == e.READING_EXPRESSION:
            e.currentContent += content
# ------------------------------------------------------------------------------
