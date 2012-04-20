'''This module contains some useful classes for constructing ODF documents
   programmatically.'''

# ------------------------------------------------------------------------------
class OdtTable:
    '''This class allows to construct an ODT table programmatically.'''
    # Some namespace definitions
    tns = 'table:'
    txns = 'text:'

    def __init__(self, tableName, paraStyle, cellStyle,
                 paraHeaderStyle, cellHeaderStyle, nbOfCols):
        self.tableName = tableName
        self.paraStyle = paraStyle
        self.cellStyle = cellStyle
        self.paraHeaderStyle = paraHeaderStyle
        self.cellHeaderStyle = cellHeaderStyle
        self.nbOfCols = nbOfCols
        self.res = ''

    def dumpCell(self, content, span=1, header=False):
        if header:
            paraStyleName = self.paraHeaderStyle
            cellStyleName = self.cellHeaderStyle
        else:
            paraStyleName = self.paraStyle
            cellStyleName = self.cellStyle
        self.res += '<%stable-cell %sstyle-name="%s" ' \
                    '%snumber-columns-spanned="%d">' % \
                    (self.tns, self.tns, cellStyleName, self.tns, span)
        self.res += '<%sp %sstyle-name="%s">%s</%sp>' % \
                    (self.txns, self.txns, paraStyleName, content, self.txns)
        self.res += '</%stable-cell>' % self.tns

    def startRow(self):
        self.res += '<%stable-row>' % self.tns

    def endRow(self):
        self.res += '</%stable-row>' % self.tns

    def startTable(self):
        self.res += '<%stable %sname="AnalysisTable">' % (self.tns, self.tns)
        self.res += '<%stable-column %snumber-columns-repeated="%d"/>' % \
                    (self.tns, self.tns, self.nbOfCols)

    def endTable(self):
        self.res += '</%stable>' % self.tns

    def dumpFloat(self, number):
        return str(round(number, 2))

    def get(self):
        '''Returns the whole table.'''
        self.startTable()
        self.getRows()
        self.endTable()
        return self.res.decode('utf-8')
# ------------------------------------------------------------------------------
