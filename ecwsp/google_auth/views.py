import urlparse

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.http import base36_to_int
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.utils.safestring import mark_safe

import gdata

@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Copy of Django's generic login view, modified to allow gdata error messages to be shown.
    """
    msg = ""
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        try:
            if form.is_valid():
                netloc = urlparse.urlparse(redirect_to)[1]
    
                # Use default setting if redirect_to is empty
                if not redirect_to:
                    redirect_to = settings.LOGIN_REDIRECT_URL
    
                # Security check -- don't allow redirection to a different host.
                elif netloc and netloc != request.get_host():
                    redirect_to = settings.LOGIN_REDIRECT_URL
    
                # Okay, security checks complete. Log the user in.
                auth_login(request, form.get_user())

                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()
    
                return HttpResponseRedirect(redirect_to)
        except gdata.service.CaptchaRequired:
            msg = 'Account may be locked, please go <a href="https://www.google.com/accounts/b/0/DisplayUnlockCaptcha"> here </a> to unlock it and try again.<br/>If you are not a Google Apps user, please ignore this message and try again.'
    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
        'msg': mark_safe(msg),
    }
    context.update(extra_context or {})
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request, current_app=current_app))