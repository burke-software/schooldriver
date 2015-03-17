# ------------------------------------------------------------------------------
try:
    import ldap
except ImportError:
    # For people that do not care about ldap.
    ldap = None

# ------------------------------------------------------------------------------
class LdapConfig:
    '''Parameters for authenticating users to an LDAP server. This class is
       used by gen-applications. For a pure, appy-independent LDAP connector,
       see the class LdapConnector below.'''
    ldapAttributes = { 'loginAttribute':None, 'emailAttribute':'email',
                       'fullNameAttribute':'title',
                       'firstNameAttribute':'firstName',
                       'lastNameAttribute':'name' }

    def __init__(self):
        self.server = '' # Name of the LDAP server
        self.port = None # Port for this server.
        # Login and password of the technical power user that the Appy
        # application will use to connect to the LDAP.
        self.adminLogin = ''
        self.adminPassword = ''
        # LDAP attribute to use as login for authenticating users.
        self.loginAttribute = 'dn' # Can also be "mail", "sAMAccountName", "cn"
        # LDAP attributes for storing email
        self.emailAttribute = None
        # LDAP attribute for storing full name (first + last name)
        self.fullNameAttribute = None
        # Alternately, LDAP attributes for storing 1st & last names separately.
        self.firstNameAttribute = None
        self.lastNameAttribute = None
        # LDAP classes defining the users stored in the LDAP.
        self.userClasses = ('top', 'person')
        self.baseDn = '' # Base DN where to find users in the LDAP.
        self.scope = 'SUBTREE' # Scope of the search within self.baseDn
        # Is this server connection enabled ?
        self.enabled = True

    def getServerUri(self):
        '''Returns the complete URI for accessing the LDAP, ie
           "ldap://some.ldap.server:389".'''
        port = self.port or 389
        return 'ldap://%s:%d' % (self.server, port)

    def getUserFilterValues(self, login):
        '''Gets the filter values required to perform a query for finding user
           corresponding to p_login in the LDAP.'''
        res = [(self.loginAttribute, login)]
        for userClass in self.userClasses:
            res.append( ('objectClass', userClass) )
        return res

    def getUserAttributes(self):
        '''Gets the attributes we want to get from the LDAP for characterizing
           a user.'''
        res = []
        for name in self.ldapAttributes.iterkeys():
            if getattr(self, name):
                res.append(getattr(self, name))
        return res

    def getUserParams(self, ldapData):
        '''Formats the user-related p_ldapData retrieved from the ldap, as a
           dict of params usable for creating or updating the corresponding
           Appy user.'''
        res = {}
        for name, appyName in self.ldapAttributes.iteritems():
            if not appyName: continue
            # Get the name of the attribute as known in the LDAP.
            ldapName = getattr(self, name)
            if not ldapName: continue
            if ldapData.has_key(ldapName) and ldapData[ldapName]:
                value = ldapData[ldapName]
                if isinstance(value, list): value = value[0]
                res[appyName] = value
        return res

# ------------------------------------------------------------------------------
class LdapConnector:
    '''This class manages the communication with a LDAP server.'''
    def __init__(self, serverUri, tentatives=5, ssl=False, timeout=5,
                 tool=None):
        # The URI of the LDAP server, ie ldap://some.ldap.server:389.
        self.serverUri = serverUri
        # The object that will represent the LDAP server
        self.server = None
        # The number of trials the connector will at most perform to the LDAP
        # server, when executing a query in it.
        self.tentatives = tentatives
        self.ssl = ssl
        # The timeout for every query to the LDAP.
        self.timeout = timeout
        # A tool from a Appy application can be given and will be used, ie for
        # logging purpose.
        self.tool = tool

    def log(self, message, type='info'):
        '''Logs via a Appy tool if available.'''
        if self.tool:
            self.tool.log(message, type=type)
        else:
            print(message)

    def connect(self, login, password):
        '''Connects to the LDAP server using p_login and p_password as
           credentials. If the connection succeeds, a server object is created
           in self.server and tuple (True, None) is returned. Else, tuple
           (False, errorMessage) is returned.'''
        try:
            self.server = ldap.initialize(self.serverUri)
            self.server.simple_bind_s(login, password)
            return True, None
        except AttributeError, ae:
            # When the ldap module is not there, trying to catch ldap.LDAPError
            # will raise an error.
            message = str(ae)
            self.log('Ldap connect error with login %s (%s).' % \
                     (login, message))
            return False, message
        except ldap.LDAPError, le:
            message = str(le)
            self.log('%s: connect error with login %s (%s).' % \
                     (self.serverUri, login, message))
            return False, message

    def getFilter(self, values):
        '''Builds and returns a LDAP filter based on p_values, a tuple or list
           of tuples (name,value).'''
        return '(&%s)' % ''.join(['(%s=%s)' % (n, v) for n, v in values])

    def search(self, baseDn, scope, filter, attributes=None):
        '''Performs a query in the LDAP at node p_baseDn, with the given
           p_scope. p_filter is a LDAP filter that constraints the search. It
           can be computed from a list of tuples (value, name) by method
           m_getFilter. p_attributes is the list of attributes that we will
           retrieve from the LDAP. If None, all attributes will be retrieved.'''
        if self.ssl: self.server.start_tls_s()
        try:
            # Get the LDAP constant corresponding to p_scope.
            scope = getattr(ldap, 'SCOPE_%s' % scope)
            # Perform the query.
            for i in range(self.tentatives):
                try:
                    return self.server.search_st(\
                        baseDn, scope, filterstr=filter, attrlist=attributes,
                        timeout=self.timeout)
                except ldap.TIMEOUT:
                    pass
        except ldap.LDAPError, le:
            self.log('LDAP query error %s: %s' % \
                     (le.__class__.__name__, str(le)))
# ------------------------------------------------------------------------------
