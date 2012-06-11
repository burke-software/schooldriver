from django.http import HttpResponse
from django.conf import settings

from ecwsp.sis.models import UserPreference

import xlwt as pycel
import sys
import re
import os
import tempfile
import binascii

def is_number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
    
def i_to_column_letter(i):
    """ Convert iterator into column letter (a,b,c.....aa,ab,etc)
    1 = a
    2 = b
    """
    i += 96
    return chr(i)

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
    
    def __init__(self, data, titles=None, fileName="report", heading="", heading_top=True):
        """ data: data to be included in rows. ex [['this', 'is', 'row 1'], ['row2', 'column2', 'column3']]
        titles: header array
        fileName:
        heading: Optionally add header above data"""
        self.prepareStyles()
        self.fileName = fileName
        self.addSheet(data, titles, heading, heading_top=heading_top)

    def addSheet(self, data, titles=None, heading="", addtional_fields_user=None, heading_top=True):
        """ Used to create additional sheet.
        data: data to be included in rows. ex [['this', 'is', 'row 1'], ['row2', 'column2', 'column3']]
        titles: header array
        heading: Optionally add header above data"""
        ws = self.wb.add_sheet(heading)
        if heading != "" and heading_top:
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
                    if unicode(cell)[:26] == "<xlwt.ExcelFormula.Formula":
                        ws.write(y,x, cell, self.dataStyle)
                    elif is_number(unicode(cell)):
                        ws.write(y,x, float(cell), self.dataStyle)
                    else:
                        ws.write(y,x,unicode(cell), self.dataStyle)
                except:
                    ws.write(y,x,str(sys.exc_info()[0]))
                x += 1
            y += 1
    
    def finish(self, type="xls"):
        response = HttpResponse(mimetype="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename="%s"' % self.fileName
        self.wb.save(response)
        return response
    
    def save(self, filename):
        self.wb.save(settings.MEDIA_ROOT + filename)


class customXls(xlsReport):
    def __init__(self, fileName):
        # A more customizable way to create an xls doc that doesn't result in an xls by itself.
        self.wb = None
        self.wb = pycel.Workbook()
        self.prepareStyles()
        self.fileName = fileName
