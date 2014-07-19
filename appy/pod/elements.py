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
from xml.sax.saxutils import quoteattr
from appy.shared.xml_parser import XmlElement
from appy.pod.odf_parser import OdfEnvironment as ns
from appy.pod import PodError

# ------------------------------------------------------------------------------
class PodElement:
    OD_TO_POD = {'p': 'Text', 'h': 'Title', 'section': 'Section',
                 'table': 'Table', 'table-row': 'Row', 'table-cell': 'Cell',
                 None: 'Expression'}
    POD_ELEMS = ('text', 'title', 'section', 'table', 'row', 'cell')
    # Elements for which the '-' operator can be applied.
    MINUS_ELEMS = ('section', 'table')
    @staticmethod
    def create(elem):
        '''Used to create any POD elem that has an equivalent OD element. Not
           for creating expressions, for example.'''
        return eval(PodElement.OD_TO_POD[elem])()

class Text(PodElement):
    OD = XmlElement('p', nsUri=ns.NS_TEXT)
    # When generating an error we may need to surround it with a given tag and
    # sub-tags.
    subTags = []

class Title(PodElement):
    OD = XmlElement('h', nsUri=ns.NS_TEXT)
    subTags = []

class Section(PodElement):
    OD = XmlElement('section', nsUri=ns.NS_TEXT)
    subTags = [Text.OD]
    # When we must remove the Section element from a buffer, the deepest element
    # to remove is the Section element itself.
    DEEPEST_TO_REMOVE = OD

class Cell(PodElement):
    OD = XmlElement('table-cell', nsUri=ns.NS_TABLE)
    subTags = [Text.OD]
    def __init__(self):
        self.tableInfo = None # ~OdTable~
        self.colIndex = None # The column index for this cell, within its table.

class Row(PodElement):
    OD = XmlElement('table-row', nsUri=ns.NS_TABLE)
    subTags = [Cell.OD, Text.OD]

class Table(PodElement):
    OD = XmlElement('table', nsUri=ns.NS_TABLE)
    subTags = [Row.OD, Cell.OD, Text.OD]
    # When we must remove the Table element from a buffer, the deepest element
    # to remove is the Cell (it can only be done for one-row, one-cell tables).
    DEEPEST_TO_REMOVE = Cell.OD
    def __init__(self):
        self.tableInfo = None # ~OdTable~

