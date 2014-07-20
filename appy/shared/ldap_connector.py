# ------------------------------------------------------------------------------
try:
    import ldap
except ImportError:
    # For people that do not care about ldap.
    ldap = None

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
