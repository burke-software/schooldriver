from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
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

from decimal import Decimal, ROUND_HALF_UP
import time
import logging

class struct(): pass

@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/')   
def schedule(request):
    years = SchoolYear.objects.all().order_by('-start_date')[:3]
    mps = MarkingPeriod.objects.all().order_by('-start_date')[:12]
    periods = Period.objects.all()[:20]
    courses = Course.objects.all().order_by('-startdate')[:20]
    
    if SchoolYear.objects.count() > 2: years.more = True
    if MarkingPeriod.objects.count() > 3: mps.more = True
    if Period.objects.count() > 6: periods.more = True
    if Course.objects.count() > 6: courses.more = True
    
    return render_to_response('schedule/schedule.html', {'request': request, 'years': years, 'mps': mps, 'periods': periods, 'courses': courses})

@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/')   
def schedule_enroll(request, id):
    course = Course.objects.get(id=id)
    if request.method == 'POST':
        form = EnrollForm(request.POST)
        if form.is_valid():
            CourseEnrollment.objects.filter(course=course, role='student').delete() # start afresh; only students passed in from the form should be enrolled
            # add manually select students first
            selected = form.cleaned_data['students']
            for student in selected:
                # add
                enroll, created = CourseEnrollment.objects.get_or_create(user=student, course=course, role="student")
                # left get_or_create in case another schedule_enroll() is running simultaneously
                if created: enroll.save()
            # add cohort students second
            cohorts = form.cleaned_data['cohorts']
            for cohort in cohorts:
                course.add_cohort(cohort)
            if 'save' in request.POST:
                return HttpResponseRedirect(reverse('admin:schedule_course_change', args=[id]))
    
    students = Student.objects.filter(courseenrollment__course=course)
    form = EnrollForm(initial={'students': students})
    return render_to_response('schedule/enroll.html', {'request': request, 'form': form, 'course': course})


