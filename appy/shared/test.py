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
import os, os.path, sys, time
from optparse import OptionParser
from appy.shared.utils import FolderDeleter, Traceback
from appy.shared.errors import InternalError
from appy.shared.rtf import RtfTablesParser
from appy.shared.xml_parser import XmlComparator

# ------------------------------------------------------------------------------
class TesterError(Exception): pass

# TesterError-related constants
WRONG_TEST_PLAN = 'The test plan you specified does not correspond to an ' \
                  'existing RTF file.'
_FLAVOUR = 'A flavour represents a test configuration.'
FLAVOURS_NOT_LIST = 'The flavours specified must be a list or tuple of ' \
                    'string. ' + _FLAVOUR
FLAVOUR_NOT_STRING = 'Each specified flavour must be a string. ' + _FLAVOUR
WRONG_TEST_FACTORY = 'You must give a test factory that inherits from the ' \
                     'abstract "appy.shared.test.TestFactory" class.'
CREATE_TEST_NOT_OVERRIDDEN = 'The appy.shared.test.TestFactory.createTest ' \
                             'method must be overridden in your concrete ' \
                             'TestFactory.'
MAIN_TABLE_NOT_FOUND = 'No table "TestSuites" found in test plan "%s".'
MAIN_TABLE_MALFORMED = 'The "TestSuites" table must have at least two ' \
                       'columns, named "Name" and "Description".'
TEST_SUITE_NOT_FOUND = 'Table "%s.descriptions" and/or "%s.data" were not ' \
                       'found.'
TEST_SUITE_MALFORMED = 'Tables "%s.descriptions" and "%s.data" do not have ' \
                       'the same length. For each test in "%s.data", You ' \
                       'should have one line in "%s.descriptions" describing ' \
                       'the test.'
FILE_NOT_FOUND = 'File to compare "%s" was not found.'
WRONG_ARGS = 'You must specify as unique argument the configuration flavour ' \
             'you want, which may be one of %s.'
WRONG_FLAVOUR = 'Wrong flavour "%s". Flavour must be one of %s.'

# InternalError-related constants
TEST_REPORT_SINGLETON_ERROR = 'You can only use the TestReport constructor ' \
                              'once. After that you can access the single ' \
                              'TestReport instance via the TestReport.' \
                              'instance static member.'

# ------------------------------------------------------------------------------
class TestReport:
    instance = None
    def __init__(self, testReportFileName, verbose):
        if TestReport.instance == None:
            self.report = open(testReportFileName, 'w')
            self.verbose = verbose
            TestReport.instance = self
        else:
            raise InternalError(TEST_REPORT_SINGLETON_ERROR)
    def say(self, msg, force=False, encoding=None):
        if self.verbose or force:
            print(msg)
        if encoding:
            self.report.write(msg.encode(encoding))
        else:
            self.report.write(msg)
        self.report.write('\n')
    def close(self):
        self.report.close()

# ------------------------------------------------------------------------------
class Test:
    '''Abstract test class.'''
    def __init__(self, testData, testDescription, testFolder, config, flavour):
        self.data = testData
        self.description = testDescription
        self.testFolder = testFolder
        self.tempFolder = None
        self.report = TestReport.instance
        self.errorDump = None
        self.config = config
        self.flavour = flavour
    def compareFiles(self, expected, actual, areXml=False, xmlTagsToIgnore=(),
                     xmlAttrsToIgnore=(), encoding=None):
        '''Compares 2 files. r_ is True if files are different. The differences
        are written in the test report.'''
        for f in expected, actual:
            assert os.path.exists(f), TesterError(FILE_NOT_FOUND % f)
        # Expected result (may be different according to flavour)
        if self.flavour:
            expectedFlavourSpecific = '%s.%s' % (expected, self.flavour)
            if os.path.exists(expectedFlavourSpecific):
                expected = expectedFlavourSpecific
        # Perform the comparison
        comparator = XmlComparator(actual, expected, areXml, xmlTagsToIgnore,
                                   xmlAttrsToIgnore)
        return not comparator.filesAreIdentical(
            report=self.report, encoding=encoding)
    def run(self):
        self.report.say('-' * 79)
        self.report.say('- Test %s.' % self.data['Name'])
        self.report.say('- %s\n' % self.description)
        # Prepare test data
        self.tempFolder = os.path.join(self.testFolder, 'temp')
        if os.path.exists(self.tempFolder):
            time.sleep(0.3) # Sometimes I can't remove it, so I wait
            FolderDeleter.delete(self.tempFolder)
        os.mkdir(self.tempFolder)
        try:
            self.do()
            self.report.say('Checking result...')
            testFailed = self.checkResult()
        except:
            testFailed = self.onError()
        self.finalize()
        return testFailed
    def do(self):
        '''Concrete part of the test. Must be overridden.'''
    def checkResult(self):
        '''r_ is False if the test succeeded.'''
        return True
    def onError(self):
        '''What must happen when an exception is raised during test
           execution? Returns True if the test failed.'''
        self.errorDump = Traceback.get()
        self.report.say('Exception occurred:')
        self.report.say(self.errorDump)
        return True
    def finalize(self):
        '''Performs sme cleaning actions after test execution.'''
        pass
    def isExpectedError(self, expectedMessage):
        '''An exception was thrown. So check if the actual error message
           (stored in self.errorDump) corresponds to the p_expectedMessage.'''
        res = True
        for line in expectedMessage:
            if (self.errorDump.find(line) == -1):
                res = False
                self.report.say('"%s" not found among error dump.' % line)
                break
        return res

