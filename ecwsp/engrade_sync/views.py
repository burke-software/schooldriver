from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext

from ecwsp.engrade_sync.models import *
from ecwsp.engrade_sync.forms import *
from ecwsp.engrade_sync.engrade_sync import *

import sys

@permission_required('engrade_sync.change_coursesync')
def setup(request):
    course_count = CourseSync.objects.count()
    teacher_count = TeacherSync.objects.count()
    school_id = settings.ENGRADE_SCHOOLID
    try:
        engrade_sync = EngradeSync()
    except:
        engrade_sync = None
        print >> sys.stderr, 'Can\'t connect to Engrade ' + str(sys.exc_info()[0])
    msg = ''
    
    if request.POST and engrade_sync:
        if 'generate_course' in request.POST:
            course_form = SetupCoursesForm(request.POST)
            if course_form.is_valid():
                ids = engrade_sync.generate_courses(course_form.cleaned_data['marking_period'])
                msg += "Success. Engrade course ids are " + unicode(ids)
    else:
        course_form = SetupCoursesForm()
    
    return render_to_response('engrade_sync/setup.html', {
        'course_count': course_count,
        'teacher_count': teacher_count,
        'course_form': course_form,
        'school_id': school_id,
        'engrade_sync': engrade_sync,
        'msg': msg,
    }, RequestContext(request, {}),)