@user_passes_test(lambda u: u.has_perm('sis.reports'), login_url='/')
def grade_analytics(request):
    def check_if_match(grade, filter, filter_grade):
        try:
            if grade == "P":
                grade = 100
            grade = float(grade)
            filter_grade = float(filter_grade)
            if filter == 'lt':
                if grade < filter_grade:
                    return True
            elif filter == 'lte':
                if grade <= filter_grade:
                    return True
            elif filter == 'gt':
                if grade > filter_grade:
                    return True
            elif filter == 'gte':
                if grade >= filter_grade:
                    return True
        except: pass
        return False

    form = GradeFilterForm()
    if request.method == 'POST':
        if 'edit' in request.POST:
            selected = request.POST.getlist('selected')
            return redirect('/admin/sis/student/?id__in=%s' % (','.join(selected),))
            
        form = GradeFilterForm(request.POST)
        if form.is_valid():
            ids = []
            if 'submit_course' in request.POST and 'course' in request.POST:
                course_selection = CourseSelectionForm(request.POST)
                if course_selection.is_valid():
                    for key in request.POST:
                        if key[:9] == "selected_":
                            ids.append(request.POST[key])
                    students = Student.objects.filter(id__in=ids)
                    if students and course_selection.cleaned_data['course']:
                        for student in students:
                            CourseEnrollment.objects.get_or_create(user=student, course=course_selection.cleaned_data['course'], role="student")
                        messages.success(request, 'Students added to %s!' % (course_selection.cleaned_data['course'].shortname,))
                    else:
                        messages.success(request, 'Did not enroll, please select students and a course.')
            course_selection = CourseSelectionForm()
            
            data = form.cleaned_data
            
            students = Student.objects.all()
            if not data['include_deleted']:
                students = students.filter(inactive=False)
            if data['filter_year']:
                students = students.filter(year__in=data['filter_year'])
            if data['in_individual_education_program']:
                students = students.filter(individual_education_program=True)
            if data['gpa']:
                # this will be something like filter(cache_gpa__lte=gpa)
                arg = 'cache_gpa__' + data['gpa_equality']
                students = students.filter(**{arg: data['gpa'],})
            
            courses = Course.objects.filter(courseenrollment__user__in=students, graded=True)
            if data['this_year']:
                courses = courses.filter(marking_period__school_year=SchoolYear.objects.get(active_year=True))
            elif not data['all_years']:
                courses = courses.filter(
                    marking_period__start_date__gte=data['date_begin'],
                    marking_period__end_date__lte=data['date_end'],
                )
            if data['marking_period']:
                courses = courses.filter(marking_period__in=data['marking_period'])
            
            students = students.distinct()
            courses = courses.distinct()
            
            mps_selected = []
            for mp in data['marking_period']:
                mps_selected.append(mp.id)
            show_students = []
            max_courses = 0
            
            (date_begin, date_end) = form.get_dates()
            
            # Pre load Discipline data
            if 'ecwsp.discipline' in settings.INSTALLED_APPS:
                if data['filter_disc_action'] and data['filter_disc'] and data['filter_disc_times']:
                    student_disciplines = students.filter(studentdiscipline__date__range=(date_begin, date_end),
                                                          studentdiscipline__action=data['filter_disc_action'],
                                                          ).annotate(action_count=Count('studentdiscipline__action'))
                if data['aggregate_disc'] and data['aggregate_disc_times']:
                    if data['aggregate_disc_major']:
                        student_aggregate_disciplines = students.filter(studentdiscipline__date__range=(date_begin, date_end),
                                                          studentdiscipline__action__major_offense=True,
                                                          ).annotate(action_count=Count('studentdiscipline'))
                    else:
                        student_aggregate_disciplines = students.filter(studentdiscipline__date__range=(date_begin, date_end),
                                                          ).annotate(action_count=Count('studentdiscipline'))
                    for student in students:
                        student.aggregate_disciplines = 0
                        for aggr in student_aggregate_disciplines:
                            if aggr.id == student.id:
                                student.aggregate_disciplines = aggr.action_count
                                break
            # Pre load Attendance data
            if data['filter_attn'] and data['filter_attn_times']:
                student_attendances = students.filter(student_attn__date__range=(date_begin, date_end),
                                                      student_attn__status__absent=True,
                                                      ).annotate(attn_count=Count('student_attn'))
            if data['filter_tardy'] and data['filter_tardy_times']:
                students_tardies = students.filter(student_attn__date__range=(date_begin, date_end),
                                                      student_attn__status__tardy=True,
                                                      ).annotate(tardy_count=Count('student_attn'))
                for student in students:
                    student.tardy_count = 0
                    for student_tardies in students_tardies:
                        if student_tardies.id == student.id:
                            student.tardy_count = student_tardies.tardy_count
                            break
                
            for student in students:
                # if this is a report, only calculate for selected students.
                if not 'xls' in request.POST or "selected" in request.POST:
                    num_matched = 0
                    add_to_list = True # If all criteria is met, add student to list
                    match_all = True
                    student.courses = []
                    i_courses = 0
                    
                    student.departments = []
                    for dept in Department.objects.all():
                        student.departments.append("")
                    
                    # for each grade for this student
                    course = None
                    done = False
                    grades_text = ""
                    if add_to_list and data['final_grade'] and data['final_grade_filter'] and data['final_grade_times']:
                        for course in student.course_set.filter(id__in=courses):
                            grade = course.get_final_grade(student)
                            if grade:
                                match = check_if_match(grade, data['final_grade_filter'], data['final_grade'])
                                if match:
                                    student.courses.append(str(course.shortname) + ' <br/>' + str(grade))
                                    num_matched += 1
                                    i_courses += 1
                                    if max_courses < i_courses: max_courses = i_courses
                                    i = 0
                                    for dept in Department.objects.all():
                                        if dept == course.department:
                                            student.departments[i] = "X"
                                        i += 1
                                else:
                                    match_all = False
                        if data['final_grade_times'] == "*" and not match_all:
                            add_to_list = False    
                        elif data['final_grade_times'] != "*" and not num_matched >= int(data['final_grade_times']):
                            add_to_list = False
                    if add_to_list and data['grade'] and data['grade_filter'] and data['grade_times']:
                        # Using just grades for optimization. Rather than for course, for mp, for grade.
                        for grade in student.grade_set.filter(course__in=courses, course__courseenrollment__user=student).order_by('course__department', 'marking_period').select_related():
                            if mps_selected == [] or grade.marking_period_id in mps_selected:
                                # if this is a new course, add previous course to student
                                if grade.course != course:
                                    if grades_text:
                                        student.courses.append(str(course.shortname) + ' <br/>' + grades_text)
                                        i_courses += 1
                                        if max_courses < i_courses: max_courses = i_courses
                                        i = 0
                                        for dept in Department.objects.all():
                                            if dept == course.department:
                                                student.departments[i] = "X"
                                            i += 1
                                    grades_text = ""
                                course = grade.course
                                
                                # data['each_marking_period'] and
                                if grade.override_final == False:
                                    grade_value = grade.get_grade()
                                    match = check_if_match(grade_value, data['grade_filter'], data['grade'])
                                    if match:
                                        grades_text += str(grade.marking_period.shortname) + ':' + str(grade_value) + " "
                                        num_matched += 1
                                    else:
                                        match_all = False
                                
                        if grades_text:
                            student.courses.append(str(course.shortname) + ' <br/>' + grades_text)
                            i_courses += 1
                            if max_courses < i_courses: max_courses = i_courses
                            i = 0
                            for dept in Department.objects.all():
                                if dept == course.department:
                                    student.departments[i] = "X"
                                i += 1
                        grades_text = ""
                        
                        if data['grade_times'] == "*" and not match_all:
                            add_to_list = False    
                        if data['grade_times'] != "*" and not num_matched >= int(data['grade_times']):
                            add_to_list = False
                    
                    # Check discipline
                    if add_to_list and 'ecwsp.discipline' in settings.INSTALLED_APPS:
                        if data['filter_disc_action'] and data['filter_disc'] and data['filter_disc_times']:
                            student.action_count = 0
                            for disc in student_disciplines:
                                if disc.id == student.id:
                                    student.action_count = disc.action_count
                                    break
                            if ((data['filter_disc'] == "lt" and not student.action_count < int(data['filter_disc_times'])) or 
                                (data['filter_disc'] == "lte" and not student.action_count <= int(data['filter_disc_times'])) or 
                                (data['filter_disc'] == "gt" and not student.action_count > int(data['filter_disc_times'])) or 
                                (data['filter_disc'] == "gte" and not student.action_count >= int(data['filter_disc_times']))
                            ):
                                add_to_list = False
                            else:
                                student.courses.append('%s: %s' % (data['filter_disc_action'], student.action_count))
                        
                        if data['aggregate_disc'] and data['aggregate_disc_times']:
                            if ((data['aggregate_disc'] == "lt" and not student.aggregate_disciplines < int(data['aggregate_disc_times'])) or 
                                (data['aggregate_disc'] == "lte" and not student.aggregate_disciplines <= int(data['aggregate_disc_times'])) or 
                                (data['aggregate_disc'] == "gt" and not student.aggregate_disciplines > int(data['aggregate_disc_times'])) or 
                                (data['aggregate_disc'] == "gte" and not student.aggregate_disciplines >= int(data['aggregate_disc_times']))
                            ):
                                add_to_list = False
                            else:
                                student.courses.append('%s: %s' % ("Aggregate Discipline", student.aggregate_disciplines))
                    
                    # Check Attendance
                    if add_to_list and data['filter_attn'] and data['filter_attn_times']:
                        try:
                            student.attn_count = student_attendances.get(id=student.id).attn_count
                        except:
                            student.attn_count = 0
                        if ((data['filter_attn'] == "lt" and not student.attn_count < int(data['filter_attn_times'])) or 
                            (data['filter_attn'] == "lte" and not student.attn_count <= int(data['filter_attn_times'])) or 
                            (data['filter_attn'] == "gt" and not student.attn_count > int(data['filter_attn_times'])) or 
                            (data['filter_attn'] == "gte" and not student.attn_count >= int(data['filter_attn_times']))
                        ):
                            add_to_list = False
                        else:
                            student.courses.append('Absents: %s' % (student.attn_count,))
                            
                    # Tardies
                    if add_to_list and data['filter_tardy'] and data['filter_tardy_times']:
                        if ((data['filter_tardy'] == "lt" and not student.tardy_count < int(data['filter_tardy_times'])) or 
                            (data['filter_tardy'] == "lte" and not student.tardy_count <= int(data['filter_tardy_times'])) or 
                            (data['filter_tardy'] == "gt" and not student.tardy_count > int(data['filter_tardy_times'])) or 
                            (data['filter_tardy'] == "gte" and not student.tardy_count >= int(data['filter_tardy_times']))
                        ):
                            add_to_list = False
                        else:
                            student.courses.append('Tardies: %s' % (student.tardy_count,))
                    
                    if add_to_list:
                        show_students.append(student)
                
            # Print xls report
            if 'xls' in request.POST or 'xls_asp' in request.POST:
                pref = UserPreference.objects.get_or_create(user=request.user)[0]
                titles = ['Student']
                data = []
                for student in show_students:
                    if unicode(student.id) in request.POST.getlist('selected'):
                        row = [student]
                        pref.get_additional_student_fields(row, student, show_students, titles)
                        i = 0
                        for course in student.courses:
                            row.append(course.replace("<br/>", " "))
                            i += 1
                        # padding data
                        while i < max_courses:
                            row.append("")
                            i += 1
                        
                        if 'xls_asp' in request.POST:
                            for dept in student.departments:
                                row.append(dept)
                        
                        data.append(row)
                titles.append('Grades')
                
                i = 1
                while i < max_courses:
                    titles.append('')
                    i += 1
                if 'xls_asp' in request.POST:
                    for dept in Department.objects.all():
                        titles.append(dept)
                report = xlsReport(data, titles, "analytics.xls", heading="Analytics Report")
                return report.finish()
                
            return render_to_response('schedule/grade_analytics.html', {'form': form, 'course_selection': None, 'students': show_students,}, RequestContext(request, {}),)
    return render_to_response('schedule/grade_analytics.html', {'form': form,}, RequestContext(request, {}),)
