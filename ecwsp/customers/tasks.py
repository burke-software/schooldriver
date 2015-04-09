from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template
from django_sis.celery import app
from .models import SignUp, Client


@app.task
def create_tenant(sign_up_id):
    sign_up = SignUp.objects.get(pk=sign_up_id)
    client = Client()
    client.name = sign_up.name
    client.domain_url = sign_up.domain_url
    client.schema_name = sign_up.domain_url
    try:
        client.save()
        sign_up.status = 'D'
    except:
        sign_up.status = 'F'
    subject = "New Schooldriver Instance"
    to = sign_up.client_email
    from_email = 'donotreply@burkesoftware.com'
    plaintext = get_template('sign-up-email.txt')
    htmly = get_template('sign-up-email.html')
    d = Context({'sign_up': sign_up})
    text_content = plaintext.render(d)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    sign_up.save()
