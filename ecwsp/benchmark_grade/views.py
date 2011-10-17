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
from ecwsp.administration.models import *
from ecwsp.benchmark_grade.models import *

from decimal import Decimal, ROUND_HALF_UP
import time
import logging

class struct(): pass

@user_passes_test(lambda u: u.groups.filter(Q(name='teacher') | Q(name="registrar")).count() > 0 or u.is_superuser, login_url='/')
def benchmark_grade_upload(request, id):
    """ This view is for inputing grades. It usually is done by uploading a spreadsheet.
    However it can also be done by manually overriding grades. This requires
    registrar level access. """
    course = Course.objects.get(id=id)
    students = course.get_enrolled_students(show_deleted=True)
    grades = course.grade_set.all()
    
    if request.method == 'POST' and 'upload' in request.POST:
        # no marking periods for now.
        import_form = UploadFileForm(request.POST, request.FILES) # GradeUpload(request.POST, request.FILES)
        if import_form.is_valid():
            from ecwsp.benchmark_grade.importer import BenchmarkGradeImporter
            importer = BenchmarkGradeImporter(request.FILES['file'], request.user)
            # yep, still no marking periods.
            importer.import_grades(course, None) # import_form.cleaned_data['marking_period'])
    else:
        # seriously, no marking periods. period.
        import_form = UploadFileForm() # GradeUpload()
    '''    
    if request.method == 'POST' and 'edit' in request.POST:
        # save grades
        handle_grade_save(request, course)
    '''
    for student in students:
        student.grades = []
        # display grades include mid marks and are not used for calculations
        student.display_grades = []
        student.comments = []
        student.grade_id = []
    
    '''
    marking_periods = course.marking_period.all().order_by('start_date')
    
    for mp in marking_periods:
        if Grade.objects.filter(course=course, marking_period=mp, final=False).count():
            mp.has_mid = True
        else:
            mp.has_mid = False
    '''
    
    tableHeaders = []
    x = 0
    y = 0
    aggNames = "Standards", "Engagement", "Organization", "Daily Practice"
    if course.department.name == "Hire4Ed":
        aggNames = "Standards", "Engagement", "Organization", "Precision & Accuracy"
    for aggName in aggNames:
        scale = None
        if aggName == "Standards":
            scale = Scale.objects.get(name="Four-Oh with YTD")
        elif aggName == "Daily Practice":
            scale = Scale.objects.get(name="Percent")
        else:
            scale = Scale.objects.get(name="Four-Oh")
        tableHeaders.append(aggName)
        y = 0
        for student in students:
            aggModel, created = Aggregate.objects.get_or_create(name=aggName, scale=scale, singleStudent=student,
                                                                singleCourse=course,
                                                                singleCategory=Category.objects.get(name=aggName))
            grade_struct = struct()
            grade_struct.grade = aggModel.scale.spruce(aggModel.manualMark)
            grade_struct.id = aggModel.id
            grade_struct.x = x
            grade_struct.y = y
            student.display_grades.append(grade_struct)
            #student.comments.append(grade.comment)
            y += 1
        x += 1
        last_y = y - 1
        last_x = x
            
    for item in Item.objects.filter(course=course):
        tableHeaders.append(item.name)
        y = 0
        for student in students:
            mark, created = Mark.objects.get_or_create(item=item, student=student)
            grade_struct = struct()
            grade_struct.grade = item.scale.spruce(mark.mark)
            grade_struct.id = mark.id
            grade_struct.x = x
            grade_struct.y = y
            student.display_grades.append(grade_struct)
    '''
    if request.user.is_superuser or request.user.has_perm('schedule.change_own_grade'):
        edit = True
    else:
        edit = False
    '''
    return render_to_response('benchmark_grade/upload.html', {
        'request': request, 
        'course': course, 
        'th_list': tableHeaders, 
        'students': students, 
        'import_form': import_form,
        'edit': False, # edit,
        'last_y': last_y,
        'last_x': last_x,
    }, RequestContext(request, {}),)