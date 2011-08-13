from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

import uno
import os
import string
import tempfile
from com.sun.star.beans import PropertyValue
from com.sun.star.style.BreakType import PAGE_BEFORE, PAGE_AFTER
from copy import deepcopy

def findandreplace(document, search, find, replace):
    """This function searches and replaces. Create search, call function findFirst, and finally replace what we found."""
    #What to search for
    search.SearchString = unicode(find)
    search.SearchCaseSensitive = True
    #search.SearchWords = True
    found = document.findFirst( search )
    while found:
        found.String = string.replace( found.String, unicode(find),unicode(replace))
        found = document.findNext( found.End, search)


def uno_open(file):
    """This function should really just be in uno
    file -- Location of the file to open
    returns an uno document
    """      
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    context = resolver.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
    desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
    return desktop.loadComponentFromURL("file://" + str(file) ,"_blank", 0, ())


def uno_save(document, filename, type):
    """ Save document
    document: desktop.loadComponentFromURL
    filename: filename of output without ext
    type: extension, example odt
    """
    tmp = tempfile.NamedTemporaryFile()
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


def replace_once_report(infile, outfile, data, type="doc"):
    """Replace words in a file use like this
    data={}
    data['$TEST']=['first','second','third',]
    It replaces the first instance of $TEST with first, second with second, etc
    returns a django HttpResponse of the file
    """
    
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    context = resolver.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
    desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
    
    document = desktop.loadComponentFromURL( "private:factory/swriter", "_blank", 0, () )
    doc_cursor = document.Text.createTextCursor()
    
    template = desktop.loadComponentFromURL("file://" + str(infile) ,"_blank", 0, ())
    
    cursor = template.Text.createTextCursor()
    search = template.createSearchDescriptor()
    
    doc_cursor.gotoEnd(False)
    tmp, filename, content = uno_save(template, outfile, type)
    doc_cursor.insertDocumentFromURL("file://" + str(tmp.name), ())
    #Do a loop of the data and replace the content.
    for find,replace in data.items():
        search.SearchString = unicode(find)
        found = None
        exist_in_template = True
        data_i = 0
        while data_i < len(replace) and exist_in_template:
            if data_i == 0:
                found = document.findFirst( search )
                if not found:
                    exist_in_template = False
            else:
                found = document.findFirst( search )
                
            if found:
                found.String = string.replace( found.String, unicode(find),unicode(replace[data_i]))
            elif exist_in_template == True:
                doc_cursor.gotoEnd(False)
                doc_cursor.insertDocumentFromURL("file://" + str(tmp.name), ())
                data_i -= 1
            
            data_i += 1
        # now destroy any remaining variables that can't be filled
        findandreplace(document,search,unicode(find),"")
    
    return save_to_response(document, outfile, type)
    

def replace_report_table(infile, outfile, data, tables, type="doc"):
    """Replace words in a file and replace tables rows, inserting rows as needed
    data={}
    data['$TEST']='worked yay'
    tables = {}
    students = ['Joe', 'Tim', 'Aly']
    grades = ['A', 'C', 'B']
    tables['table_name']={'$student': students, '$grade': grades}
    returns a django HttpResponse of the file
    """
    document = uno_open(infile) # custom function that just opens a file
    
    cursor = document.Text.createTextCursor()

    search = document.createSearchDescriptor()
    #Do a loop of the data and replace the content.
    for find,replace in data.items():
        findandreplace(document,search,unicode(find),unicode(replace))
     
    # for each table in our tables    
    for table_name, table in tables.iteritems():
        otables = document.TextTables
        otable = otables.getByName(table_name)
        orows = otable.Rows
        num_rows = orows.Count
        data_array = otable.DataArray
        
        # convert to list because tuples are hard to work with
        data_list = []
        for tuple_row in data_array:
            data_list.append(list(tuple_row))

        i = 1 # TODO use num_rows to handle any row count 
        last_row = num_rows
        
        to_add = 0
        # get number of times to add values (on first dict item)
        for replace, replace_with in table.iteritems():
            if len(replace_with) > to_add:
                to_add = len(replace_with)        
        
        #run until finished (no more data to replace)
        while i <= to_add:
            # clone last row (which contains variables to replace)
            data_list.append(deepcopy(data_list[len(data_list) - 1]))
            # for cell in data_list[second to last row]
            icell = 0
            for cell in data_list[i]:
                # for each variable to replace, array to replace with
                # basically search and replace
                for replace, replace_with in table.iteritems():
                    if str(replace) == str(cell):
                        try: data_list[i][icell] = replace_with[i-1]
                        except: data_list[i][icell] = ""
                icell += 1
            i += 1

        # remove last row (which is a copy of the variables)    
        data_list.pop()
        # add rows in the ooo table

        if to_add > 1:
            orows.insertByIndex(num_rows, to_add - 1)
        elif to_add == 0:
            orows.removeByIndex(num_rows-1, 1)
        
        # convert list back into tuple
        data_array = ()
        for x in data_list:
            data_array += (tuple(x),)
        
        otable.DataArray = data_array

    return save_to_response(document, outfile, type) # custom function that returns the file as a Django response



def mail_merge(infile, outfile, data, type="doc"):
    """ Acts like a mail merge with a template file and data
        Does not assume page breaks in between pages
        page1={}
        page2={}
        page1["$students"]="Joe Student"
        page2["$students"]="Jane Student"
        data = []
        data.append(page1)
        data.append(page2)
    """
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    context = resolver.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
    desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
    
    document = desktop.loadComponentFromURL( "private:factory/swriter", "_blank", 0, () )
    doc_cursor = document.Text.createTextCursor()
    
    for record in data:
        template = desktop.loadComponentFromURL("file://" + str(infile) ,"_blank", 0, ())
        
        cursor = template.Text.createTextCursor()
        search = template.createSearchDescriptor()
        #Do a loop of the data and replace the content.
        for find,replace in record.items():
            findandreplace(template,search,unicode(find),unicode(replace))
        
        tmp, filename, content = uno_save(template, outfile, type)

        doc_cursor.gotoEnd(False)
        doc_cursor.insertDocumentFromURL("file://" + str(tmp.name), ())
    return save_to_response(document, outfile, type)
    

def is_number(x):
	try:
		float(x)
		return True
	except ValueError:
		return False
        
    
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
