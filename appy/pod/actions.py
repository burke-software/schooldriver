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
from appy import Object
from appy.pod import PodError
from appy.pod.elements import *

# ------------------------------------------------------------------------------
EVAL_ERROR = 'Error while evaluating expression "%s".'
FROM_EVAL_ERROR = 'Error while evaluating the expression "%s" defined in the ' \
                  '"from" part of a statement.'
WRONG_SEQ_TYPE = 'Expression "%s" is not iterable.'
TABLE_NOT_ONE_CELL = "The table you wanted to populate with '%s' " \
                     "can\'t be dumped with the '-' option because it has " \
                     "more than one cell in it."

# ------------------------------------------------------------------------------
class BufferAction:
    '''Abstract class representing a action (=statement) that must be performed
       on the content of a buffer (if, for...).'''
    def __init__(self, name, buffer, expr, elem, minus, source, fromExpr):
        self.name = name # Actions may be named. Currently, the name of an
        # action is only used for giving a name to "if" actions; thanks to this
        # name, "else" actions that are far away may reference their "if".
        self.buffer = buffer # The object of the action
        self.expr = expr # Python expression to evaluate (may be None in the
        # case of a NullAction or ElseAction, for example)
        self.elem = elem # The element within the buffer that is the object
        # of the action.
        self.minus = minus # If True, the main buffer element(s) must not be
        # dumped.
        self.result = self.buffer.getFileBuffer()
        self.source = source # if 'buffer', we must dump the (evaluated) buffer
        # content. If 'from', we must dump what comes from the 'from' part of
        # the action (='fromExpr')
        self.fromExpr = fromExpr
        # We store the result of evaluation of expr and fromExpr
        self.exprResult = None
        self.fromExprResult = None
    def writeError(self, errorMessage, dumpTb=True):
        # Empty the buffer
        self.buffer.__init__(self.buffer.env, self.buffer.parent)
        PodError.dump(self.buffer, errorMessage, withinElement=self.elem,
                      dumpTb=dumpTb)
        self.buffer.evaluate()
    def execute(self):
        # Check that if minus is set, we have an element which can accept it
        if self.minus and isinstance(self.elem, Table) and \
           (not self.elem.tableInfo.isOneCell()):
            self.writeError(TABLE_NOT_ONE_CELL % self.expr)
        else:
            errorOccurred = False
            if self.expr:
                try:
                    self.exprResult = eval(self.expr, self.buffer.env.context)
                except:
                    self.exprResult = None
                    self.writeError(EVAL_ERROR % self.expr)
                    errorOccurred = True
            if not errorOccurred:
                self.do()
    def evaluateBuffer(self):
        if self.source == 'buffer':
            self.buffer.evaluate(removeMainElems = self.minus)
        else:
            # Evaluate fromExpr
            self.fromExprResult = None
            errorOccurred = False
            try:
                self.fromExprResult= eval(self.fromExpr,self.buffer.env.context)
            except PodError, pe:
                self.writeError(FROM_EVAL_ERROR % self.fromExpr + ' ' + str(pe),
                                dumpTb=False)
                errorOccurred = True
            except:
                self.writeError(FROM_EVAL_ERROR % self.fromExpr)
                errorOccurred = True
            if not errorOccurred:
                self.result.write(self.fromExprResult)

class IfAction(BufferAction):
    '''Action that determines if we must include the content of the buffer in
       the result or not.'''
    def do(self):
        if self.exprResult:
            self.evaluateBuffer()
        else:
            if self.buffer.isMainElement(Cell.OD):
                # Don't leave the current row with a wrong number of cells
                self.result.dumpElement(Cell.OD.elem)

class ElseAction(IfAction):
    '''Action that is linked to a previous "if" action. In fact, an "else"
       action works exactly like an "if" action, excepted that instead of
       defining a conditional expression, it is based on the negation of the
       conditional expression of the last defined "if" action.'''
    def __init__(self, name, buffer, expr, elem, minus, source, fromExpr,
                 ifAction):
        IfAction.__init__(self, name, buffer, None, elem, minus, source,
                          fromExpr)
        self.ifAction = ifAction
    def do(self):
        # The result of this "else" action is "not <result from last execution
        # of linked 'if' action>".
        self.exprResult = not self.ifAction.exprResult
        IfAction.do(self)

