'''This module allows to call RFC functions exposed by a distant SAP system.
   It requires the "pysap" module available at http://pysaprfc.sourceforge.net
   and the library librfccm.so that one can download from the "SAP MarketPlace",
   a website by SAP requiring a login/password.'''

# ------------------------------------------------------------------------------
from appy.gen.utils import sequenceTypes

class SapError(Exception): pass
SAP_MODULE_ERROR = 'Module pysap was not found (you can get it at ' \
    'http://pysaprfc.sourceforge.net)'
SAP_CONNECT_ERROR = 'Error while connecting to SAP (conn_string: %s). %s'
SAP_FUNCTION_ERROR = 'Error while calling function "%s". %s'
SAP_DISCONNECT_ERROR = 'Error while disconnecting from SAP. %s'
SAP_TABLE_PARAM_ERROR = 'Param "%s" does not correspond to a valid table ' \
    'parameter for function "%s".'
SAP_STRUCT_ELEM_NOT_FOUND = 'Structure used by parameter "%s" does not define '\
    'an attribute named "%s."'
SAP_STRING_REQUIRED = 'Type mismatch for attribute "%s" used in parameter ' \
    '"%s": a string value is expected (SAP type is %s).'
SAP_STRING_OVERFLOW = 'A string value for attribute "%s" used in parameter ' \
    '"%s" is too long (SAP type is %s).'
SAP_FUNCTION_NOT_FOUND = 'Function "%s" does not exist.'
SAP_FUNCTION_INFO_ERROR = 'Error while asking information about function ' \
    '"%s". %s'
SAP_GROUP_NOT_FOUND = 'Group of functions "%s" does not exist or is empty.'

# Is the pysap module present or not ?
hasSap = True
try:
    import pysap
except ImportError:
    hasSap = False

# ------------------------------------------------------------------------------
class SapResult:
    '''Represents a result as returned by SAP. It defines a __getattr__ method
       that allows to retrieve SAP "output" parameters (export, tables) by their
       name (as if they were attributes of this class), in a Python format
       (list, dict, simple value).'''
    def __init__(self, function):
        # The pysap function obj that was called and that produced this result.
        self.function = function
    def __getattr__(self, name):
        '''Allows a smart access to self.function's results.'''
        if name.startswith('__'): raise AttributeError
        paramValue = self.function[name]
        paramType = paramValue.__class__.__name__
        if paramType == 'ItTable':
            return paramValue.to_list()
        elif paramType == 'STRUCT':
            return paramValue.to_dict()
        else:
            return paramValue

