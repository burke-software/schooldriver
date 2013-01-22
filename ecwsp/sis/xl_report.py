from django.http import HttpResponse
import cStringIO as StringIO
from openpyxl.workbook import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.cell import get_column_letter
import re

def i_to_column_letter(column_number):
    """ Convert iterator into column letter (a,b,c.....aa,ab,etc)
    1 = a
    2 = b
    """
    # Since we convert to spreadsheet columns which contain multiple letters we need to build the string of letters
    column_name = ""
    dividend = column_number
    while dividend > 0:
        # mod division by 26 (letters in alphebet) plus 96 to offset into character range for str converstion
        modulo = (dividend - 1) % 26
        column_name = chr(65 + modulo) + column_name
        dividend = int((dividend - modulo) / 26)
    return column_name

class XlReport:
    """ Wrapper for openpyxl
    Using xlsx because xls has limitations and ods has no good python
    library
    """
    def __init__(self, file_name="Report"):
        self.wb = Workbook()
        self.wb.remove_sheet(self.wb.get_active_sheet())
        self.file_name = file_name
    
    def add_sheet(self, data, title=None, auto_width=False):
        """ Add a sheet with data to workbook
        """
        sheet = self.wb.create_sheet()
        if title:
            sheet.title = title
        for row in data:
            row = map(unicode, row)
            sheet.append(row)
        
    def as_download(self):
        """ Returns a django HttpResponse with the xlsx file """
        myfile = StringIO.StringIO()
        myfile.write(save_virtual_workbook(self.wb))
        response = HttpResponse(
            myfile.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s.xlsx' % self.file_name
        response['Content-Length'] = myfile.tell()
        return response