class ForAction(BufferAction):
    '''Actions that will include the content of the buffer as many times as
       specified by the action parameters.'''
    def __init__(self, name, buffer, expr, elem, minus, iter, source, fromExpr):
        BufferAction.__init__(self, name, buffer, expr, elem, minus, source,
                              fromExpr)
        self.iter = iter # Name of the iterator variable used in the each loop

    def initialiseLoop(self):
        '''Initialises information about the loop, before entering into it.'''
        context = self.buffer.env.context
        # The "loop" object, made available in the POD context, contains info
        # about all currently walked loops. For every walked loop, a specific
        # object, le'ts name it curLoop, accessible at getattr(loop, self.iter),
        # stores info about its status:
        #   * curLoop.length  gives the total number of walked elements withhin
        #                     the loop
        #   * curLoop.nb      gives the index (starting at 0) if the currently
        #                     walked element.
        # For example, if you have a "for" statement like this:
        #        for elem in myListOfElements
        # Within the part of the ODT document impacted by this statement, you
        # may access to:
        #   * loop.elem.length to know the total length of myListOfElements
        #   * loop.elem.nb     to know the index of the current elem within
        #                      myListOfElements.
        if 'loop' not in context:
            context['loop'] = Object()
        try:
            total = len(self.exprResult)
        except:
            total = 0
        curLoop = Object(length=total)
        setattr(context['loop'], self.iter, curLoop)
        return curLoop

    def do(self):
        context = self.buffer.env.context
        # Check self.exprResult type
        try:
            str(self.exprResult) ### django-sis change
            # All "iterable" objects are OK. Thanks to Bernhard Bender for this
            # improvement.
        except TypeError:
            self.writeError(WRONG_SEQ_TYPE % self.expr)
            return
        # Remember variable hidden by iter if any
        hasHiddenVariable = False
        if context.has_key(self.iter):
            hiddenVariable = context[self.iter]
            hasHiddenVariable = True
        # In the case of cells, initialize some values
        isCell = False
        if isinstance(self.elem, Cell):
            isCell = True
            nbOfColumns = self.elem.tableInfo.nbOfColumns
            initialColIndex = self.elem.colIndex
            currentColIndex = initialColIndex
            rowAttributes = self.elem.tableInfo.curRowAttrs
            # If self.exprResult is empty, dump an empty cell to avoid
            # having the wrong number of cells for the current row
            if not self.exprResult:
                self.result.dumpElement(Cell.OD.elem)
        # Enter the "for" loop
        loop = self.initialiseLoop()
        i = -1
        for item in self.exprResult:
            i += 1
            loop.nb = i
            context[self.iter] = item
            # Cell: add a new row if we are at the end of a row
            if isCell and (currentColIndex == nbOfColumns):
                self.result.dumpEndElement(Row.OD.elem)
                self.result.dumpStartElement(Row.OD.elem, rowAttributes)
                currentColIndex = 0
            self.evaluateBuffer()
            # Cell: increment the current column index
            if isCell:
                currentColIndex += 1
        # Cell: leave the last row with the correct number of cells
        if isCell and self.exprResult and False:  ## django-sis change
            wrongNbOfCells = (currentColIndex-1) - initialColIndex
            if wrongNbOfCells < 0: # Too few cells for last row
                for i in range(abs(wrongNbOfCells)):
                    context[self.iter] = ''
                    self.buffer.evaluate(subElements=False)
                    # This way, the cell is dumped with the correct styles
            elif wrongNbOfCells > 0: # Too many cells for last row
                # Finish current row
                nbOfMissingCells = 0
                if currentColIndex < nbOfColumns:
                    nbOfMissingCells = nbOfColumns - currentColIndex
                    context[self.iter] = ''
                    for i in range(nbOfMissingCells):
                        self.buffer.evaluate(subElements=False)
                self.result.dumpEndElement(Row.OD.elem)
                # Create additional row with remaining cells
                self.result.dumpStartElement(Row.OD.elem, rowAttributes)
                nbOfRemainingCells = wrongNbOfCells + nbOfMissingCells
                nbOfMissingCellsLastLine = nbOfColumns - nbOfRemainingCells
                context[self.iter] = ''
                for i in range(nbOfMissingCellsLastLine):
                    self.buffer.evaluate(subElements=False)
        # Delete the object representing info about the current loop.
        try:
            delattr(context['loop'], self.iter)
        except AttributeError:
            pass
        # Restore hidden variable if any
        if hasHiddenVariable:
            context[self.iter] = hiddenVariable
        else:
            if self.exprResult:
                if self.iter in context: # May not be the case on error.
                    del context[self.iter]

class NullAction(BufferAction):
    '''Action that does nothing. Used in conjunction with a "from" clause, it
       allows to insert in a buffer arbitrary odt content.'''
    def do(self):
        self.evaluateBuffer()

class VariableAction(BufferAction):
    '''Action that allows to define a variable somewhere in the template.'''
    def __init__(self, name, buffer, expr, elem, minus, varName, source,
        fromExpr):
        BufferAction.__init__(self, name, buffer, expr, elem, minus, source,
                              fromExpr)
        self.varName = varName # Name of the variable
    def do(self):
        context = self.buffer.env.context
        # Remember the variable hidden by our variable definition, if any
        hasHiddenVariable = False
        if context.has_key(self.varName):
            hiddenVariable = context[self.varName]
            hasHiddenVariable = True
        # Add the variable to the context
        context[self.varName] = self.exprResult
        # Evaluate the buffer
        self.evaluateBuffer()
        # Restore hidden variable if any
        if hasHiddenVariable:
            context[self.varName] = hiddenVariable
        else:
            del context[self.varName]
# ------------------------------------------------------------------------------
