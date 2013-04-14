"""CAS login/logout replacement views"""
from datetime import datetime
from urllib import urlencode
import urlparse
from operator import itemgetter

from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from cas.models import PgtIOU
from django.contrib import messages

__all__ = ['login', 'logout']


def _service_url(request, redirect_to=None, gateway=False):
    """Generates application service URL for CAS"""

    protocol = ('http://', 'https://')[request.is_secure()]
    host = request.get_host()
    prefix = (('http://', 'https://')[request.is_secure()] + host)
    service = protocol + host + request.path
    if redirect_to:        
        if '?' in service:
            service += '&'
        else:
            service += '?'
        if gateway:
            """ If gateway, capture params and reencode them before returning a url """
            gateway_params = [ (REDIRECT_FIELD_NAME, redirect_to), ('gatewayed','true') ]
            query_dict = request.GET.copy()
            try:
                del query_dict['ticket']
            except:
                pass
            query_list = query_dict.items()

            #remove duplicate params
            for item in query_list:
                for index, item2 in enumerate(gateway_params):
                    if item[0] == item2[0]:
                        gateway_params.pop(index)
            extra_params = gateway_params + query_list
            
            #Sort params by key name so they are always in the same order.
            sorted_params = sorted(extra_params, key=itemgetter(0))            
            service += urlencode(sorted_params)
        else:
            service += urlencode({REDIRECT_FIELD_NAME: redirect_to})
    return service


def _redirect_url(request):
    """Redirects to referring page, or CAS_REDIRECT_URL if no referrer is
    set.
    """
    
    next = request.GET.get(REDIRECT_FIELD_NAME)
    if not next:
        if settings.CAS_IGNORE_REFERER:
            next = settings.CAS_REDIRECT_URL
        else:
            next = request.META.get('HTTP_REFERER', settings.CAS_REDIRECT_URL)
                        
        host = request.get_host()
        prefix = (('http://', 'https://')[request.is_secure()] + host)
        if next.startswith(prefix):
            next = next[len(prefix):]
    return next


def _login_url(service, ticket='ST', gateway=False):
    """Generates CAS login URL"""
    LOGINS = {'ST':'login',
              'PT':'proxyValidate'}
    if gateway:
        params = {'service': service, 'gateway':True}
    else:
        params = {'service': service}
    if settings.CAS_EXTRA_LOGIN_PARAMS:
        params.update(settings.CAS_EXTRA_LOGIN_PARAMS)
    if not ticket:
        ticket = 'ST'
    login = LOGINS.get(ticket[:2],'login')

    return urlparse.urljoin(settings.CAS_SERVER_URL, login) + '?' + urlencode(params)

def _logout_url(request, next_page=None):
    """Generates CAS logout URL"""

    url = urlparse.urljoin(settings.CAS_SERVER_URL, 'logout')
    if next_page:
        protocol = ('http://', 'https://')[request.is_secure()]
        host = request.get_host()
        url += '?' + urlencode({'url': protocol + host + next_page})
    return url


def login(request, next_page=None, required=False, gateway=False):
    """Forwards to CAS login URL or verifies CAS ticket"""

    if not next_page:
        next_page = _redirect_url(request)
    if request.user.is_authenticated():
        return HttpResponseRedirect(next_page)
    ticket = request.GET.get('ticket')

    if gateway:
        service = _service_url(request, next_page, True)
    else:
        service = _service_url(request, next_page, False)

    if ticket:
        from django.contrib import auth
        user = auth.authenticate(ticket=ticket, service=service)

        if user is not None:
            #Has ticket, logs in fine    
            auth.login(request, user)
            if settings.CAS_PROXY_CALLBACK:
                proxy_callback(request)
            #keep urls
            return HttpResponseRedirect(next_page)
        elif settings.CAS_RETRY_LOGIN or required:
            #Has ticket, 
            if gateway:
                return HttpResponseRedirect(_login_url(service, ticket, True))
            else:
                return HttpResponseRedirect(_login_url(service, ticket, False))
        else:
            #Has ticket, not session
            if getattr(settings, 'CAS_CUSTOM_FORBIDDEN'):
                from django.core.urlresolvers import reverse
                return HttpResponseRedirect(reverse(settings.CAS_CUSTOM_FORBIDDEN) + "?" + request.META['QUERY_STRING'])
            else:
                error = "<h1>Forbidden</h1><p>Login failed.</p>"
                return HttpResponseForbidden(error)
    else:
        if gateway:
            return HttpResponseRedirect(_login_url(service, ticket, True))
        else:
            return HttpResponseRedirect(_login_url(service, ticket, False))


def logout(request, next_page=None):
    """Redirects to CAS logout page"""

    from django.contrib.auth import logout
    logout(request)
    if not next_page:
        next_page = _redirect_url(request)
    if settings.CAS_LOGOUT_COMPLETELY:
        return HttpResponseRedirect(_logout_url(request, next_page))
    else:
        return HttpResponseRedirect(next_page)

def proxy_callback(request):
    """Handles CAS 2.0+ XML-based proxy callback call.
    Stores the proxy granting ticket in the database for 
    future use.
    
    NB: Use created and set it in python in case database
    has issues with setting up the default timestamp value
    """
    pgtIou = request.GET.get('pgtIou')
    tgt = request.GET.get('pgtId')

    if not (pgtIou and tgt):
        return HttpResponse('No pgtIOO', mimetype="text/plain")
    try:
        PgtIOU.objects.create(tgt=tgt, pgtIou=pgtIou, created=datetime.now())
        request.session['pgt-TICKET'] = ticket
        return HttpResponse('PGT ticket is: %s' % str(ticket, mimetype="text/plain"))
    except:
        return HttpResponse('PGT storage failed for %s' % str(request.GET), mimetype="text/plain")

    return HttpResponse('Success', mimetype="text/plain")

