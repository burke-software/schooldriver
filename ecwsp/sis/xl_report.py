from django.http import HttpResponse
import cStringIO as StringIO
from openpyxl.workbook import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.cell import get_column_letter
import re

class XlReport:
    """ Wrapper for openpyxl
    Using xlsx because xls has limitations and ods has no good python
    library
    """
    def __init__(self, file_name="Report"):
        """ file_name does not need an extention """
        self.workbook = Workbook()
        self.workbook.remove_sheet(self.workbook.get_active_sheet())
        self.file_name = file_name
    
    def add_sheet(self, data, title=None, auto_width=False, max_auto_width=50):
        """ Add a sheet with data to workbook
        auto_width will ESTIMATE the width of each column by counting
        max chars in each column. It will not work with a formula.
        max_auto_width is the max number of characters a column to be
        """
        sheet = self.workbook.create_sheet()
        if title:
            sheet.title = title
        for row in data:
            row = map(unicode, row)
            sheet.append(row)
        if auto_width:
            column_widths = []
            for row in data:
                row = map(unicode, row)
                for i, cell in enumerate(row):
                    if len(column_widths) > i:
                        if len(cell) > column_widths[i]:
                            column_widths[i] = len(cell)
                    else:
                        column_widths += [len(cell)]
            
            for i, column_width in enumerate(column_widths):
                if column_width > 0:
                    if column_width < max_auto_width:
                        # * 0.9 estimates a typical variable width font
                        sheet.column_dimensions[get_column_letter(i+1)].width = column_width * 0.9
                    else:
                        sheet.column_dimensions[get_column_letter(i+1)].width = max_auto_width
        
    def as_download(self):
        """ Returns a django HttpResponse with the xlsx file """
        myfile = StringIO.StringIO()
        myfile.write(save_virtual_workbook(self.workbook))
        response = HttpResponse(
            myfile.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s.xlsx' % self.file_name
        response['Content-Length'] = myfile.tell()
        return response