# ------------------------------------------------------------------------------
class TestFactory:
    def createTest(testData, testDescription, testFolder, config, flavour):
        '''This method allows you to create tests that are instances of classes
           that you create. Those classes must be children of
           appy.shared.test.Test. m_createTest must return a Test instance and
           is called every time a test definition is encountered in the test
           plan.'''
        raise TesterError(CREATE_TEST_NOT_OVERRIDDEN)
    createTest = staticmethod(createTest)

# ------------------------------------------------------------------------------
class Tester:
    def __init__(self, testPlan, flavours, testFactory):
        # Check test plan
        if (not os.path.exists(testPlan)) or (not os.path.isfile(testPlan)) \
           or (not testPlan.endswith('.rtf')):
            raise TesterError(WRONG_TEST_PLAN)
        self.testPlan = testPlan
        self.testFolder = os.path.abspath(os.path.dirname(testPlan))
        # Check flavours
        if (not isinstance(flavours, list)) and \
           (not isinstance(flavours, tuple)):
            raise TesterError(FLAVOURS_NOT_LIST)
        for flavour in flavours:
            if not isinstance(flavour, basestring):
                raise TesterError(FLAVOUR_NOT_STRING)
        self.flavours = flavours
        self.flavour = None
        # Check test factory
        if not issubclass(testFactory, TestFactory):
            raise TesterError(WRONG_TEST_FACTORY)
        self.testFactory = testFactory
        self.getOptions()
        self.report = TestReport('%s/Tester.report.txt' % self.testFolder,
                                 self.verbose)
        self.report.say('Parsing RTF file... ')
        t1 = time.time()
        self.tables = RtfTablesParser(testPlan).parse()
        t2 = time.time() - t1
        self.report.say('Done in %d seconds' % t2)
        self.config = None
        ext = ''
        if self.flavour:
            ext = '.%s' % self.flavour
        configTableName = 'Configuration%s' % ext
        if self.tables.has_key(configTableName):
            self.config = self.tables[configTableName].asDict()
        self.tempFolder = os.path.join(self.testFolder, 'temp')
        if os.path.exists(self.tempFolder):
            FolderDeleter.delete(self.tempFolder)
        self.nbOfTests = 0
        self.nbOfSuccesses = 0
        self.nbOfIgnoredTests = 0
    def getOptions(self):
        optParser = OptionParser()
        optParser.add_option("-v", "--verbose", action="store_true",
                             help="Dumps the whole test report on stdout")
        optParser.add_option("-k", "--keepTemp", action="store_true", help = \
                             "Keep the temp folder, in order to be able to " \
                             "copy some results and make them expected " \
                             "results when needed.")
        (options, args) = optParser.parse_args()
        if self.flavours:
            if len(args) != 1:
                raise TesterError(WRONG_ARGS % self.flavours)
            self.flavour = args[0]
            if not self.flavour in self.flavours:
                raise TesterError(WRONG_FLAVOUR % (self.flavour, self.flavours))
        self.verbose = options.verbose == True
        self.keepTemp = options.keepTemp == True
    def runSuite(self, suite):
        self.report.say('*' * 79)
        self.report.say('* Suite %s.' % suite['Name'])
        self.report.say('* %s\n' % suite['Description'])
        i = -1
        for testData in self.tables['%s.data' % suite['Name']]:
            self.nbOfTests += 1
            i += 1
            if testData['Name'].startswith('_'):
                self.nbOfIgnoredTests += 1
            else:
                description = self.tables['%s.descriptions' % \
                                          suite['Name']][i]['Description']
                test = self.testFactory.createTest(
                    testData, description, self.testFolder, self.config,
                    self.flavour)
                testFailed = test.run()
                if not self.verbose:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                if testFailed:
                    self.report.say('Test failed.\n')
                else:
                    self.report.say('Test successful.\n')
                    self.nbOfSuccesses += 1
    def run(self):
        assert self.tables.has_key('TestSuites'), \
               TesterError(MAIN_TABLE_NOT_FOUND % self.testPlan)
        for testSuite in self.tables['TestSuites']:
            if (not testSuite.has_key('Name')) or \
               (not testSuite.has_key('Description')):
                raise TesterError(MAIN_TABLE_MALFORMED)
            if testSuite['Name'].startswith('_'):
                tsName = testSuite['Name'][1:]
                tsIgnored = True
            else:
                tsName = testSuite['Name']
                tsIgnored = False
            assert self.tables.has_key('%s.descriptions' % tsName) \
                   and self.tables.has_key('%s.data' % tsName), \
                   TesterError(TEST_SUITE_NOT_FOUND % (tsName, tsName))
            assert len(self.tables['%s.descriptions' % tsName]) == \
                   len(self.tables['%s.data' % tsName]), \
                   TesterError(TEST_SUITE_MALFORMED % ((tsName,)*4))
            if tsIgnored:
                nbOfIgnoredTests = len(self.tables['%s.data' % tsName])
                self.nbOfIgnoredTests += nbOfIgnoredTests
                self.nbOfTests += nbOfIgnoredTests
            else:
                self.runSuite(testSuite)
        self.finalize()
    def finalize(self):
        msg = '%d/%d successful test(s)' % \
              (self.nbOfSuccesses, (self.nbOfTests-self.nbOfIgnoredTests))
        if self.nbOfIgnoredTests >0:
            msg += ', but %d ignored test(s) not counted' % \
                   self.nbOfIgnoredTests
        msg += '.'
        self.report.say(msg, force=True)
        self.report.close()
        if not self.keepTemp:
            if os.path.exists(self.tempFolder):
                FolderDeleter.delete(self.tempFolder)
# ------------------------------------------------------------------------------
