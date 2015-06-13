from django.db.models.fields.files import FieldFile
from django.conf import settings
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

import os
import string
import tempfile

if 'TRAVIS' not in os.environ:
    """this import is killing us on TravisCI, so I'm removing it. There
    may be a better way to do this, but we honestly don't need anything
    from this file during our test runs."""
    import uno

import re

from ecwsp.sis.template_report import TemplateReport
from ecwsp.sis.helper_functions import strip_unicode_to_ascii


def uno_open(file):
    """This function should really just be in uno
    file -- Location of the file to open - must be a FieldFile
    returns an uno document
    """
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    context = resolver.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
    desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
    if 'amazonaws' in settings.STATIC_URL and hasattr(file, 'url'):
        file_url = file.url
    else:
        if isinstance(file, FieldFile):
            # We want the File then
            file = file.file
        file_url = "file://" + str(file)
    return desktop.loadComponentFromURL(file_url ,"_blank", 0, ())


def uno_save(document, filename, type):
    """ Save document
    document: desktop.loadComponentFromURL
    filename: filename of output without ext
    type: extension, example odt
    """
    from com.sun.star.beans import PropertyValue
    tmp = tempfile.NamedTemporaryFile()

    # Strictly sanitize filename since Content-Disposition is really fussy
    filename = re.sub(
        '[^A-Za-z0-9]+',
        '_',
        strip_unicode_to_ascii(filename)
    )
    if type == "doc":
        properties = (
            PropertyValue("Overwrite",0,True,0),
            PropertyValue("FilterName",0,"MS Word 97",0))
        document.storeToURL("file://" + str(tmp.name), properties)
        content = "application/msword"
        filename += ".doc"
    if type == "docx":
        properties = (
            PropertyValue("Overwrite",0,True,0),
            PropertyValue("FilterName",0,"MS Word 2007 XML",0))
        document.storeToURL("file://" + str(tmp.name), properties)
        content = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename += ".docx"
    elif type == "pdf":
        properties = (
            PropertyValue("Overwrite",0,True,0),
            PropertyValue("FilterName",0,"writer_pdf_Export",0))
        document.storeToURL("file://" + str(tmp.name), properties)
        content = "application/pdf"
        filename += ".pdf"
    elif type == "ods":
        document.storeToURL("file://" + str(tmp.name), ())
        content = "application/vnd.oasis.opendocument.spreadsheet"
        filename += ".ods"
    elif type == "xlsx":
        properties = (
            PropertyValue("Overwrite",0,True,0),
            PropertyValue("FilterName",0,"Calc MS Excel 2007 XML",0))
        document.storeToURL("file://" + str(tmp.name), properties)
        content = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename += ".xlsx"
    elif type == "xls":
        properties = (
            PropertyValue("Overwrite",0,True,0),
            PropertyValue("FilterName",0,"MS Excel 97",0))
        document.storeToURL("file://" + str(tmp.name), properties)
        content = "application/vnd.ms-excel"
        filename += ".xls"
    else:
        document.storeToURL("file://" + str(tmp.name), ())
        content = "application/vnd.oasis.opendocument.text"
        filename += ".odt"
    document.close(True)
    return tmp, filename, content


def save_as(document, filename, type):
    """
    Save file as a particular file type.
    returns just the file using python file()
    """
    tmp, filename, content = uno_save(document, filename, type)
    return file(tmp.name)

def save_to_response(document, filename, type):
    """Saves a file in any format and returns the http response
    type - choices are doc, pdf, ods, xls, and odt"""
    # create temporariy file to store document in
    tmp, filename, content = uno_save(document, filename, type)
    # create http response out of temporariy file.
    wrapper = FileWrapper(file(tmp.name))
    response = HttpResponse(wrapper, content_type=content)
    response['Content-Length'] = os.path.getsize(tmp.name)
    response['Content-Disposition'] = 'attachment; filename=' + filename

    return response


def is_number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


def new_replace_spreadsheet(infile, outfile, data, type="ods", sheets=False):
    """ An appy pod implimentation, appy is too buggy though """
    report = TemplateReport()
    report.data = data
    report.filename = outfile
    return report.pod_save(infile, ext=".ods")


def replace_spreadsheet(infile, outfile, data, type="ods", sheets=False):
    """replaces variables with an array or single entry
    data={}
    data['$TEST'] = ['worked yay', 'second']
    So in the docment if cell(1,1) contained $TEST, that cell would be
    placed by data['$TEST'][0]
    the cell (1,2) would be data['$TEST'][0]
    returns a django HttpResponse of the file
    """
    document = uno_open(infile)
    sheets = document.getSheets()

    i = 0
    while i < sheets.getCount():
        sheet = sheets.getByIndex(i)
        i += 1
        search = sheet.createSearchDescriptor()
        #Do a loop of the data and replace the content.
        for find,replace in data.items():
            search.SearchString = unicode(find)
            search.SearchCaseSensitive = True
            #search.SearchWords = True
            found = sheet.findFirst( search )
            while found:
                x = found.CellAddress.Column
                y = found.CellAddress.Row
                original = sheet.getCellByPosition(x, y)
                if isinstance(data[find], list):
                    for item in data[find]:
                        cell = sheet.getCellByPosition(x, y)
                        try:
                            cell.CellStyle = original.CellStyle
                            cell.CellBackColor = original.CellBackColor
                            cell.CharFont = original.CharFont
                            if is_number(item):
                                cell.Value = item
                            else:
                                cell.String = item
                        except: ""
                        y += 1
                else:
                    found.String = string.replace( found.String, unicode(find),unicode(replace))
                found = sheet.findNext(found.End, search)

    return save_to_response(document, outfile, type)
