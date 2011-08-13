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
import os, os.path, sys, zipfile, re, shutil
import appy.shared.test
from appy.shared.test import TesterError
from appy.shared.utils import FolderDeleter
from appy.pod.odf_parser import OdfEnvironment, OdfParser
from appy.pod.renderer import Renderer
from appy.pod import XML_SPECIAL_CHARS

# TesterError-related constants ------------------------------------------------
TEMPLATE_NOT_FOUND = 'Template file "%s" was not found.'
CONTEXT_NOT_FOUND = 'Context file "%s" was not found.'
EXPECTED_RESULT_NOT_FOUND = 'Expected result "%s" was not found.'

# ------------------------------------------------------------------------------
class AnnotationsRemover(OdfParser):
    '''This parser is used to remove from content.xml and styles.xml the
       Python tracebacks that may be dumped into OpenDocument annotations by
       pod when generating errors. Indeed, those tracebacks contain lot of
       machine-specific info, like absolute paths to the python files, etc.'''
    def __init__(self, env, caller):
        OdfParser.__init__(self, env, caller)
        self.res = u''
        self.inAnnotation = False # Are we parsing an annotation ?
        self.textEncountered = False # Within an annotation, have we already
        # met a text ?
        self.ignore = False # Must we avoid dumping the current tag/content
        # into the result ?
    def startElement(self, elem, attrs):
        e = OdfParser.startElement(self, elem, attrs)
        # Do we enter into an annotation ?
        if elem == '%s:annotation' % e.ns(e.NS_OFFICE):
            self.inAnnotation = True
            self.textEncountered = False
        elif elem == '%s:p' % e.ns(e.NS_TEXT):
            if self.inAnnotation:
                if not self.textEncountered:
                    self.textEncountered = True
                else:
                    self.ignore = True
        if not self.ignore:
            self.res += '<%s' % elem
            for attrName, attrValue in attrs.items():
                self.res += ' %s="%s"' % (attrName, attrValue)
            self.res += '>'
    def endElement(self, elem):
        e = OdfParser.endElement(self, elem)
        if elem == '%s:annotation' % e.ns(e.NS_OFFICE):
            self.inAnnotation = False
            self.ignore = False
        if not self.ignore:
            self.res += '</%s>' % elem
    def characters(self, content):
        e = OdfParser.characters(self, content)
        if not self.ignore:
            for c in content:
                if XML_SPECIAL_CHARS.has_key(c):
                    self.res += XML_SPECIAL_CHARS[c]
                else:
                    self.res += c
    def getResult(self):
        return self.res

