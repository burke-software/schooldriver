# ------------------------------------------------------------------------------
import cgi

# ------------------------------------------------------------------------------
class OdtTable:
    '''This class allows to construct an ODT table programmatically. As ODT and
       HTML are very similar, this class also allows to contruct an
       HTML table.'''
    # Some namespace definitions
    tns = 'table:'
    txns = 'text:'

    def __init__(self, name, paraStyle, cellStyle, nbOfCols,
                 paraHeaderStyle=None, cellHeaderStyle=None, html=False):
        # An ODT table must have a name. In the case of an HTML table, p_name
        # represents the CSS class for the whole table.
        self.name = name
        # The default style of every paragraph within cells
        self.paraStyle = paraStyle
        # The default style of every cell
        self.cellStyle = cellStyle
        # The total number of columns
        self.nbOfCols = nbOfCols
        # The default style of every paragraph within a header cell
        self.paraHeaderStyle = paraHeaderStyle or paraStyle
        # The default style of every header cell
        self.cellHeaderStyle = cellHeaderStyle or cellStyle
        # The buffer where the resulting table will be rendered
        self.res = ''
        # Do we need to generate an HTML table instead of an ODT table ?
        self.html = html

    def dumpCell(self, content, span=1, header=False,
                 paraStyle=None, cellStyle=None):
        '''Dumps a cell in the table. If no specific p_paraStyle (p_cellStyle)
           is given, self.paraStyle (self.cellStyle) is used, excepted if
           p_header is True: in that case, self.paraHeaderStyle
           (self.cellHeaderStyle) is used.'''
        if not paraStyle:
            if header: paraStyle = self.paraHeaderStyle
            else: paraStyle = self.paraStyle
        if not cellStyle:
            if header: cellStyle = self.cellHeaderStyle
            else: cellStyle = self.cellStyle
        if not self.html:
            self.res += '<%stable-cell %sstyle-name="%s" ' \
                        '%snumber-columns-spanned="%d">' % \
                        (self.tns, self.tns, cellStyle, self.tns, span)
            self.res += '<%sp %sstyle-name="%s">%s</%sp>' % \
                        (self.txns, self.txns, paraStyle,
                         cgi.escape(str(content)), self.txns)
            self.res += '</%stable-cell>' % self.tns
        else:
            tag = header and 'th' or 'td'
            self.res += '<%s colspan="%d">%s</%s>' % \
                        (tag, span, cgi.escape(str(content)), tag)

    def startRow(self):
        if not self.html:
            self.res += '<%stable-row>' % self.tns
        else:
            self.res += '<tr>'

    def endRow(self):
        if not self.html:
            self.res += '</%stable-row>' % self.tns
        else:
            self.res += '</tr>'

    def startTable(self):
        if not self.html:
            self.res += '<%stable %sname="%s">' % (self.tns, self.tns,
                                                   self.name)
            self.res += '<%stable-column %snumber-columns-repeated="%d"/>' % \
                        (self.tns, self.tns, self.nbOfCols)
        else:
            css = ''
            if self.name: css = ' class="%s"' % self.name
            self.res += '<table%s cellpadding="0" cellspacing="0">' % css

    def endTable(self):
        if not self.html:
            self.res += '</%stable>' % self.tns
        else:
            self.res += '</table>'

    def dumpFloat(self, number):
        return str(round(number, 2))

    def get(self):
        '''Returns the whole table.'''
        if self.html:
            return self.res
        else:
            return self.res.decode('utf-8')
# ------------------------------------------------------------------------------
