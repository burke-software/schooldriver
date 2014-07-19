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
import sys, os, os.path, time, signal
from optparse import OptionParser

htmlFilters = {'odt': 'HTML (StarWriter)',
               'ods': 'HTML (StarCalc)',
               'odp': 'impress_html_Export'}

FILE_TYPES = {'odt': 'writer8',
              'ods': 'calc8',
              'odp': 'impress8',
              'htm': htmlFilters, 'html': htmlFilters,
              'rtf': 'Rich Text Format',
              'txt': 'Text',
              'csv': 'Text - txt - csv (StarCalc)',
              'pdf': {'odt': 'writer_pdf_Export',  'ods': 'calc_pdf_Export',
                      'odp': 'impress_pdf_Export', 'htm': 'writer_pdf_Export',
                      'html': 'writer_pdf_Export', 'rtf': 'writer_pdf_Export',
                      'txt': 'writer_pdf_Export', 'csv': 'calc_pdf_Export',
                      'swf': 'draw_pdf_Export', 'doc': 'writer_pdf_Export',
                      'xls': 'calc_pdf_Export', 'ppt': 'impress_pdf_Export',
                      'docx': 'writer_pdf_Export', 'xlsx': 'calc_pdf_Export'
                      },
              'swf': 'impress_flash_Export',
              'doc': 'MS Word 97',
              'xls': 'MS Excel 97',
              'ppt': 'MS PowerPoint 97',
              'docx': 'MS Word 2007 XML',
              'xlsx': 'Calc MS Excel 2007 XML',
}
# Conversion from odt to odt does not make any conversion, but updates indexes
# and linked documents.

# ------------------------------------------------------------------------------
class ConverterError(Exception): pass

# ConverterError-related messages ----------------------------------------------
DOC_NOT_FOUND = 'Document "%s" was not found.'
URL_NOT_FOUND = 'Doc URL "%s" is wrong. %s'
BAD_RESULT_TYPE = 'Bad result type "%s". Available types are %s.'
CANNOT_WRITE_RESULT = 'I cannot write result "%s". %s'
CONNECT_ERROR = 'Could not connect to LibreOffice on port %d. UNO ' \
                '(LibreOffice API) says: %s.'

# Some constants ---------------------------------------------------------------
DEFAULT_PORT = 2002

