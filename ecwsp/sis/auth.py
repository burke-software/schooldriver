from django.contrib.auth.models import User
from constance import config

def associate_by_email(**kwargs):
    email = kwargs['details']['email']
    user = User.objects.filter(email=email).first()
    if user == None:
        apps_domain = config.GOOGLE_APPS_DOMAIN
        if apps_domain:
            email_username, email_domain = email.split('@')
            if email_domain == apps_domain:
                user = User.objects.filter(username=email_username).first()
    kwargs['user'] = user
    return kwargs
