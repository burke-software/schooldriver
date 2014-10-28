from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from constance import config
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.contrib.sessions.models import Session
from ecwsp.sis.models import Student
from suds.client import Client
import json


@login_required
def login(request):
    """ Log student into Naviance. If successful redirect them.
    """
    username = config.NAVIANCE_USERNAME
    password = config.NAVIANCE_PASSWORD
    linked_field = config.NAVIANCE_SWORD_ID
    url = 'https://services.naviance.com/services/school/index.php?wsdl'

    if request.user.groups.filter(name="students").count():
        try:
            student = Student.objects.get(username=request.user.username)
        except:
            return HttpResponse('Not a valid student')

        if linked_field == 'username':
            nav_id = student.username
        elif linked_field == 'id':
            nav_id = student.id
        elif linked_field == 'unique_id':
            nav_id = student.unique_id
        else:
            return HttpResponse('Error: NAVIANCE_SWORD_ID not set correctly')
    else:
        msg = mark_safe('You must be a student to use Naviance Single Sign On. Did you want to <a href="/logout">log out</a>?')
        return render_to_response('sis/generic_msg.html', {'msg':msg}, RequestContext(request, {}), )

    client = Client(url)
    token = client.service.GetSessionToken(username, password)
    result = client.service.LoginStudent(
        token,
        '{"highschoolStudentId":"%s"}' % (nav_id,),
    )

    url = json.loads(result).get('loginUrl')
    # Log out user because naviance won't
    for s in Session.objects.all():
        if s.get_decoded().get('_auth_user_id') == request.user.id:
            s.delete()
    return HttpResponseRedirect(url)