# ------------------------------------------------------------------------------
class Test(appy.shared.test.Test):
    '''Abstract test class.'''
    interestingOdtContent = ('content.xml', 'styles.xml')
    def __init__(self, testData, testDescription, testFolder, config, flavour):
        appy.shared.test.Test.__init__(self, testData, testDescription,
                                       testFolder, config, flavour)
        self.templatesFolder = os.path.join(self.testFolder, 'templates')
        self.contextsFolder = os.path.join(self.testFolder, 'contexts')
        self.resultsFolder = os.path.join(self.testFolder, 'results')
        self.result = None
    def getContext(self, contextName):
        '''Gets the objects that are in the context.'''
        contextPy = os.path.join(self.contextsFolder, contextName + '.py')
        if not os.path.exists(contextPy):
            raise TesterError(CONTEXT_NOT_FOUND % contextPy)
        contextPkg = 'appy.pod.test.contexts.%s' % contextName
        exec 'import %s' % contextPkg
        exec 'context = dir(%s)' % contextPkg
        res = {}
        for elem in context:
            if not elem.startswith('__'):
                exec 'res[elem] = %s.%s' % (contextPkg, elem)
        return res
    def do(self):
        self.result = os.path.join(
            self.tempFolder, '%s.%s' % (
                self.data['Name'], self.data['Result']))
        # Get the path to the template to use for this test
        template = os.path.join(self.templatesFolder,
                                self.data['Template'] + '.odt')
        if not os.path.exists(template):
            raise TesterError(TEMPLATE_NOT_FOUND % template)
        # Get the context
        context = self.getContext(self.data['Context'])
        # Get the OpenOffice port
        ooPort = self.data['OpenOfficePort']
        pythonWithUno = self.config['pythonWithUnoPath']
        # Get the styles mapping
        stylesMapping = eval('{' + self.data['StylesMapping'] + '}')
        # Mmh, dicts are not yet managed by RtfTablesParser
        # Call the renderer.
        Renderer(template, context, self.result, ooPort=ooPort,
                 pythonWithUnoPath=pythonWithUno,
                 stylesMapping=stylesMapping).run()
        # Store all result files
        # I should allow to do this from an option given to Tester.py: this code
        # keeps in a separate folder the odt results of all ran tests.
        #tempFolder2 = '%s/sevResults' % self.testFolder
        #if not os.path.exists(tempFolder2):
        #    os.mkdir(tempFolder2)
        #print 'Result is', self.result, 'temp folder 2 is', tempFolder2
        #shutil.copy(self.result, tempFolder2)
    def getOdtContent(self, odtFile):
        '''Creates in the temp folder content.xml and styles.xml extracted
           from p_odtFile.'''
        contentXml = None
        stylesXml = None
        if odtFile == self.result:
            filePrefix = 'actual'
        else:
            filePrefix = 'expected'
        zipFile = zipfile.ZipFile(odtFile)
        for zippedFile in zipFile.namelist():
            if zippedFile in self.interestingOdtContent:
                f = file(os.path.join(self.tempFolder,
                                      '%s.%s' % (filePrefix, zippedFile)), 'wb')
                fileContent = zipFile.read(zippedFile)
                if zippedFile == 'content.xml':
                    # Sometimes, in annotations, there are Python tracebacks.
                    # Those tracebacks include the full path to the Python
                    # files, which of course may be different from one machine
                    # to the other. So we remove those paths.
                    annotationsRemover = AnnotationsRemover(
                       OdfEnvironment(), self)
                    annotationsRemover.parse(fileContent)
                    fileContent = annotationsRemover.getResult()
                f.write(fileContent.encode('utf-8'))
                f.close()
        zipFile.close()
    def checkResult(self):
        '''r_ is False if the test succeeded.'''
        # Get styles.xml and content.xml from the actual result
        res = False
        self.getOdtContent(self.result)
        # Get styles.xml and content.xml from the expected result
        expectedResult = os.path.join(self.resultsFolder,
                                      self.data['Name'] + '.odt')
        if not os.path.exists(expectedResult):
            raise TesterError(EXPECTED_RESULT_NOT_FOUND % expectedResult)
        self.getOdtContent(expectedResult)
        for fileName in self.interestingOdtContent:
            diffOccurred = self.compareFiles(
                os.path.join(self.tempFolder, 'actual.%s' % fileName),
                os.path.join(self.tempFolder, 'expected.%s' % fileName),
                areXml=True, xmlTagsToIgnore=(
                   (OdfEnvironment.NS_DC, 'date'),
                   (OdfEnvironment.NS_STYLE, 'style')),
                xmlAttrsToIgnore=('draw:name','text:name','text:bullet-char'),
                encoding='utf-8')
            if diffOccurred:
                res = True
                break
        return res

# Concrete test classes --------------------------------------------------------
class NominalTest(Test):
    '''Tests an application model.'''
    def __init__(self, testData, testDescription, testFolder, config, flavour):
        Test.__init__(self, testData, testDescription, testFolder, config,
                      flavour)

class ErrorTest(Test):
    '''Tests an application model.'''
    def __init__(self, testData, testDescription, testFolder, config, flavour):
        Test.__init__(self, testData, testDescription, testFolder, config,
                      flavour)
    def onError(self):
        '''Compares the error that occurred with the expected error.'''
        Test.onError(self)
        return not self.isExpectedError(self.data['Message'])

# ------------------------------------------------------------------------------
class PodTestFactory(appy.shared.test.TestFactory):
    def createTest(testData, testDescription, testFolder, config, flavour):
        if testData.table.instanceOf('ErrorTest'):
            test = ErrorTest(testData, testDescription, testFolder, config,
                              flavour)
        else:
            test = NominalTest(testData, testDescription, testFolder, config,
                               flavour)
        return test
    createTest = staticmethod(createTest)

# ------------------------------------------------------------------------------
class PodTester(appy.shared.test.Tester):
    def __init__(self, testPlan):
        appy.shared.test.Tester.__init__(self, testPlan, [], PodTestFactory)

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    PodTester('Tests.rtf').run()
# ------------------------------------------------------------------------------
