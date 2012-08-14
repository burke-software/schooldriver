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
from ecwsp.grades.forms import *
from ecwsp.administration.models import *
from ecwsp.benchmark_grade.models import *
from ecwsp.benchmark_grade.forms import *
from ecwsp.omr.models import Benchmark

from decimal import Decimal, ROUND_HALF_UP
import time
import logging

@user_passes_test(lambda u: u.groups.filter(Q(name='teacher') | Q(name="registrar")).count() > 0 or u.is_superuser, login_url='/')
def benchmark_grade_upload(request, id):
    """ Grades can only be entered/changed by spreadsheet upload. """
    course = Course.objects.get(id=id)
    message = ''
    mps = ()
    available_mps = course.marking_period.filter(Q(active=True) | Q(start_date__lt=date.today))
    show_descriptions = True
    if request.method == 'POST':
        if 'upload' in request.POST:
            import_form = GradeUpload(request.POST, request.FILES)
            verify_form = BenchmarkGradeVerifyForm() 
            if import_form.is_valid():
                from ecwsp.benchmark_grade.importer import BenchmarkGradeImporter
                importer = BenchmarkGradeImporter(request.FILES['file'], request.user)
                mark_count = importer.import_grades(course, import_form.cleaned_data['marking_period'])
                message = str(mark_count) + " marks were imported."
        if 'verify' in request.POST:
            verify_form = BenchmarkGradeVerifyForm(request.POST)
            verify_form.fields['marking_periods'].queryset = available_mps 
            import_form = GradeUpload()
            if verify_form.is_valid():
                ''' basically the same as student_grade, except is per-student instead of per-course '''
                mps = MarkingPeriod.objects.filter(id__in=verify_form.cleaned_data['marking_periods'])
                if verify_form.cleaned_data['all_students']:
                    students = course.get_enrolled_students()
                else:
                    students = course.get_enrolled_students().filter(id__in=verify_form.cleaned_data['students'])
                categories = Category.objects.filter(item__course=course).distinct()
                for mp in mps:
                    mp.students = students.all() # must have all() to make a copy; loses all optimization gains
                    for student in mp.students:
                        student.categories = categories.all()
                        for category in student.categories:
                            category.marks = Mark.objects.filter(student=student, item__course=course, item__category=category,
                                                                 item__markingPeriod=mp).order_by('-item__date', 'item__name', 'description')
                            if not verify_form.cleaned_data['all_demonstrations']:
                                category.marks = category.marks.filter(Q(description='Session') | Q(description=''))
                                # If all_demonstrations aren't shown, "Session" is assumed; description is unnecessary
                                show_descriptions = False
                            try:
                                agg = Aggregate.objects.get(singleStudent=student, singleCourse=course,
                                                            singleCategory=category, singleMarkingPeriod=mp)
                                category.average = agg.scale.spruce(agg.cachedValue)
                            except:
                                category.average = None
    else:
        import_form = GradeUpload()
        verify_form = BenchmarkGradeVerifyForm()
    verify_form.fields['marking_periods'].queryset = available_mps
    verify_form.fields['marking_periods'].initial = verify_form.fields['marking_periods'].queryset
    
    return render_to_response('benchmark_grade/upload.html', {
        'request': request,
        'course': course,
        'import_form': import_form,
        'verify_form': verify_form.as_p(),
        'message': message,
        'mps': mps,
        'show_descriptions': show_descriptions
    }, RequestContext(request, {}),)

@user_passes_test(lambda u: u.groups.filter(name='students').count() > 0 or u.is_superuser, login_url='/')
def student_grade(request):
    """ A view for students to see their own grades in detail. """
    error_message = None
    mps = MarkingPeriod.objects.filter(school_year=SchoolYear.objects.get(active_year=True),
                                       start_date__lte=date.today()).order_by('-start_date')
    try:
        student = Student.objects.get(username=request.user.username)
    except:
        logging.warning('No student found for user "' + request.user.username + '"', exc_info=True)
        student = None
        mps = () 
        error_message = 'Sorry, a student record was not found for the username, ' + request.user.username + ', that you provided. Please contact the school registrar.'
    for mp in mps:
        mp.courses = Course.objects.filter(courseenrollment__user=student, graded=True, marking_period=mp).order_by('fullname')
        for course in mp.courses:
            course.categories = Category.objects.filter(item__course=course).distinct()
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
        'mps': mps,
        'error_message': error_message
    }, RequestContext(request, {}),)

@user_passes_test(lambda u: u.groups.filter(name='family').count() > 0 or u.is_superuser, login_url='/')
def family_grade(request):
    """ A view for family to see one or more students' grades in detail. """
    available_students = None
    student = None
    mps = None
    error_message = None

    available_students = Student.objects.filter(family_access_users=request.user)
    if available_students.count() == 1:
        student = available_students[0]
    elif 'student_username' not in request.GET:
        error_message = "Please select a student."
    elif available_students.filter(username=request.GET['student_username']).count() == 0:
        error_message = "Please select a student." # We'll be polite in response to your evil.
    else:
        student = available_students.get(username=request.GET['student_username'])
    if student is not None:
        mps = MarkingPeriod.objects.filter(school_year=SchoolYear.objects.get(active_year=True),
                                           start_date__lte=date.today()).order_by('-start_date')
        for mp in mps:
            mp.courses = Course.objects.filter(courseenrollment__user=student, graded=True, marking_period=mp).order_by('fullname')
            for course in mp.courses:
                course.categories = Category.objects.filter(item__course=course).distinct()
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
    return render_to_response('benchmark_grade/family_grade.html', {
        'student': student,
        'available_students': available_students,
        'today': date.today(),
        'mps': mps,
        'error_message': error_message
    }, RequestContext(request, {}),)

def gradebook(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    fifty = []
    i = 0
    while i < 50:
        i += 1
        fifty += ['foo' + str(i)]
    students = Student.objects.filter(inactive=False,course=course)
    
    cohorts = Cohort.objects.filter(student__in=students).distinct()
    marking_periods = MarkingPeriod.objects.filter(school_year__active_year=True)
    benchmarks = Benchmark.objects.all()[:30]
    
    
    return render_to_response('benchmark_grade/gradebook.html', {
        'fifty':fifty,
        'students':students,
        'course': course,
        'cohorts': cohorts,
        'marking_periods': marking_periods,
        'benchmarks': benchmarks,
    }, RequestContext(request, {}),)

def ajax_get_item_form(request, course_id, item_id=None):
    course = get_object_or_404(Course, pk=course_id)
    
    print request.POST
    if request.POST:
        if item_id:
            form = ItemForm(request.POST, instance=item)
        else:
            form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            # Should I use the django message framework to inform the user?
            # This would not work in ajax unless we make some sort of ajax
            # message handler.
            messages.success(request, '%s saved' % (item,))
            return HttpResponse('SUCCESS'); 
        
    else:
        if item_id:
            item = get_object_or_404(Item, pk=item_id)
            form = ItemForm(instance=item)
        else:
            form = ItemForm(initial={'course': course})
    
    print "oh hai"
    return render_to_response('sis/generic_form_fragment.html', {
        'form': form,
    }, RequestContext(request, {}),)

# Please add security checks
def ajax_save_grade(request, mark_id=None):
    return HttpResponse('SUCCESS');