# ------------------------------------------------------------------------------
class Converter:
    '''Converts a document readable by LibreOffice into pdf, doc, txt, rtf...'''
    exeVariants = ('soffice.exe', 'soffice')
    pathReplacements = {'program files': 'progra~1',
                        'openoffice.org 1': 'openof~1',
                        'openoffice.org 2': 'openof~1',
                        }
    def __init__(self, docPath, resultType, port=DEFAULT_PORT):
        self.port = port
        self.docUrl, self.docPath = self.getInputUrls(docPath)
        self.inputType = os.path.splitext(docPath)[1][1:].lower()
        self.resultType = resultType
        self.resultFilter = self.getResultFilter()
        self.resultUrl = self.getResultUrl()
        self.loContext = None
        self.oo = None # The LibreOffice application object
        self.doc = None # The LibreOffice loaded document

    def getInputUrls(self, docPath):
        '''Returns the absolute path of the input file. In fact, it returns a
           tuple with some URL version of the path for OO as the first element
           and the absolute path as the second element.''' 
        import unohelper
        if not os.path.exists(docPath) and not os.path.isfile(docPath):
            raise ConverterError(DOC_NOT_FOUND % docPath)
        docAbsPath = os.path.abspath(docPath)
        # Return one path for OO, one path for me.
        return unohelper.systemPathToFileUrl(docAbsPath), docAbsPath

    def getResultFilter(self):
        '''Based on the result type, identifies which OO filter to use for the
           document conversion.'''
        if self.resultType in FILE_TYPES:
            res = FILE_TYPES[self.resultType]
            if isinstance(res, dict):
                res = res[self.inputType]
        else:
            raise ConverterError(BAD_RESULT_TYPE % (self.resultType,
                                                    FILE_TYPES.keys()))
        return res

    def getResultUrl(self):
        '''Returns the path of the result file in the format needed by LO. If
           the result type and the input type are the same (ie the user wants to
           refresh indexes or some other action and not perform a real
           conversion), the result file is named
                           <inputFileName>.res.<resultType>.

           Else, the result file is named like the input file but with a
           different extension:
                           <inputFileName>.<resultType>
        '''
        import unohelper
        baseName = os.path.splitext(self.docPath)[0]
        if self.resultType != self.inputType:
            res = '%s.%s' % (baseName, self.resultType)
        else:
            res = '%s.res.%s' % (baseName, self.resultType)
        try:
            f = open(res, 'w')
            f.write('Hello')
            f.close()
            os.remove(res)
            return unohelper.systemPathToFileUrl(res)
        except (OSError, IOError):
            e = sys.exc_info()[1]
            raise ConverterError(CANNOT_WRITE_RESULT % (res, e))

    def connect(self):
        '''Connects to LibreOffice'''
        if os.name == 'nt':
            import socket
        import uno
        from com.sun.star.connection import NoConnectException
        try:
            # Get the uno component context from the PyUNO runtime
            localContext = uno.getComponentContext()
            # Create the UnoUrlResolver
            resolver = localContext.ServiceManager.createInstanceWithContext(
                "com.sun.star.bridge.UnoUrlResolver", localContext)
            # Connect to the running office
            self.loContext = resolver.resolve(
                'uno:socket,host=localhost,port=%d;urp;StarOffice.' \
                'ComponentContext' % self.port)
            # Is seems that we can't define a timeout for this method.
            # I need it because, for example, when a web server already listens
            # to the given port (thus, not a LibreOffice instance), this method
            # blocks.
            smgr = self.loContext.ServiceManager
            # Get the central desktop object
            self.oo = smgr.createInstanceWithContext(
                'com.sun.star.frame.Desktop', self.loContext)
        except NoConnectException:
            e = sys.exc_info()[1]
            raise ConverterError(CONNECT_ERROR % (self.port, e))

    def updateOdtDocument(self):
        '''If the input file is an ODT document, we will perform 2 tasks:
           1) Update all annexes;
           2) Update sections (if sections refer to external content, we try to
              include the content within the result file)
        '''
        from com.sun.star.lang import IndexOutOfBoundsException
        # I need to use IndexOutOfBoundsException because sometimes, when
        # using sections.getCount, UNO returns a number that is bigger than
        # the real number of sections (this is because it also counts the
        # sections that are present within the sub-documents to integrate)
        # Update all indexes
        indexes = self.doc.getDocumentIndexes()
        indexesCount = indexes.getCount()
        if indexesCount != 0:
            for i in range(indexesCount):
                try:
                    indexes.getByIndex(i).update()
                except IndexOutOfBoundsException:
                    pass
        # Update sections
        self.doc.updateLinks()
        sections = self.doc.getTextSections()
        sectionsCount = sections.getCount()
        if sectionsCount != 0:
            for i in range(sectionsCount-1, -1, -1):
                # I must walk into the section from last one to the first
                # one. Else, when "disposing" sections, I remove sections
                # and the remaining sections other indexes.
                try:
                    section = sections.getByIndex(i)
                    if section.FileLink and section.FileLink.FileURL:
                        section.dispose() # This method removes the
                        # <section></section> tags without removing the content
                        # of the section. Else, it won't appear.
                except IndexOutOfBoundsException:
                    pass
        
    def loadDocument(self):
        from com.sun.star.lang import IllegalArgumentException, \
                                      IndexOutOfBoundsException
        from com.sun.star.beans import PropertyValue
        try:
            # Loads the document to convert in a new hidden frame
            prop = PropertyValue(); prop.Name = 'Hidden'; prop.Value = True
            if self.inputType == 'csv':
                # Give some additional params if we need to open a CSV file
                prop2 = PropertyValue()
                prop2.Name = 'FilterFlags'
                prop2.Value = '59,34,76,1'
                #prop2.Name = 'FilterData'
                #prop2.Value = 'Any'
                props = (prop, prop2)
            else:
                props = (prop,)
            self.doc = self.oo.loadComponentFromURL(self.docUrl, "_blank", 0,
                                                    props)
            if self.inputType == 'odt':
                # Perform additional tasks for odt documents
                self.updateOdtDocument()
            try:
                self.doc.refresh()
            except AttributeError:
                pass
        except IllegalArgumentException:
            e = sys.exc_info()[1]
            raise ConverterError(URL_NOT_FOUND % (self.docPath, e))

    def convertDocument(self):
        '''Calls LO to perform a document conversion. Note that the conversion
           is not really done if the source and target documents have the same
           type.'''
        properties = []
        from com.sun.star.beans import PropertyValue
        prop = PropertyValue()
        prop.Name = 'FilterName'
        prop.Value = self.resultFilter
        properties.append(prop)
        if self.resultType == 'csv':
            # For CSV export, add options (separator, etc)
            optionsProp = PropertyValue()
            optionsProp.Name = 'FilterOptions'
            optionsProp.Value = '59,34,76,1'
            properties.append(optionsProp)
        self.doc.storeToURL(self.resultUrl, tuple(properties))

    def run(self):
        '''Connects to LO, does the job and disconnects.'''
        self.connect()
        self.loadDocument()
        self.convertDocument()
        self.doc.close(True)

# ConverterScript-related messages ---------------------------------------------
WRONG_NB_OF_ARGS = 'Wrong number of arguments.'
ERROR_CODE = 1

# Class representing the command-line program ----------------------------------
class ConverterScript:
    usage = 'usage: python converter.py fileToConvert outputType [options]\n' \
            '   where fileToConvert is the absolute or relative pathname of\n' \
            '         the file you want to convert (or whose content like\n' \
            '         indexes need to be refreshed);\n'\
            '   and   outputType is the output format, that must be one of\n' \
            '         %s.\n' \
            ' "python" should be a UNO-enabled Python interpreter (ie the ' \
            '  one which is included in the LibreOffice distribution).' % \
            str(FILE_TYPES.keys())
    def run(self):
        optParser = OptionParser(usage=ConverterScript.usage)
        optParser.add_option("-p", "--port", dest="port",
                             help="The port on which LibreOffice runs " \
                             "Default is %d." % DEFAULT_PORT,
                             default=DEFAULT_PORT, metavar="PORT", type='int')
        (options, args) = optParser.parse_args()
        if len(args) != 2:
            sys.stderr.write(WRONG_NB_OF_ARGS)
            sys.stderr.write('\n')
            optParser.print_help()
            sys.exit(ERROR_CODE)
        converter = Converter(args[0], args[1], options.port)
        try:
            converter.run()
        except ConverterError:
            e = sys.exc_info()[1]
            sys.stderr.write(str(e))
            sys.stderr.write('\n')
            optParser.print_help()
            sys.exit(ERROR_CODE)

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    ConverterScript().run()
# ------------------------------------------------------------------------------
