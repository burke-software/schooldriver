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
    MINUS_ELEMS = ('section', 'table') # Elements for which the '-' operator can
    # be applied
    def create(elem):
        '''Used to create any POD elem that has a equivalent OD element. Not
           for creating expressions, for example.'''
        return eval(PodElement.OD_TO_POD[elem])()
    create = staticmethod(create)

class Text(PodElement):
    OD = XmlElement('p', nsUri=ns.NS_TEXT)
    subTags = [] # When generating an error we may need to surround the error
    # with a given tag and subtags

class Title(PodElement):
    OD = XmlElement('h', nsUri=ns.NS_TEXT)
    subTags = []

class Section(PodElement):
    OD = XmlElement('section', nsUri=ns.NS_TEXT)
    subTags = [Text.OD]
    DEEPEST_TO_REMOVE = OD # When we must remove the Section element from a
    # buffer, the deepest element to remove is the Section element itself

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
    DEEPEST_TO_REMOVE = Cell.OD # When we must remove the Table element from a
    # buffer, the deepest element to remove is the Cell (it can only be done for
    # one-row, one-cell tables
    def __init__(self):
        self.tableInfo = None # ~OdTable~

class Expression(PodElement):
    '''Instances of this class represent Python expressions that are inserted
       into a POD template.'''
    OD = None
    def __init__(self, pyExpr):
        # The Python expression
        self.expr = pyExpr
        # We will store here the expression's true result (before being
        # converted to a string)
        self.result = None
        # This boolean indicates if this Expression instance has already been
        # evaluated or not. Expressions which are tied to attribute hooks are
        # already evaluated when the tied hook is evaluated: this boolean
        # prevents the expression from being evaluated twice.
        self.evaluated = False

    def evaluate(self, context):
        '''Evaluates the Python expression (self.expr) with a given
           p_context.'''
        # Evaluate the expression, or get it from self.result if it has already
        # been computed.
        if self.evaluated:
            res = self.result
            # It can happen only once, to ask to evaluate an expression that
            # was already evaluated (from the tied hook). We reset here the
            # boolean "evaluated" to allow for the next evaluation, probably
            # with another context.
            self.evaluated = False
        else:
            # Evaluates the Python expression
            res = self.result = eval(self.expr, context)
        # Converts the expression result to a string that can be inserted into
        # the POD result.
        if res == None:
            res = u''
        elif isinstance(res, str):
            res = unicode(res.decode('utf-8'))
        elif isinstance(res, unicode):
            pass
        else:
            res = unicode(res)
        return res

class Attributes(PodElement):
    '''Represents a bunch of XML attributes that will be dumped for a given tag
       in the result.'''
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
            self.evaluated = True
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
# ------------------------------------------------------------------------------