# ------------------------------------------------------------------------------
class Sap:
    '''Represents a remote SAP system. This class allows to connect to a distant
       SAP system and perform RFC calls.'''
    def __init__(self, host, sysnr, client, user, password):
        self.host = host # Hostname or IP address of SAP server
        self.sysnr = sysnr # The system number of SAP server/gateway
        self.client = client # The instance/client number
        self.user = user
        self.password = password
        self.sap = None # Will hold the handler to the SAP distant system.
        self.functionName = None # The name of the next function to call.
        if not hasSap: raise SapError(SAP_MODULE_ERROR)

    def connect(self):
        '''Connects to the SAP system.'''
        params = 'ASHOST=%s SYSNR=%s CLIENT=%s USER=%s PASSWD=%s' % (self.host,
            self.sysnr, self.client, self.user, self.password)
        try:
            self.sap = pysap.Rfc_connection(conn_string = params)
            self.sap.open()
        except pysap.BaseSapRfcError, se:
            # Put in the error message the connection string without the
            # password.
            connNoPasswd = params[:params.index('PASSWD')] + 'PASSWD=********'
            raise SapError(SAP_CONNECT_ERROR % (connNoPasswd, str(se)))

    def createStructure(self, structDef, userData, paramName):
        '''Create a struct corresponding to SAP/C structure definition
           p_structDef and fills it with dict p_userData.'''
        res = structDef()
        for name, value in userData.iteritems():
            if name not in structDef._sfield_names_:
                raise SapError(SAP_STRUCT_ELEM_NOT_FOUND % (paramName, name))
            sapType = structDef._sfield_sap_types_[name]
            # Check if the value is valid according to the required type
            if sapType[0] == 'C':
                sType = '%s%d' % (sapType[0], sapType[1])
                # "None" value is tolerated.
                if value == None: value = ''
                if not isinstance(value, basestring):
                    raise SapError(
                        SAP_STRING_REQUIRED % (name, paramName, sType))
                if len(value) > sapType[1]:
                    raise SapError(
                        SAP_STRING_OVERFLOW % (name, paramName, sType))
                # Left-fill the string with blanks.
                v = value.ljust(sapType[1])
            else:
                v = value
            res[name.lower()] = v
        return res

    def call(self, functionName=None, **params):
        '''Calls a function on the SAP server.'''
        try:
            if not functionName:
                functionName = self.functionName
            function = self.sap.get_interface(functionName)
            # Specify the parameters
            for name, value in params.iteritems():
                if type(value) == dict:
                    # The param corresponds to a SAP/C "struct"
                    v = self.createStructure(
                        self.sap.get_structure(name),value, name)
                elif type(value) in sequenceTypes:
                    # The param must be a SAP/C "table" (a list of structs)
                    # Retrieve the name of the struct type related to this
                    # table.
                    fDesc = self.sap.get_interface_desc(functionName)
                    tableTypeName = ''
                    for tDesc in fDesc.tables:
                        if tDesc.name == name:
                            # We have found the correct table param
                            tableTypeName = tDesc.field_def
                            break
                    if not tableTypeName:
                        raise SapError(\
                            SAP_TABLE_PARAM_ERROR % (name, functionName))
                    v = self.sap.get_table(tableTypeName)
                    for dValue in value:
                        v.append(self.createStructure(v.struc, dValue, name))
                else:
                    v = value
                function[name] = v
            # Call the function
            function()
        except pysap.BaseSapRfcError, se:
            raise SapError(SAP_FUNCTION_ERROR % (functionName, str(se)))
        return SapResult(function)

    def __getattr__(self, name):
        '''The user can directly call self.<sapFunctionName>(params) instead of
           calling self.call(<sapFunctionName>, params).'''
        if name.startswith('__'): raise AttributeError
        self.functionName = name
        return self.call

    def getTypeInfo(self, typeName):
        '''Returns information about the type (structure) named p_typeName.'''
        res = ''
        tInfo = self.sap.get_structure(typeName)
        for fName, fieldType in tInfo._fields_:
            res += '  %s: %s (%s)\n' % (fName, tInfo.sap_def(fName),
                                        tInfo.sap_type(fName))
        return res

    def getFunctionInfo(self, functionName):
        '''Returns information about the RFC function named p_functionName.'''
        try:
            res = ''
            usedTypes = set() # Names of type definitions used in parameters.
            fDesc = self.sap.get_interface_desc(functionName)
            functionDescr = str(fDesc).strip()
            if functionDescr: res += functionDescr
            # Import parameters
            if fDesc.imports:
                res += '\nIMPORTS\n'
                for iDesc in fDesc.imports:
                    res += '  %s\n' % str(iDesc)
                    usedTypes.add(iDesc.field_def)
            # Export parameters
            if fDesc.exports:
                res += '\nEXPORTS\n'
                for eDesc in fDesc.exports:
                    res += '  %s\n' % str(eDesc)
                    usedTypes.add(eDesc.field_def)
            if fDesc.tables:
                res += '\nTABLES\n'
                for tDesc in fDesc.tables:
                    res += '  %s\n' % str(tDesc)
                    usedTypes.add(tDesc.field_def)
            if fDesc.exceptions:
                res += '\nEXCEPTIONS\n'
                for eDesc in fDesc.exceptions:
                    res += '  %s\n' % str(eDesc)
            # Add information about used types
            if usedTypes:
                res += '\nTypes used by the parameters:\n'
                for typeName in usedTypes:
                    # Dump info only if it is a structure, not a simple type
                    try:
                        self.sap.get_structure(typeName)
                        res += '%s\n%s\n\n' % \
                            (typeName, self.getTypeInfo(typeName))
                    except pysap.BaseSapRfcError, ee:
                        pass
            return res
        except pysap.BaseSapRfcError, se:
            if se.value == 'FU_NOT_FOUND':
                raise SapError(SAP_FUNCTION_NOT_FOUND % (functionName))
            else:
                raise SapError(SAP_FUNCTION_INFO_ERROR % (functionName,str(se)))

    def getGroupInfo(self, groupName):
        '''Gets information about the functions that are available in group of
           functions p_groupName.'''
        if groupName == '_all_':
            # Search everything.
            functions = self.sap.search_functions('*')
        else:
            functions = self.sap.search_functions('*', grpname=groupName)
        if not functions:
            raise SapError(SAP_GROUP_NOT_FOUND % (groupName))
        res = 'Available functions:\n'
        for f in functions:
            res += '  %s' % f.funcname
            if groupName == '_all_':
                res += ' (group: %s)' % f.groupname
            res += '\n'
        return res

    def disconnect(self):
        '''Disconnects from SAP.'''
        try:
            self.sap.close()
        except pysap.BaseSapRfcError, se:
            raise SapError(SAP_DISCONNECT_ERROR % str(se))
# ------------------------------------------------------------------------------
