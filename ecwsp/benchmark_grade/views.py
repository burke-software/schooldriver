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
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q, Max
from django.db import transaction
from django.template import RequestContext

from ecwsp.sis.models import SchoolYear, Student, Faculty
#from ecwsp.sis.uno_report import *
#from ecwsp.sis.xlsReport import *
from ecwsp.schedule.models import Course, MarkingPeriod
#from ecwsp.schedule.forms import 
from ecwsp.grades.forms import GradeUpload
#from ecwsp.administration.models import *
from ecwsp.benchmark_grade.models import Category, Mark, Aggregate, Item, Demonstration
from ecwsp.benchmark_grade.forms import BenchmarkGradeVerifyForm, GradebookFilterForm, ItemForm, DemonstrationForm
from ecwsp.benchmarks.models import Benchmark
from ecwsp.benchmark_grade.utility import gradebook_get_average, gradebook_recalculate_on_item_change, gradebook_recalculate_on_mark_change
from ecwsp.benchmark_grade.utility import benchmark_find_calculation_rule

from decimal import Decimal
import logging
import json
import datetime

#@user_passes_test(lambda u: u.groups.filter(Q(name='teacher') | Q(name="registrar")).count() > 0 or u.is_superuser, login_url='/')
@user_passes_test(lambda u: u.groups.filter(name="registrar").count() > 0 or u.is_superuser, login_url='/')
def benchmark_grade_upload(request, id):
    """ Grades can only be entered/changed by spreadsheet upload. """
    course = Course.objects.get(id=id)
    message = ''
    mps = ()
    
    available_mps = course.marking_period.filter(Q(active=True) | Q(start_date__lt=datetime.date.today))
    show_descriptions = True
    if request.method == 'POST':
        if 'upload' in request.POST:
            import_form = GradeUpload(request.POST, request.FILES)
            verify_form = BenchmarkGradeVerifyForm() 
            if import_form.is_valid():
                from ecwsp.benchmark_grade.importer import BenchmarkGradeImporter
                importer = BenchmarkGradeImporter(request.FILES['file'], request.user)
                message = importer.import_grades(course, import_form.cleaned_data['marking_period'])
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
                                                                 item__marking_period=mp).order_by('-item__date', 'item__name',
                                                                                                   'description')
                            if not verify_form.cleaned_data['all_demonstrations']:
                                category.marks = category.marks.filter(Q(description='Session') | Q(description=''))
                                # If all_demonstrations aren't shown, "Session" is assumed; description is unnecessary
                                show_descriptions = False
                            try:
                                agg = Aggregate.objects.get(student=student, course=course,
                                                            category=category, marking_period=mp)
                                category.average = agg.cached_value
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

def student_family_grade_common(student):
    PASSING_GRADE = 3 # TODO: pull config value. Roche has it set to something crazy now and I don't want to deal with it
    school_year = SchoolYear.objects.get(active_year=True)
    mps = MarkingPeriod.objects.filter(school_year=school_year, start_date__lte=datetime.date.today()).order_by('-start_date')
    calculation_rule = benchmark_find_calculation_rule(school_year)
    for mp in mps:
        mp.courses = Course.objects.filter(courseenrollment__user=student, graded=True, marking_period=mp).order_by('fullname')
        for course in mp.courses:
            course.categories = Category.objects.filter(item__course=course, item__mark__student=student).distinct()
            course.category_by_name = {}
            for category in course.categories:
                category.percentage = calculation_rule.per_course_category_set.get(
                    category=category, apply_to_departments=course.department).weight * 100
                category.percentage = category.percentage.quantize(Decimal('0'))
                category.average = gradebook_get_average(student, course, category, mp, None)
                items = Item.objects.filter(course=course, category=category, mark__student=student).annotate(best_mark=Max('mark__mark'))
                counts = {}
                counts['total'] = items.exclude(best_mark=None).distinct().count()
                counts['missing'] = items.filter(best_mark__lt=PASSING_GRADE).distinct().count()
                counts['passing'] = items.filter(best_mark__gte=PASSING_GRADE).distinct().count()
                if counts['total']:
                    counts['percentage'] = (Decimal(counts['passing']) / counts['total'] * 100).quantize(Decimal('0'))
                course.category_by_name[category.name] = counts
            course.average = gradebook_get_average(student, course, None, mp, None)
    return mps