class Expression(PodElement):
    '''Represents a Python expression that is found in a pod or px.'''
    OD = None
    def extractInfo(self, py):
        '''Within p_py, several elements can be included:
           - the fact that XML chars must be escaped or not (leading ":")
           - the "normal" Python expression,
           - an optional "error" expression, that is evaluated when the normal
             expression raises an exception.
           This method return a tuple (escapeXml, normaExpr, errorExpr).'''
        # Determine if we must escape XML chars or not.
        escapeXml = True
        if py.startswith(':'):
            py = py[1:]
            escapeXml = False
        # Extract normal and error expression
        if '|' not in py:
            expr = py
            errorExpr = None
        else:
            expr, errorExpr = py.rsplit('|', 1)
            expr = expr.strip()
            errorExpr = errorExpr.strip()
        return escapeXml, expr, errorExpr

    def __init__(self, py, pod):
        # Extract parts from expression p_py.
        self.escapeXml, self.expr, self.errorExpr = self.extractInfo(py.strip())
        self.pod = pod # True if I work for pod, False if I work for px.
        if self.pod:
            # pod-only: store here the expression's true result (before being
            # converted to a string).
            self.result = None
            # pod-only: the following bool indicates if this Expression instance
            # has already been evaluated or not. Expressions which are tied to
            # attribute hooks are already evaluated when the tied hook is
            # evaluated: this boolean prevents the expression from being
            # evaluated twice.
            self.evaluated = False
            # self.result and self.evaluated are not used by PX, because they
            # are not thread-safe.

    def _eval(self, context):
        '''Evaluates self.expr with p_context. If self.errorExpr is defined,
           evaluate it if self.expr raises an error.'''
        if self.errorExpr:
            try:
                res = eval(self.expr, context)
            except Exception:
                res = eval(self.errorExpr, context)
        else:
            res = eval(self.expr, context)
        return res

    def evaluate(self, context):
        '''Evaluates the Python expression (self.expr) with a given
           p_context, and returns the result. More precisely, it returns a
           tuple (result, escapeXml). Boolean escapeXml indicates if XML chars
           must be escaped or not.'''
        escapeXml = self.escapeXml
        # Evaluate the expression, or get it from self.result if it has already
        # been computed.
        if self.pod and self.evaluated:
            res = self.result
            # It can happen only once, to ask to evaluate an expression that
            # was already evaluated (from the tied hook). We reset here the
            # boolean "evaluated" to allow for the next evaluation, probably
            # with another context.
            self.evaluated = False
        else:
            res = self._eval(context)
            # pod-only: cache the expression result.
            if self.pod: self.result = res
        # Converts the expr result to a string that can be inserted in the
        # pod/px result.
        resultType = res.__class__.__name__
        if resultType == 'NoneType':
            res = u''
        elif resultType == 'str':
            res = res.decode('utf-8')
        elif resultType == 'unicode':
            pass # Don't perform any conversion, unicode is the target type.
        elif resultType == 'Px':
            # A PX that must be called within the current PX. Call it with the
            # current context.
            res = res(context, applyTemplate=False)
            # Force escapeXml to False.
            escapeXml = False
        else:
            res = unicode(res)
        return res, escapeXml

class Attributes(PodElement):
    '''Represents a bunch of XML attributes that will be dumped for a given tag
       in the result. pod-only.'''
    OD = None
    floatTypes = ('int', 'long', 'float')
    dateTypes = ('DateTime',)

    def __init__(self, env):
        self.attrs = {}
        # Depending on the result of a tied expression, we will dump, for
        # another tag, the series of attrs that this instance represents.
        self.tiedExpression = None
        # We will need the env to get the full names of attributes to dump.
        self.env = env

    def computeAttributes(self, expr):
        '''p_expr has been evaluated: its result is in expr.result. Depending
           on its type, we will dump the corresponding attributes in
           self.attrs.'''
        exprType = expr.result.__class__.__name__
        tags = self.env.tags
        attrs = self.attrs
        if exprType in self.floatTypes:
            attrs[tags['value-type']] = 'float'
            attrs[tags['value']] = str(expr.result)
        elif exprType in self.dateTypes:
            attrs[tags['value-type']] = 'date'
            attrs[tags['value']] = expr.result.strftime('%Y-%m-%d')
        else:
            attrs[tags['value-type']] = 'string'

    def evaluate(self, context):
        # Evaluate first the tied expression, in order to determine its type.
        try:
            self.tiedExpression.evaluate(context)
            self.tiedExpression.evaluated = True
        except Exception, e:
            # Don't set "evaluated" to True. This way, when the buffer will
            # evaluate the expression directly, we will really evaluate it, so
            # the error will be dumped into the pod result.
            pass
        # Analyse the return type of the expression.
        self.computeAttributes(self.tiedExpression)
        # Now, self.attrs has been populated. Transform it into a string.
        res = ''
        for name, value in self.attrs.iteritems():
            res += ' %s=%s' % (name, quoteattr(value))
        return res

class Attribute(PodElement):
    '''Represents an HTML special attribute like "selected" or "checked".
       px-only.'''
    OD = None

    def __init__(self, name, expr):
        # The name of the attribute
        self.name = name
        # The expression that will compute the attribute value
        self.expr = expr.strip()

    def evaluate(self, context):
        # If the expr evaluates to False, we do not dump the attribute at all.
        if eval(self.expr, context): return ' %s="%s"' % (self.name, self.name)
        return ''
# ------------------------------------------------------------------------------
