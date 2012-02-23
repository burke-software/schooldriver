import xlwt as pycel
import sys
import re
from django.http import HttpResponse

def is_number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False

class xlsReport:
    # Generate a generic xls report based on given data in array.
    # Can make a simple 1 sheet report with 1 line of code or make multiple
    titleStyle = pycel.XFStyle()
    headingStyle = pycel.XFStyle()
    dataStyle = pycel.XFStyle()
    wb = pycel.XFStyle()
    
    def prepareStyles(self):
        self.wb = None
        self.wb = pycel.Workbook()
        #setup styles
        myFont = pycel.Font()
        myFont.bold = True
        self.titleStyle.borders.left   = 0x01
        self.titleStyle.borders.right  = 0x01
        self.titleStyle.borders.bottom = 0x02
        self.titleStyle.font = myFont
        myFont = pycel.Font()
        myFont.bold = True
        self.headingStyle.font = myFont
        self.dataStyle.borders.left   = 0x01
        self.dataStyle.borders.right  = 0x01
        self.dataStyle.borders.bottom = 0x01
        self.dataStyle.borders.top = 0x01
    
    def __init__(self, data, titles, fileName, heading=""):
        # a typical and very simple way of using this.
        self.prepareStyles()
        self.fileName = fileName
        self.addSheet(data, titles, heading)
    
    def addSheet(self, data, titles=None, heading=""):
        ws = self.wb.add_sheet(heading)
        if heading != "":
            ws.write(0,0,heading, self.headingStyle)
            y = 1
        else:
            y = 0
        x = 0
        if titles:
            for title in titles:
                ws.write(y,x,str(title), self.titleStyle)
                x += 1
            y += 1
        for row in data:
            x=0
            for cell in row:
                try:
                    if is_number(unicode(cell)):
                        ws.write(y,x, float(cell), self.dataStyle)
                    else:
                        ws.write(y,x,unicode(cell), self.dataStyle)
                except:
                    ws.write(y,x,str(sys.exc_info()[0]))
                x += 1
            y += 1
    
    def finish(self):
        response = HttpResponse(mimetype="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=%s' % self.fileName
        self.wb.save(response)
        return response

class customXls(xlsReport):
    def __init__(self, fileName):
        # A more customizable way to create an xls doc that doesn't result in an xls by itself.
        self.wb = None
        self.wb = pycel.Workbook()
        self.prepareStyles()
        self.fileName = fileName
