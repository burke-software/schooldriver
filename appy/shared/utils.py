# -*- coding: utf-8 -*-
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
import os, os.path, re, time, sys, traceback, unicodedata, shutil
sequenceTypes = (list, tuple)

# ------------------------------------------------------------------------------
class FolderDeleter:
    def delete(dirName):
        '''Recursively deletes p_dirName.'''
        dirName = os.path.abspath(dirName)
        for root, dirs, files in os.walk(dirName, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(dirName)
    delete = staticmethod(delete)

# ------------------------------------------------------------------------------
extsToClean = ('.pyc', '.pyo', '.fsz', '.deltafsz', '.dat', '.log')
def cleanFolder(folder, exts=extsToClean, folders=(), verbose=False):
    '''This function allows to remove, in p_folder and subfolders, any file
       whose extension is in p_exts, and any folder whose name is in
       p_folders.'''
    if verbose: print 'Cleaning folder', folder, '...'
    # Remove files with an extension listed in p_exts
    if exts:
        for root, dirs, files in os.walk(folder):
            for fileName in files:
                ext = os.path.splitext(fileName)[1]
                if (ext in exts) or ext.endswith('~'):
                    fileToRemove = os.path.join(root, fileName)
                    if verbose: print 'Removing file %s...' % fileToRemove
                    os.remove(fileToRemove)
    # Remove folders whose names are in p_folders.
    if folders:
        for root, dirs, files in os.walk(folder):
            for folderName in dirs:
                if folderName in folders:
                    toDelete = os.path.join(root, folderName)
                    if verbose: print 'Removing folder %s...' % toDelete
                    FolderDeleter.delete(toDelete)

# ------------------------------------------------------------------------------
def copyFolder(source, dest, cleanDest=False):
    '''Copies the content of folder p_source to folder p_dest. p_dest is
       created, with intermediary subfolders if required. If p_cleanDest is
       True, it removes completely p_dest if it existed. Else, content of
       p_source will be added to possibly existing content in p_dest, excepted
       if file names corresponds. In this case, file in p_source will overwrite
       file in p_dest.'''
    dest = os.path.abspath(dest)
    # Delete the dest folder if required
    if os.path.exists(dest) and cleanDest:
        FolderDeleter.delete(dest)
    # Create the dest folder if it does not exist
    if not os.path.exists(dest):
        os.makedirs(dest)
    # Copy the content of p_source to p_dest.
    for name in os.listdir(source):
        sourceName = os.path.join(source, name)
        destName = os.path.join(dest, name)
        if os.path.isfile(sourceName):
            # Copy a single file
            shutil.copy(sourceName, destName)
        elif os.path.isdir(sourceName):
            # Copy a subfolder (recursively)
            copyFolder(sourceName, destName)

# ------------------------------------------------------------------------------
def encodeData(data, encoding=None):
    '''Applies some p_encoding to string p_data, but only if an p_encoding is
       specified.'''
    if not encoding: return data
    return data.encode(encoding)

# ------------------------------------------------------------------------------
def copyData(data, target, targetMethod, type='string', encoding=None,
             chunkSize=1024):
    '''Copies p_data to a p_target, using p_targetMethod. For example, it copies
       p_data which is a string containing the binary content of a file, to
       p_target, which can be a HTTP connection or a file object.

       p_targetMethod can be "write" (files) or "send" (HTTP connections) or ...
       p_type can be "string", "file" or "zope". In the latter case it is an
       instance of OFS.Image.File. If p_type is "file", one may, in p_chunkSize,
       specify the amount of bytes transmitted at a time.

       If an p_encoding is specified, it is applied on p_data before copying.

       Note that if the p_target is a Python file, it must be opened in a way
       that is compatible with the content of p_data, ie file('myFile.doc','wb')
       if content is binary.'''
    dump = getattr(target, targetMethod)
    if not type or (type == 'string'): dump(encodeData(data, encoding))
    elif type == 'file':
        while True:
            chunk = data.read(chunkSize)
            if not chunk: break
            dump(encodeData(chunk, encoding))
    elif type == 'zope':
        # A OFS.Image.File instance can be split into several chunks
        if isinstance(data.data, basestring): # One chunk
            dump(encodeData(data.data, encoding))
        else:
            # Several chunks
            data = data.data
            while data is not None:
                dump(encodeData(data.data, encoding))
                data = data.next

# ------------------------------------------------------------------------------
def splitList(l, sub):
    '''Returns a list that was build from list p_l whose elements were
       re-grouped into sub-lists of p_sub elements.

       For example, if l = [1,2,3,4,5] and sub = 3, the method returns
       [ [1,2,3], [4,5] ].'''
    res = []
    i = -1
    for elem in l:
        i += 1
        if (i % sub) == 0:
            # A new sub-list must be created
            res.append([elem])
        else:
            res[-1].append(elem)
    return res

# ------------------------------------------------------------------------------
class Traceback:
    '''Dumps the last traceback into a string.'''
    def get():
        res = ''
        excType, excValue, tb = sys.exc_info()
        tbLines = traceback.format_tb(tb)
        for tbLine in tbLines:
            res += ' %s' % tbLine
        res += ' %s: %s' % (str(excType), str(excValue))
        return res
    get = staticmethod(get)

# ------------------------------------------------------------------------------
def getOsTempFolder():
    tmp = '/tmp'
    if os.path.exists(tmp) and os.path.isdir(tmp):
        res = tmp
    elif os.environ.has_key('TMP'):
        res = os.environ['TMP']
    elif os.environ.has_key('TEMP'):
        res = os.environ['TEMP']
    else:
        raise "Sorry, I can't find a temp folder on your machine."
    return res

def getTempFileName(prefix='', extension=''):
    '''Returns the absolute path to a unique file name in the OS temp folder.
       The caller will then be able to create a file with this name.

       A p_prefix to this file can be provided. If an p_extension is provided,
       it will be appended to the name. Both dotted and not dotted versions
       of p_extension are allowed (ie, ".pdf" or "pdf").'''
    res = '%s/%s_%f' % (getOsTempFolder(), prefix, time.time())
    if extension:
        if extension.startswith('.'): res += extension
        else: res += '.' + extension
    return res

# ------------------------------------------------------------------------------
def executeCommand(cmd):
    '''Executes command p_cmd and returns the content of its stderr.'''
    childStdIn, childStdOut, childStdErr = os.popen3(cmd)
    res = childStdErr.read()
    childStdIn.close(); childStdOut.close(); childStdErr.close()
    return res

# ------------------------------------------------------------------------------
unwantedChars = ('\\', '/', ':', '*', '?', '"', '<', '>', '|', ' ', '\t', "'")
alphaRex = re.compile('[a-zA-Z]')
alphanumRex = re.compile('[a-zA-Z0-9]')
def normalizeString(s, usage='fileName'):
    '''Returns a version of string p_s whose special chars (like accents) have
       been replaced with normal chars. Moreover, if p_usage is:
       * fileName: it removes any char that can't be part of a file name;
       * alphanum: it removes any non-alphanumeric char;
       * alpha: it removes any non-letter char.
    '''
    # We work in unicode. Convert p_s to unicode if not unicode.
    if isinstance(s, str):           s = s.decode('utf-8')
    elif not isinstance(s, unicode): s = unicode(s)
    if usage == 'extractedText':
        # Replace single quotes with blanks.
        s = s.replace("'", " ").replace(u'’', ' ')
    # Remove any special char like accents.
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    # Remove any other char, depending on p_usage.
    if usage == 'fileName':
        # Remove any char that can't be found within a file name under
        # Windows or that could lead to problems with OpenOffice.
        res = ''
        for char in s:
            if char not in unwantedChars: res += char
    elif usage.startswith('alpha'):
        exec 'rex = %sRex' % usage
        res = ''
        for char in s:
            if rex.match(char): res += char
    else:
        res = s
    return res

# ------------------------------------------------------------------------------
def normalizeText(s):
    '''Normalizes p_s: remove special chars, lowerizes it, etc, for indexing
       purposes.'''
    return normalizeString(s, usage='extractedText').strip().lower()

# ------------------------------------------------------------------------------
def formatNumber(n, sep=',', precision=2, tsep=' '):
    '''Returns a string representation of number p_n, which can be a float
       or integer. p_sep is the decimal separator to use. p_precision is the
       number of digits to keep in the decimal part for producing a nice rounded
       string representation. p_tsep is the "thousands" separator.'''
    if n == None: return ''
    # Manage precision
    if precision == None:
        res = str(n)
    else:
        format = '%%.%df' % precision
        res = format % n
    # Use the correct decimal separator
    res = res.replace('.', sep)
    # Insert p_tsep every 3 chars in the integer part of the number
    splitted = res.split(sep)
    res = ''
    if len(splitted[0]) < 4: res = splitted[0]
    else:
        i = len(splitted[0])-1
        j = 0
        while i >= 0:
            j += 1
            res = splitted[0][i] + res
            if (j % 3) == 0:
                res = tsep + res
            i -= 1
    # Add the decimal part if not 0
    if len(splitted) > 1:
        try:
            decPart = int(splitted[1])
            if decPart != 0:
                res += sep + str(decPart)
        except ValueError:
            # This exception may occur when the float value has an "exp"
            # part, like in this example: 4.345e-05
            res += sep + splitted[1]
    return res

# ------------------------------------------------------------------------------
def lower(s):
    '''French-accents-aware variant of string.lower.'''
    isUnicode = isinstance(s, unicode)
    if not isUnicode: s = s.decode('utf-8')
    res = s.lower()
    if not isUnicode: res = res.encode('utf-8')
    return res

def upper(s):
    '''French-accents-aware variant of string.upper.'''
    isUnicode = isinstance(s, unicode)
    if not isUnicode: s = s.decode('utf-8')
    res = s.upper()
    if not isUnicode: res = res.encode('utf-8')
    return res

# ------------------------------------------------------------------------------
typeLetters = {'b': bool, 'i': int, 'j': long, 'f':float, 's':str, 'u':unicode,
               'l': list, 'd': dict}
exts = {'py': ('.py', '.vpy', '.cpy'), 'pt': ('.pt', '.cpt')}

class CodeAnalysis:
    '''This class holds information about some code analysis (line counts) that
       spans some folder hierarchy.'''
    def __init__(self, name):
        self.name = name # Let's give a name for the analysis
        self.numberOfFiles = 0 # The total number of analysed files
        self.emptyLines = 0 # The number of empty lines within those files
        self.commentLines = 0 # The number of comment lines
        # A code line is defined as anything that is not an empty or comment
        # line.
        self.codeLines = 0

    def numberOfLines(self):
        '''Computes the total number of lines within analysed files.'''
        return self.emptyLines + self.commentLines + self.codeLines

    def analyseZptFile(self, theFile):
        '''Analyses the ZPT file named p_fileName.'''
        inDoc = False
        for line in theFile:
            stripped = line.strip()
            # Manage a comment
            if not inDoc and (line.find('<tal:comment ') != -1):
                inDoc = True
            if inDoc:
                self.commentLines += 1
                if line.find('</tal:comment>') != -1:
                    inDoc = False
                continue
            # Manage an empty line
            if not stripped:
                self.emptyLines += 1
            else:
                self.codeLines += 1

    docSeps = ('"""', "'''")
    def isPythonDoc(self, line, start, isStart=False):
        '''Returns True if we find, in p_line, the start of a docstring (if
           p_start is True) or the end of a docstring (if p_start is False).
           p_isStart indicates if p_line is the start of the docstring.'''
        if start:
            res = line.startswith(self.docSeps[0]) or \
                  line.startswith(self.docSeps[1])
        else:
            sepOnly = (line == self.docSeps[0]) or (line == self.docSeps[1])
            if sepOnly:
                # If the line contains the separator only, is this the start or
                # the end of the docstring?
                if isStart: res = False
                else: res = True
            else:
                res = line.endswith(self.docSeps[0]) or \
                      line.endswith(self.docSeps[1])
        return res

    def analysePythonFile(self, theFile):
        '''Analyses the Python file named p_fileName.'''
        # Are we in a docstring ?
        inDoc = False
        for line in theFile:
            stripped = line.strip()
            # Manage a line that is within a docstring
            inDocStart = False
            if not inDoc and self.isPythonDoc(stripped, start=True):
                inDoc = True
                inDocStart = True
            if inDoc:
                self.commentLines += 1
                if self.isPythonDoc(stripped, start=False, isStart=inDocStart):
                    inDoc = False
                continue
            # Manage an empty line
            if not stripped:
                self.emptyLines += 1
                continue
            # Manage a comment line
            if line.startswith('#'):
                self.commentLines += 1
                continue
            # If we are here, we have a code line.
            self.codeLines += 1

    def analyseFile(self, fileName):
        '''Analyses file named p_fileName.'''
        self.numberOfFiles += 1
        theFile = file(fileName)
        ext = os.path.splitext(fileName)[1]
        if ext in exts['py']:   self.analysePythonFile(theFile)
        elif ext in exts['pt']: self.analyseZptFile(theFile)
        theFile.close()

    def printReport(self):
        '''Returns the analysis report as a string, only if there is at least
           one analysed line.'''
        lines = self.numberOfLines()
        if not lines: return
        commentRate = (self.commentLines / float(lines)) * 100.0
        blankRate = (self.emptyLines / float(lines)) * 100.0
        print '%s: %d files, %d lines (%.0f%% comments, %.0f%% blank)' % \
              (self.name, self.numberOfFiles, lines, commentRate, blankRate)

# ------------------------------------------------------------------------------
class LinesCounter:
    '''Counts and classifies the lines of code within a folder hierarchy.'''
    defaultExcludes = ('%s.svn' % os.sep, '%s.bzr' % os.sep, '%stmp' % os.sep,
                       '%stemp' % os.sep)

    def __init__(self, folderOrModule, excludes=None):
        if isinstance(folderOrModule, basestring):
            # It is the path of some folder
            self.folder = folderOrModule
        else:
            # It is a Python module
            self.folder = os.path.dirname(folderOrModule.__file__)
        # These dicts will hold information about analysed files
        self.python = {False: CodeAnalysis('Python'),
                       True:  CodeAnalysis('Python (test)')}
        self.zpt = {False: CodeAnalysis('ZPT'),
                    True:  CodeAnalysis('ZPT (test)')}
        # Are we currently analysing real or test code?
        self.inTest = False
        # Which paths to exclude from the analysis?
        self.excludes = list(self.defaultExcludes)
        if excludes: self.excludes += excludes

    def printReport(self):
        '''Displays on stdout a small analysis report about self.folder.'''
        for zone in (False, True): self.python[zone].printReport()
        for zone in (False, True): self.zpt[zone].printReport()

    def isExcluded(self, path):
        '''Must p_path be excluded from the analysis?'''
        for excl in self.excludes:
            if excl in path: return True

    def run(self):
        '''Let's start the analysis of self.folder.'''
        # The test markers will allow us to know if we are analysing test code
        # or real code within a given part of self.folder code hierarchy.
        testMarker1 = '%stest%s' % (os.sep, os.sep)
        testMarker2 = '%stest' % os.sep
        testMarker3 = '%stests%s' % (os.sep, os.sep)
        testMarker4 = '%stests' % os.sep
        j = os.path.join
        for root, folders, files in os.walk(self.folder):
            if self.isExcluded(root): continue
            # Are we in real code or in test code ?
            self.inTest = False
            if root.endswith(testMarker2) or (root.find(testMarker1) != -1) or \
               root.endswith(testMarker4) or (root.find(testMarker3) != -1):
                self.inTest = True
            # Scan the files in this folder
            for fileName in files:
                ext = os.path.splitext(fileName)[1]
                if ext in exts['py']:
                    self.python[self.inTest].analyseFile(j(root, fileName))
                elif ext in exts['pt']:
                    self.zpt[self.inTest].analyseFile(j(root, fileName))
        self.printReport()

# ------------------------------------------------------------------------------
CONVERSION_ERROR = 'An error occurred while executing command "%s". %s'
class FileWrapper:
    '''When you get, from an appy object, the value of a File attribute, you
       get an instance of this class.'''
    def __init__(self, zopeFile):
        '''This constructor is only used by Appy to create a nice File instance
           from a Zope corresponding instance (p_zopeFile). If you need to
           create a new file and assign it to a File attribute, use the
           attribute setter, do not create yourself an instance of this
           class.'''
        d = self.__dict__
        d['_zopeFile'] = zopeFile # Not for you!
        d['name'] = zopeFile.filename
        d['content'] = zopeFile.data
        d['mimeType'] = zopeFile.content_type
        d['size'] = zopeFile.size # In bytes

    def __setattr__(self, name, v):
        d = self.__dict__
        if name == 'name':
            self._zopeFile.filename = v
            d['name'] = v
        elif name == 'content':
            self._zopeFile.update_data(v, self.mimeType, len(v))
            d['content'] = v
            d['size'] = len(v)
        elif name == 'mimeType':
            self._zopeFile.content_type = self.mimeType = v
        else:
            raise 'Impossible to set attribute %s. "Settable" attributes ' \
                  'are "name", "content" and "mimeType".' % name

    def dump(self, filePath=None, format=None, tool=None):
        '''Writes the file on disk. If p_filePath is specified, it is the
           path name where the file will be dumped; folders mentioned in it
           must exist. If not, the file will be dumped in the OS temp folder.
           The absolute path name of the dumped file is returned.
           If an error occurs, the method returns None. If p_format is
           specified, OpenOffice will be called for converting the dumped file
           to the desired format. In this case, p_tool, a Appy tool, must be
           provided. Indeed, any Appy tool contains parameters for contacting
           OpenOffice in server mode.'''
        if not filePath:
            filePath = '%s/file%f.%s' % (getOsTempFolder(), time.time(),
                normalizeString(self.name))
        f = file(filePath, 'w')
        if self.content.__class__.__name__ == 'Pdata':
            # The file content is splitted in several chunks.
            f.write(self.content.data)
            nextPart = self.content.next
            while nextPart:
                f.write(nextPart.data)
                nextPart = nextPart.next
        else:
            # Only one chunk
            f.write(self.content)
        f.close()
        if format:
            if not tool: return
            # Convert the dumped file using OpenOffice
            errorMessage = tool.convert(filePath, format)
            # Even if we have an "error" message, it could be a simple warning.
            # So we will continue here and, as a subsequent check for knowing if
            # an error occurred or not, we will test the existence of the
            # converted file (see below).
            os.remove(filePath)
            # Return the name of the converted file.
            baseName, ext = os.path.splitext(filePath)
            if (ext == '.%s' % format):
                filePath = '%s.res.%s' % (baseName, format)
            else:
                filePath = '%s.%s' % (baseName, format)
            if not os.path.exists(filePath):
                tool.log(CONVERSION_ERROR % (cmd, errorMessage), type='error')
                return
        return filePath
# ------------------------------------------------------------------------------