@user_passes_test(lambda u: u.groups.filter(name='students').count() > 0 or u.is_superuser, login_url='/')
def student_grade(request):
    """ A view for students to see their own grades in summary. """
    error_message = None
    try:
        student = Student.objects.get(username=request.user.username)
        mps = student_family_grade_common(student)
    except Student.DoesNotExist:
        logging.warning('No student found for user "' + request.user.username + '"', exc_info=True)
        student = None
        mps = () 
        error_message = 'Sorry, a student record was not found for the username, ' + request.user.username + \
                        ', that you provided. Please contact the school registrar.'
    
    #return HttpResponse(s)
    return render_to_response('benchmark_grade/student_grade.html', {
        'student': student,
        'mps': mps,
        'error_message': error_message,
    }, RequestContext(request, {}),)

def student_family_grade_course_detail_common(student, course, mp):
    course.categories = Category.objects.filter(item__course=course, item__mark__student=student).distinct()
    for category in course.categories:
        items = Item.objects.filter(course=course, category=category, mark__student=student).annotate(best_mark=Max('mark__mark'))
        item_names = items.values_list('name').distinct()
        category.item_groups = {}
        for item_name_tuple in item_names:
            item_name = item_name_tuple[0]
            category.item_groups[item_name] = items.filter(name=item_name).distinct() 
        category.average = gradebook_get_average(student, course, category, mp, None)
    return course
    
@user_passes_test(lambda u: u.groups.filter(name='students').count() > 0 or u.is_superuser, login_url='/')
def student_grade_course_detail(request, course_id, marking_period_id):
    """ A view for students to see their own grades in detail. """
    course = get_object_or_404(Course, pk=course_id)
    mp = get_object_or_404(MarkingPeriod, pk=marking_period_id)
    error_message = None
    try:
        student = Student.objects.get(username=request.user.username)
        course = student_family_grade_course_detail_common(student, course, mp)
    except Student.DoesNotExist:
        logging.warning('No student found for user "' + request.user.username + '"', exc_info=True)
        student = None
        error_message = 'Sorry, a student record was not found for the username, ' + request.user.username + \
                        ', that you provided. Please contact the school registrar.'

    #return HttpResponse(s)
    return render_to_response('benchmark_grade/student_grade_course_detail.html', {
        'course': course,
        'mp': mp,
        'error_message': error_message,
    }, RequestContext(request, {}),)

@user_passes_test(lambda u: u.groups.filter(name='family').count() > 0 or u.is_superuser, login_url='/')
def family_grade(request):
    """ A view for family to see one or more students' grades in summary. """
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
        mps = student_family_grade_common(student)
    return render_to_response('benchmark_grade/student_grade.html', {
        'student': student,
        'available_students': available_students,
        'mps': mps,
        'error_message': error_message
    }, RequestContext(request, {}),)

@user_passes_test(lambda u: u.groups.filter(name='family').count() > 0 or u.is_superuser, login_url='/')
def family_grade_course_detail(request, course_id, marking_period_id):
    """ A view for family to see a student's grades in detail. """
    course = get_object_or_404(Course, pk=course_id)
    mp = get_object_or_404(MarkingPeriod, pk=marking_period_id)
    available_students = None
    student = None
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
        course = student_family_grade_course_detail_common(student, course, mp)
    else:
        course = None
        mp = None

    return render_to_response('benchmark_grade/student_grade_course_detail.html', {
        'student': student,
        'available_students': available_students,
        'course': course,
        'mp': mp,
        'error_message': error_message
    }, RequestContext(request, {}),)

