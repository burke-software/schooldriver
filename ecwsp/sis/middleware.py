from django.contrib import messages
from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from django.shortcuts import redirect
from social.exceptions import AuthCanceled

class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) == AuthCanceled:
            messages.add_message(
                request,
                messages.WARNING,
                "You canceled your single sign on request.")
            return redirect('/accounts/login/')
        else:
            pass
