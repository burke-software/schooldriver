#   Copyright 2011 Burke Software and Consulting LLC
#   Author: John Milner <john@tmoj.net>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.models import Count
from django.views.generic.simple import redirect_to
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory

from ecwsp.sis.models import *
from ecwsp.sis.uno_report import *
from ecwsp.sis.xlsReport import *
from ecwsp.schedule.models import *
from ecwsp.schedule.forms import *
from ecwsp.schedule.forms import *
from ecwsp.administration.models import *
from ecwsp.benchmark_grade.models import *

from decimal import Decimal, ROUND_HALF_UP
import time
import logging

class struct(): pass

@user_passes_test(lambda u: u.groups.filter(Q(name='teacher') | Q(name="registrar")).count() > 0 or u.is_superuser, login_url='/')
def benchmark_grade_upload(request, id):
    """ Grades can only be entered/changed by spreadsheet upload. """
    course = Course.objects.get(id=id)
    message = ''
    if request.method == 'POST' and 'upload' in request.POST:
        import_form = GradeUpload(request.POST, request.FILES)
        if import_form.is_valid():
            from ecwsp.benchmark_grade.importer import BenchmarkGradeImporter
            importer = BenchmarkGradeImporter(request.FILES['file'], request.user)
            mark_count = importer.import_grades(course, import_form.cleaned_data['marking_period'])
            message = str(mark_count) + " marks were imported."
    else:
        import_form = GradeUpload()
        
    ''' basically the same as student_grade, except is per-student instead of per-course '''
    mps = MarkingPeriod.objects.filter(school_year=SchoolYear.objects.get(active_year=True),
                                       start_date__lte=date.today(), active=True).order_by('-start_date')
    for mp in mps:
        mp.students = course.get_enrolled_students(show_deleted=True)
        for student in mp.students:
            student.categories = Category.objects.all() # derp DERP
            for category in student.categories:
                category.marks = Mark.objects.filter(student=student, item__course=course,
                                                     item__category=category, item__markingPeriod=mp).order_by('-item__date', 'item__name',
                                                                                                               'description')
                try:
                    agg = Aggregate.objects.get(singleStudent=student, singleCourse=course,
                                                singleCategory=category, singleMarkingPeriod=mp)
                    category.average = agg.scale.spruce(agg.cachedValue)
                except:
                    category.average = None
 
    return render_to_response('benchmark_grade/upload.html', {
        'request': request,
        'course': course,
        'import_form': import_form,
        'message': message,
        'mps': mps
    }, RequestContext(request, {}),)

@user_passes_test(lambda u: u.groups.filter(name='students').count() > 0 or u.is_superuser, login_url='/')
def student_grade(request):
    """ A view for students to see their own grades, in detail. """
    mps = MarkingPeriod.objects.filter(school_year=SchoolYear.objects.get(active_year=True),
                                       start_date__lte=date.today()).order_by('-start_date')
    try:
        student = Student.objects.get(username=request.user.username)
    except:
        print 'No student found for user "' + request.user.username + '"'
        # don't actually fix anything; I still want it to 500 and email me when this happens
    for mp in mps:
        mp.courses = Course.objects.filter(courseenrollment__user=student, graded=True, marking_period=mp).order_by('fullname')
        for course in mp.courses:
            course.categories = Category.objects.all() # derp
            for category in course.categories:
                category.marks = Mark.objects.filter(student=student, item__course=course,
                                                     item__category=category, item__markingPeriod=mp).order_by('-item__date', 'item__name',
                                                                                                               'description')
                if category.name == 'Standards':
                    category.marks = category.marks.filter(description='Session')
                try:
                    agg = Aggregate.objects.get(singleStudent=student, singleCourse=course,
                                                singleCategory=category, singleMarkingPeriod=mp)
                    category.average = agg.scale.spruce(agg.cachedValue)
                except:
                    category.average = None
    
    #return HttpResponse(s)
    return render_to_response('benchmark_grade/student_grade.html', {
        'student': student,
        'today': date.today(),
        'mps': mps
    }, RequestContext(request, {}),)
