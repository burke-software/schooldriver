from django.contrib.auth.models import User

def associate_by_email(**kwargs):
    email = kwargs['details']['email']
    kwargs['user'] = User.objects.filter(email=email).first()
    return kwargs
