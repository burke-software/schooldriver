import logging
from django.contrib.auth.models import User
import django
from django.conf import settings
from gdata.apps.service import AppsService, AppsForYourDomainException
from gdata.docs.service import DocsService
from gdata.service import BadAuthentication


logging.debug('GoogleAppsBackend')


class GoogleAppsBackend:
 """ Authenticate against Google Apps """

 def authenticate(self, username=None, password=None):
     logging.debug('GoogleAppsBackend.authenticate: %s - %s' % (username, '*' * len(password)))
     admin_email = '%s@%s' % (settings.GAPPS_USERNAME, settings.GAPPS_DOMAIN)
     email = '%s@%s' % (username, settings.GAPPS_DOMAIN)

     try:
         # Check user's password
         logging.debug('GoogleAppsBackend.authenticate: gdocs')
         gdocs = DocsService()
         gdocs.email = email
         gdocs.password = password
         gdocs.ProgrammaticLogin()
         # Get the user object

         logging.debug('GoogleAppsBackend.authenticate: gapps')
         gapps = AppsService(email=admin_email, password=settings.GAPPS_PASSWORD, domain=settings.GAPPS_DOMAIN)
         gapps.ProgrammaticLogin()
         guser = gapps.RetrieveUser(username)

         logging.debug('GoogleAppsBackend.authenticate: user - %s' % username)
         user, created = User.objects.get_or_create(username=username)

         if created:
             logging.debug('GoogleAppsBackend.authenticate: created')
             user.email = email
             user.last_name = guser.name.family_name
             user.first_name = guser.name.given_name
             user.is_active = not guser.login.suspended == 'true'
             user.is_superuser = guser.login.admin == 'true'
             user.is_staff = True
             user.save()

     except BadAuthentication:
         logging.debug('GoogleAppsBackend.authenticate: BadAuthentication')
         return None

     except AppsForYourDomainException:
         logging.debug('GoogleAppsBackend.authenticate: AppsForYourDomainException')
         return None
    
     except gdata.service.CaptchaRequired:
        import gdata.apps.service
        captcha_token = service._GetCaptchaToken()
        url = service._GetCaptchaURL()
        return redirect(url)

     return user


 def get_user(self, user_id):

     user = None
     try:
         logging.debug('GoogleAppsBackend.get_user')
         user = User.objects.get(pk=user_id)

     except User.DoesNotExist:
         logging.debug('GoogleAppsBackend.get_user - DoesNotExist')
         return None

     return user