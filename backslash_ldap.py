import ldap
from django.conf import settings
from django.contrib.auth.models import User
from ldap_groups.accounts.backends import ActiveDirectoryGroupMembershipSSLBackend

class BackslashActiveDirectoryGroupMembershipSSLBackend(ActiveDirectoryGroupMembershipSSLBackend):
    ''' Hack on ldap_groups so that it recognizes DOMAIN\username syntax. If the user does
    not include DOMAIN\ in the username, the standard ldap_groups behavior is retained. '''
    def bind_ldap(self, username, password):
        try:
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE,settings.CERT_FILE)
        except AttributeError:
            pass
        ldap.set_option(ldap.OPT_REFERRALS,0) # DO NOT TURN THIS OFF OR SEARCH WON'T WORK!
        l = ldap.initialize(settings.LDAP_URL)
        l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        split_username = username.split('\\')
        if len(split_username) > 1:
            # someone trying to use DOMAIN\username syntax
            binddn = "%s@%s" % (split_username[1], split_username[0])
        else:
            # use predetermined domain
            binddn = "%s@%s" % (username,settings.NT4_DOMAIN)
        l.simple_bind_s(binddn.encode('utf-8'),password.encode('utf-8'))
        return l

    def get_or_create_user(self, username, password):
        unparsed_username = username
        if '\\' in username:
            username = username.split('\\')[1]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:

            try:
                l = self.bind_ldap(unparsed_username, password)
                # search
                result = l.search_ext_s(settings.SEARCH_DN,ldap.SCOPE_SUBTREE,"sAMAccountName=%s" % username,settings.SEARCH_FIELDS)[0][1]

                if result.has_key('memberOf'):
                    membership = result['memberOf']
                else:
                    membership = None

                # get email
                if result.has_key('mail'):
                    mail = result['mail'][0]
                else:
                    mail = None
                # get surname
                if result.has_key('sn'):
                    last_name = result['sn'][0]
                else:
                    last_name = None

                # get display name
                if result.has_key('givenName'):
                    first_name = result['givenName'][0]
                else:
                    first_name = None

                l.unbind_s()

                user = User(username=username,first_name=first_name,last_name=last_name,email=mail)

            except Exception, e:
                return None

            user.is_staff = False
            user.is_superuser = False
            user.set_unusable_password()
            user.save()

            self.set_memberships_from_ldap(user, membership)

        return user
