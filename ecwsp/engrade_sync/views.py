from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import permission_required
from constance import config
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext

from ecwsp.engrade_sync.models import *
from ecwsp.engrade_sync.forms import *
from ecwsp.engrade_sync.engrade_sync import *
from ecwsp.schedule.models import CourseSection

import sys
import logging

@permission_required('engrade_sync.change_coursesync')
def setup(request):
    course_sections_count = CourseSectionSync.objects.count()
    teacher_count = TeacherSync.objects.count()
    school_id = config.ENGRADE_SCHOOLID
    try:
        engrade_sync = EngradeSync()
    except:
        engrade_sync = None
        print >> sys.stderr, 'Can\'t connect to Engrade ' + str(sys.exc_info()[0])
    msg = ''

    course_form = SetupCourseForm(prefix="course")
    grade_sync_form = GradeSyncForm()

    if request.POST and engrade_sync:
        if 'generate_course' in request.POST:
            course_form = SetupCourseForm(request.POST,prefix="course")
            if course_form.is_valid():
                ids = engrade_sync.generate_courses(course_form.cleaned_data['marking_period'])
                msg += "Success. Engrade course ids are " + unicode(ids)
        elif 'generate_teacher' in request.POST:
            num_created = engrade_sync.generate_all_teachers()
            msg += "Created %s teachers in Engrade." % (num_created,)
        elif 'grade_sync' in request.POST:
            grade_sync_form = GradeSyncForm(request.POST)
            if grade_sync_form.is_valid():
                marking_period = grade_sync_form.cleaned_data['marking_period']
                teachers = grade_sync_form.cleaned_data['teachers']
                include_comments = grade_sync_form.cleaned_data['include_comments']
                try:
                    course_sections = CourseSection.objects.filter(marking_period=marking_period,teachers__in=teachers,graded=True)
                    es = EngradeSync()
                    errors = ""
                    successful = 0
                    for course_section in course_sections:
                        error = es.sync_course_grades(course_section, marking_period, include_comments)
                        if error:
                            errors += error
                        else:
                            successful += 1
                    if errors:
                        messages.warning(
                            request,
                            'Engrade Sync successful for %s course sections, but has some issues: %s' % (str(successful),errors)
                            )
                    else:
                        messages.success(
                            request,
                            'Engrade Sync successful for %s course sections. Please verify anyway!' % (str(successful,))
                            )
                except:
                    messages.error(request, 'Engrade Sync unsuccessful. Contact an administrator.')
                    logger.error('Engrade Sync unsuccessful', exc_info=True, extra={
                        'request': request,
                        'exception':sys.exc_info(),
                    })

    return render_to_response('engrade_sync/setup.html', {
        'course_sections_count': course_sections_count,
        'teacher_count': teacher_count,
        'course_form': course_form,
        'grade_sync_form': grade_sync_form,
        'school_id': school_id,
        'engrade_sync': engrade_sync,
        'msg': msg,
    }, RequestContext(request, {}),)