@staff_member_required
def gradebook(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    try:
        teacher = Faculty.objects.get(username=request.user.username)
        teacher_courses = Course.objects.filter(
            graded=True,
            marking_period__school_year__active_year=True,
        ).filter(Q(teacher=teacher) | Q(secondary_teachers=teacher)).distinct()
    except Faculty.DoesNotExist:
        teacher_courses = None

    if not request.user.is_superuser and not request.user.groups.filter(name='registrar').count() and \
    (teacher_courses is None or course not in teacher_courses):
        return HttpResponse(status=403)

    #students = Student.objects.filter(inactive=False,course=course)
    students = Student.objects.filter(course=course)
    items = Item.objects.filter(course=course)
    filtered = False

    if request.GET:
        filter_form = GradebookFilterForm(request.GET)
        filter_form.update_querysets(course)
        if filter_form.is_valid():
            for filter_key, filter_value in filter_form.cleaned_data.iteritems():
                if filter_value is not None:
                    try:
                        if not len(filter_value):
                            continue
                    except TypeError:
                        # not everything has a len
                        pass
                    if filter_key == 'cohort': 
                        students = students.filter(cohorts=filter_value)
                    if filter_key == 'marking_period':
                        items = items.filter(marking_period=filter_value)
                    if filter_key == 'benchmark':
                        items = items.filter(benchmark__in=filter_value)
                    if filter_key == 'category':
                        items = items.filter(category=filter_value)
                    if filter_key == 'assignment_type':
                        items = items.filter(assignment_type=filter_value)
                    if filter_key == 'name':
                        items = items.filter(name__icontains=filter_value)
                    if filter_key == 'date_begin':
                        items = items.filter(date__gt=filter_value)
                    if filter_key == 'date_end':
                        items = items.filter(date__lt=filter_value)
                    filtered = True
    else:
        # show only the active marking period by default
        active_mps = course.marking_period.filter(active=True)
        if active_mps:
            filter_form = GradebookFilterForm(initial={'marking_period': active_mps[0]})
            items = items.filter(marking_period=active_mps[0])
        else:
            filter_form = GradebookFilterForm()
        filter_form.update_querysets(course)
    
    # Freeze these now in case someone else gets in here!
    items = items.order_by('id').all()
    # whoa, super roll of the dice. is Item.demonstration_set really guaranteed to be ordered by id?
    # precarious; sorting must match items (and demonstrations!) exactly
    marks = Mark.objects.filter(item__in=items).order_by('item__id', 'demonstration__id').all() 
    items_count = items.filter(demonstration=None).count() + Demonstration.objects.filter(item__in=items).count()
    for student in students:
        student_marks = marks.filter(student=student)
        if student_marks.count() < items_count:
            # maybe student enrolled after assignments were created
            for item in items:
                if len(item.demonstration_set.all()):
                    # must create mark for each demonstration
                    for demonstration in item.demonstration_set.all():
                        mark, created = Mark.objects.get_or_create(item=item, demonstration=demonstration, student=student)
                        if created:
                            mark.save()
                else:
                    # a regular item without demonstrations; make only one mark
                    mark, created = Mark.objects.get_or_create(item=item, student=student)
                    if created:
                        mark.save()
        if student_marks.count() > items_count:
            # Yikes, there are multiple marks per student per item. Stop loading the gradebook now.
            if 'dangerous' in request.GET:
                pass
            else:
                raise Exception('Multiple marks per student per item.')
        student.marks = student_marks
        student.average = gradebook_get_average(student, course, None, None, None)
        if filtered:
            student.filtered_average = gradebook_get_average(student, course, filter_form.cleaned_data['category'],
                                                             filter_form.cleaned_data['marking_period'], items)
        # TC's column of counts
        # TODO: don't hardcode
        standards_category = Category.objects.get(name='Standards')
        PASSING_GRADE = 3
        standards_objects = Item.objects.filter(course=course, category=standards_category, mark__student=student).annotate(best_mark=Max('mark__mark')).exclude(best_mark=None)
        standards_count_passing = standards_objects.filter(best_mark__gte=PASSING_GRADE).count()
        standards_count_total = standards_objects.count()
        if standards_count_total:
            student.standards_counts = '{} / {} ({:.0f}%)'.format(standards_count_passing, standards_count_total, 100.0 * standards_count_passing / standards_count_total)
        else:
            student.standards_counts_ = None
        if filtered:
            standards_objects = items.filter(course=course, category=standards_category, mark__student=student).annotate(best_mark=Max('mark__mark')).exclude(best_mark=None)
            standards_count_passing = standards_objects.filter(best_mark__gte=PASSING_GRADE).count()
            standards_count_total = standards_objects.count()
            if standards_count_total:
                student.filtered_standards_counts = '{} / {} ({:.0f}%)'.format(standards_count_passing, standards_count_total, 100.0 * standards_count_passing / standards_count_total)
            else:
                student.filtered_standards_counts = None

        # TC's row of counts
        # TODO: don't hardcode
        for item in items:
            if item.category != standards_category:
                item.marks_counts = 'N/A'
                continue
            marks_count_passing = item.mark_set.filter(mark__gte=PASSING_GRADE).count()
            marks_count_total = item.mark_set.exclude(mark=None).count()
            if marks_count_total:
                item.marks_counts = '{} / {} ({:.0f}%)'.format(marks_count_passing, marks_count_total, 100.0 * marks_count_passing / marks_count_total)
            else:
                item.marks_counts = None
            

    return render_to_response('benchmark_grade/gradebook.html', {
        'items': items,
        'students': students,
        'course': course,
        'teacher_courses': teacher_courses,
        'filtered' : filtered,
        'filter_form': filter_form,
    }, RequestContext(request, {}),)

@staff_member_required
@transaction.commit_on_success
def ajax_delete_item_form(request, course_id, item_id):
    item = get_object_or_404(Item, pk=item_id)
    ghost_item = Item()
    ghost_item.course = item.course
    ghost_item.category = item.category
    ghost_item.marking_period = item.marking_period
    message = '%s deleted' % (item,)
    item.delete()
    gradebook_recalculate_on_item_change(ghost_item)
    messages.success(request, message)
    return HttpResponse('SUCCESS')

@staff_member_required
@transaction.commit_on_success
def ajax_get_item_form(request, course_id, item_id=None):
    ''' the transaction decorator helps, but people can still hammer the submit button
    and create tons of assignments. for some reason, only one shows up right away, and the rest
    don't appear until reload '''
    course = get_object_or_404(Course, pk=course_id)
    item = None
    lists = None
    
    if request.POST:
        if item_id:
            item = get_object_or_404(Item, pk=item_id)
            form = ItemForm(request.POST, instance=item, prefix="item")
        else:
            form = ItemForm(request.POST, prefix="item")
        if form.is_valid():
            item = form.save()
            if item_id is None:
                # a new item!
                dem = None
                if item.category.allow_multiple_demonstrations:
                    # must have at least one demonstration; create a new one
                    dem = Demonstration()
                    dem.name = 'Dem. 1'
                    dem.item = item
                    dem.save()
                # must create blank marks for each student
                for student in Student.objects.filter(course=course):
                    mark, created = Mark.objects.get_or_create(item=item, student=student, demonstration=dem)
                    if created:
                        mark.save()

            # Should I use the django message framework to inform the user?
            # This would not work in ajax unless we make some sort of ajax
            # message handler.
            messages.success(request, '%s saved' % (item,))
            return HttpResponse('SUCCESS')
        
    else:
        if item_id:
            item = get_object_or_404(Item, pk=item_id)
            form = ItemForm(instance=item, prefix="item")
            # TODO: remove TC hard-coding
            students_missing = Student.objects.filter(mark__item=item).annotate(best_mark=Max('mark__mark')).filter(best_mark__lt=3)
            if not students_missing: students_missing = ('None',)
            lists = ({'heading':'Students Missing This Item', 'items':students_missing},)
        else:
            active_mps = course.marking_period.filter(active=True)
            if active_mps:
                form = ItemForm(initial={'course': course, 'marking_period':active_mps[0]}, prefix="item")
            else:
                form = ItemForm(initial={'course': course}, prefix="item")
    
    form.fields['marking_period'].queryset = course.marking_period.all()
    form.fields['category'].queryset = Category.objects.filter(display_in_gradebook=True)
    form.fields['benchmark'].queryset = Benchmark.objects.filter()

    form.fields['category'].widget.attrs = {
        'onchange': "Dajaxice.ecwsp.benchmark_grade.check_fixed_points_possible(Dajax.process, {'category':this.value})"}
    if item and item.category.fixed_points_possible:
        form.fields['points_possible'].widget.attrs = {'disabled': 'true'}

    return render_to_response('sis/generic_form_fragment.html', {
        'form': form,
        'item_id': item_id,
        'lists': lists,
    }, RequestContext(request, {}),)

@staff_member_required
@transaction.commit_on_success
def ajax_delete_demonstration_form(request, course_id, demonstration_id):
    demonstration = get_object_or_404(Demonstration, pk=demonstration_id)
    item = demonstration.item
    ghost_item = Item()
    ghost_item.course = item.course
    ghost_item.category = item.category
    ghost_item.marking_period = item.marking_period
    message = '%s deleted' % (demonstration,)
    demonstration.delete()
    if not Demonstration.objects.filter(item=item):
        if Mark.objects.filter(item=item):
            raise Exception('Stray marks found after attempting to delete last demonstration.')
        else:
            # the last demonstration is dead. kill the item.
            item.delete()

    gradebook_recalculate_on_item_change(ghost_item)
    messages.success(request, message)
    return HttpResponse('SUCCESS')

@staff_member_required
@transaction.commit_on_success
def ajax_get_demonstration_form(request, course_id, demonstration_id=None):
    ''' the transaction decorator helps, but people can still hammer the submit button
    and create tons of assignments. for some reason, only one shows up right away, and the rest
    don't appear until reload '''
    course = get_object_or_404(Course, pk=course_id)
    lists = None
    
    if request.POST:
        if demonstration_id:
            demonstration = get_object_or_404(Demonstration, pk=demonstration_id)
            form = DemonstrationForm(request.POST, instance=demonstration, prefix="demonstration")
        else:
            form = DemonstrationForm(request.POST, prefix="demonstration")
        if form.is_valid():
            demonstration = form.save()
            if demonstration_id is None:
                # a new demonstration; must create blank marks for each student
                for student in Student.objects.filter(course=course):
                    mark, created = Mark.objects.get_or_create(item=demonstration.item, demonstration=demonstration, student=student)
                    if created:
                        mark.save()

            # Should I use the django message framework to inform the user?
            # This would not work in ajax unless we make some sort of ajax
            # message handler.
            messages.success(request, '%s saved' % (demonstration,))
            return HttpResponse('SUCCESS')
        
    else:
        if demonstration_id:
            demonstration = get_object_or_404(Demonstration, pk=demonstration_id)
            form = DemonstrationForm(instance=demonstration, prefix="demonstration")
            # TODO: remove TC hard-coding
            students_missing = Student.objects.filter(mark__demonstration=demonstration, mark__mark__lt=3)
            if not students_missing: students_missing = ('None',)
            lists = ({'heading':'Students Missing This Demonstration', 'items':students_missing},)
        else:
            form = DemonstrationForm(initial={'course': course}, prefix="demonstration")
    
    form.fields['item'].queryset = Item.objects.filter(course=course,
                                                       category__display_in_gradebook=True, category__allow_multiple_demonstrations=True)

    return render_to_response('benchmark_grade/demonstration_form_fragment.html', {
        'form': form,
        'demonstration_id': demonstration_id,
        'lists': lists,
    }, RequestContext(request, {}),)

@staff_member_required
def ajax_get_student_info(request, course_id, student_id):
    student = get_object_or_404(Student, pk=student_id)
    course = get_object_or_404(Course, pk=course_id)

    # TODO: remove TC hard-coding
    standards_missing = Item.objects.filter(course=course, category__name='Standards', mark__student=student).annotate(best_mark=Max('mark__mark')).filter(best_mark__lt=3)
    if not standards_missing: standards_missing = ('None',)
    lists = ({'heading':'Standards Missing for {}'.format(student), 'items':standards_missing},)

    return render_to_response('sis/generic_list_fragment.html', {
        'lists': lists,
    }, RequestContext(request, {}),)

@staff_member_required
def ajax_save_grade(request):
    if 'mark_id' in request.POST and 'value' in request.POST:
        mark_id = request.POST['mark_id'].strip()
        value = request.POST['value'].strip()
        try: mark = Mark.objects.get(id=mark_id)
        except Mark.DoesNotExist: return HttpResponse('NO MARK WITH ID ' + mark_id, status=404) 
        if not request.user.is_superuser and not request.user.groups.filter(name='registrar').count() \
            and request.user.username != mark.item.course.teacher.username \
            and not mark.item.course.secondary_teachers.filter(username=request.user.username).count():
            return HttpResponse(status=403)

        if len(value) and value.lower != 'none':
            mark.mark = value
        else:
            mark.mark = None
            value = 'None'
        # temporarily log who's changing stuff since i'll have to manually recalculate averages later
        mark.description += ',' + request.user.username
        try:
            mark.full_clean()
            mark.save()
        except Exception as e:
            return HttpResponse(e, status=400)
        gradebook_recalculate_on_mark_change(mark)
        # just the whole course average for now
        # TODO: update filtered average
        average = gradebook_get_average(mark.student, mark.item.course, None, None, None) 
        return HttpResponse(json.dumps({'success': 'SUCCESS', 'value': value, 'average': str(average)}))
    else:
        return HttpResponse('POST DATA INCOMPLETE', status=400) 
