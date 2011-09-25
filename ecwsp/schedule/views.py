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
            # add manually select students first
            selected = form.cleaned_data['students']
            for student in Student.objects.filter(inactive=False):
                if student in selected:
                    # add
                    enroll, created = CourseEnrollment.objects.get_or_create(user=student, course=course, role="student")
                    if created: enroll.save()
                else:
                    # remove
                    try:
                        enroll = CourseEnrollment.objects.get(user=student, course=course, role="student")
                        enroll.delete()
                    except: pass
            # add cohort students second
            cohorts = form.cleaned_data['cohorts']
            for cohort in cohorts:
                course.add_cohort(cohort)
            if 'save' in request.POST:
                return HttpResponseRedirect(reverse('admin:schedule_course_change', args=[id]))
    
    students = Student.objects.filter(courseenrollment__course=course)
    form = EnrollForm(initial={'students': students})
    return render_to_response('schedule/enroll.html', {'request': request, 'form': form, 'course': course})

@user_passes_test(lambda u: u.groups.filter(name='teacher').count() > 0 or u.is_superuser, login_url='/')   
def teacher_grade(request):
    if Faculty.objects.filter(username=request.user.username):
        teacher = Faculty.objects.get(username=request.user.username)
    else:
        messages.info(request, 'You do not have any courses.')
        return HttpResponseRedirect(reverse('admin:index'))
    courses = Course.objects.filter(
            graded=True,
            marking_period__school_year__active_year=True,
        ).filter(Q(teacher=teacher) | Q(secondary_teachers=teacher)).distinct()

    if "ecwsp.engrade_sync" in settings.INSTALLED_APPS:
        if request.method == 'POST':
            form = EngradeSyncForm(request.POST)
            if form.is_valid():
                try:
                    from ecwsp.engrade_sync.engrade_sync import EngradeSync
                    marking_period = form.cleaned_data['marking_period']
                    include_comments = form.cleaned_data['include_comments']
                    courses = teacher.course_set.filter(marking_period=marking_period, graded=True)
                    sec_courses = teacher.secondary_course_set.filter(marking_period=marking_period, graded=True)
                    courses = courses | sec_courses
                    courses = courses.distinct()
                    es = EngradeSync()
                    for course in courses:
                        es.sync_course_grades(course, marking_period, include_comments)
                    messages.success(request, 'Engrade Sync successful. Please verify each course!')
                except:
                    messages.info(request, 'Engrade Sync unsuccessful. Contact an administrator.')
                    print >> sys.stderr, str(sys.exc_info()[1].message)
            else:
                messages.info(request, 'You must select a valid marking period')
        engrade_sync = True
        form = EngradeSyncForm()
    else:
        engrade_sync = False
        form = None
    return render_to_response('schedule/teacher_grade.html', {'request': request, 'courses': courses, 'form': form,
                                                              'engrade_sync': engrade_sync}, RequestContext(request, {}),)

@user_passes_test(lambda u: u.groups.filter(Q(name='teacher') | Q(name="registrar")).count() > 0 or u.is_superuser, login_url='/')   
def teacher_grade_download(request, id, type=None):
    """ Download grading spreadsheet of requested class 
    id: course id
    type: filetype (ods or xls)"""
    if not type:
        profile = UserPreference.objects.get_or_create(user=request.user)[0]
        type = profile.get_format(type="spreadsheet")
    course = Course.objects.get(id=id)
    template, created = Template.objects.get_or_create(name="grade spreadsheet")
    filename = unicode(course) + "_grade"
    data={}
    data['$students'] = []
    data['$username'] = []
    
    for student in course.get_enrolled_students(show_deleted=True):
        data['$students'].append(unicode(student))
        data['$username'].append(unicode(student.username))
    
    # Libreoffice crashes sometimes, maybe 5% of the time. So try it some more!
    for x in range(0,3):
        try:
            return replace_spreadsheet(template.file.path, filename, data, type)
        except:
            logger.error('Libreoffice died, try one more time')
            time.sleep(3)
    return replace_spreadsheet(template.file.path, filename, data, type)

def view_comment_codes(request):
    comments = GradeComment.objects.all()
    msg = ""
    for comment in comments:
        msg += "%s <br/>" % (comment,)
    return render_to_response('sis/generic_msg.html', {'msg': msg,}, RequestContext(request, {}),)

def handle_grade_save(request, course=None):
    """ Customized code to process POST data from the gradesheets (both course and student) """
    for input, value in request.POST.items():
        try:
            input = input.split('_')
            if input[0] == "grade":
                grade = Grade.objects.get(id=input[1])
                if grade.get_grade() != value:
                    grade.set_grade(value)
                    grade.save()
            elif input[0] == "comment":
                grade = Grade.objects.get(id=input[1])
                if grade.comment != value:
                    grade.comment = value
                    grade.save()
        except:
            try:
                messages.info(request, 'Error in grade for ' + unicode(Student.objects.get(id=input[1])))
            except:
                try:
                    messages.info(request, 'Error in grade for ' + unicode(Grade.objects.get(id=input[1]).student))
                except:
                    messages.info(request, 'Unknown error ' + unicode(input))
    handle_final_grade_save(request, course=course)

def handle_final_grade_save(request, course=None):
    for input, value in request.POST.items():
        try:
            input = input.split('_')
            # Final grade
            if input[0] == "gradefinalform":
                student = Student.objects.get(id=input[1])
                grade = value
                if not Grade.objects.filter(course=course, override_final=True, student=student).count():
                    try:
                        # check if number
                        Decimal(grade)
                        # Check if it's the same value, thus no override needed
                        final = course.calculate_final_grade(student)
                        # Sanitize! Force it to 2 decimal points
                        grade = Decimal(grade).quantize(Decimal("0.01"), ROUND_HALF_UP)
                        if grade != final:
                            # Different so override!
                            grade_object, created = Grade.objects.get_or_create(course=course, override_final=True, student=student)
                            grade_object.set_grade(grade)
                            grade_object.save()
                    except:
                        # not number
                        if not grade == "" and not grade == None and not grade == "None":
                            grade_object, created = Grade.objects.get_or_create(course=course, override_final=True, student=student)
                            grade_object.set_grade(grade)
                            grade_object.save()
                else:
                    # override already exists
                    grade_object, created = Grade.objects.get_or_create(course=course, override_final=True, student=student)
                    if grade == "" or grade == None or grade == "None":
                        grade_object.delete()
                    else:
                        grade_object.set_grade(grade)
                        grade_object.save()
            elif input[0] == "coursefinalform":  # coursefinalform_course.id_student.id    
                course = Course.objects.get(id=input[1])
                student = Student.objects.get(id=input[2])
                grade = value
                if not Grade.objects.filter(course=course, override_final=True, student=student).count():
                    try:
                        # check if number
                        Decimal(grade)
                        # Check if it's the same value, thus no override needed
                        final = course.calculate_final_grade(student)
                        # Sanitize! Force it to 2 decimal points
                        grade = Decimal(grade).quantize(Decimal("0.01"), ROUND_HALF_UP)
                        if grade != final:
                            # Different so override!
                            grade_object, created = Grade.objects.get_or_create(course=course, override_final=True, student=student)
                            grade_object.set_grade(grade)
                            grade_object.save()
                    except:
                        # not number
                        if not grade == "" and not grade == None and not grade == "None":
                            grade_object, created = Grade.objects.get_or_create(course=course, override_final=True, student=student)
                            grade_object.set_grade(grade)
                            grade_object.save()
                else:
                    # override already exists
                    grade_object, created = Grade.objects.get_or_create(course=course, override_final=True, student=student)
                    if grade == "" or grade == None or grade == "None":
                        grade_object.delete()
                    else:
                        grade_object.set_grade(grade)
                        grade_object.save()
        except:
            try:
                messages.info(request, 'Error in grade for ' + unicode(Student.objects.get(id=input[1])))
            except:
                try:
                    messages.info(request, 'Error in grade for ' + unicode(Grade.objects.get(id=input[1]).student))
                except:
                    messages.info(request, 'Unknown error ' + unicode(input))

@user_passes_test(lambda u: u.has_perm('schedule.change_grade'))
def student_gradesheet(request, id, year_id=None):
    student = Student.objects.get(id=id)
    if request.POST:
        handle_grade_save(request)
    courses = student.course_set.filter(graded=True)
    school_years = SchoolYear.objects.filter(markingperiod__course__enrollments__student=student).distinct()
    if year_id:
        school_year = SchoolYear.objects.get(id=year_id)
    else:
        school_year = SchoolYear.objects.get(active_year=True)
    courses = courses.filter(marking_period__school_year=school_year).distinct()
    for course in courses:
        for mp in school_year.markingperiod_set.all():
            grade, created = Grade.objects.get_or_create(student=student, course=course, marking_period=mp, final=True)
        course.grades = student.grade_set.filter(course=course, final=True, override_final=False)
        
        try:
            override_grade = course.grade_set.get(student=student, override_final=True)
            course.final = unicode(override_grade.get_grade())
            course.final_override = True  # effects CSS
        except:
            course.final = course.calculate_final_grade(student)
        
    return render_to_response('schedule/student_gradesheet.html', {
        'request': request,
        'student': student,
        'courses': courses,
        'school_year': school_year,
        'school_years': school_years,
    }, RequestContext(request, {}),)

@user_passes_test(lambda u: u.groups.filter(Q(name='teacher') | Q(name="registrar")).count() > 0 or u.is_superuser, login_url='/')
def teacher_grade_upload(request, id):
    """ This view is for inputing grades. It usually is done by uploading a spreadsheet.
    However it can also be done by manually overriding grades. This requires
    registrar level access. """
    course = Course.objects.get(id=id)
    students = course.get_enrolled_students(show_deleted=True)
    grades = course.grade_set.all()
    
    if request.method == 'POST' and 'upload' in request.POST:
        import_form = GradeUpload(request.POST, request.FILES)
        if import_form.is_valid():
            from sis.importer import *
            importer = Importer(request.FILES['file'], request.user)
            importer.import_grades(course, import_form.cleaned_data['marking_period'])
    else:
        import_form = GradeUpload()
        
    if request.method == 'POST' and 'edit' in request.POST:
        # save grades
        handle_grade_save(request, course)
    for student in students:
        student.grades = []
        # display grades include mid marks and are not used for calculations
        student.display_grades = []
        student.comments = []
        student.grade_id = []
    
    marking_periods = course.marking_period.all().order_by('start_date')
    
    for mp in marking_periods:
        if Grade.objects.filter(course=course, marking_period=mp, final=False).count():
            mp.has_mid = True
        else:
            mp.has_mid = False
    
    x = 0
    y = 0
    for mp in marking_periods:
        y = 0
        for student in students:
            grade, created = Grade.objects.get_or_create(student=student, course=course, marking_period=mp, final=True)
            grade_struct = struct()
            grade_struct.grade = grade.get_grade()
            grade_struct.id = grade.id
            grade_struct.x = x
            grade_struct.y = y
            student.display_grades.append(grade_struct)
            student.comments.append(grade.comment)
            
            
            if mp.has_mid:
                mid_grade, created = Grade.objects.get_or_create(student=student, course=course, marking_period=mp, final=False)
                grade_struct = struct()
                grade_struct.grade = mid_grade.get_grade()
                grade_struct.id = mid_grade.id
                grade_struct.x = x + 1
                grade_struct.y = y
                student.display_grades.append(grade_struct)
                student.comments.append(mid_grade.comment)
                student.grade_id.append(mid_grade.id)
            y += 1
        x += 1
        if mp.has_mid: x += 1
        last_y = y - 1
        last_x = x
            
    y = 0
    for student in students:
        student.final_x = x
        student.final_y = y
        y += 1
        try:
            override_grade = Grade.objects.get(student=student, course=course, override_final=True)
            student.final = unicode(override_grade.get_grade())
            student.final_override = True  # effects CSS
        except:
            student.final = course.calculate_final_grade(student)
    
    if request.user.is_superuser or request.user.has_perm('schedule.change_own_grade'):
        edit = True
    else:
        edit = False
    
    return render_to_response('schedule/teacher_grade_upload.html', {
        'request': request, 
        'course': course, 
        'marking_periods': marking_periods, 
        'students': students, 
        'import_form': import_form,
        'edit': edit,
        'last_y': last_y,
        'last_x': last_x,
    }, RequestContext(request, {}),)

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


@user_passes_test(lambda u: u.has_perm('sis.reports'), login_url='/')
def grade_analytics(request):
    form = GradeFilterForm()
    if request.method == 'POST':
        if 'bulk' in request.POST:
            selected = request.POST.getlist('selected')
            queryset = Student.objects.filter(id__in=selected)
            return redirect_to(request, url = '/admin/sis/%s-masschange/%s' % ('student', ','.join(selected)))
            
        form = GradeFilterForm(request.POST)
        if form.is_valid():
            # Add to course
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
            if data['currently_in_asp']:
                students = students.filter(courseenrollment__course__asp=True)
            if data['in_individual_education_program']:
                students = students.filter(individual_education_program=True)
            
            courses = Course.objects.filter(courseenrollment__user__in=students, graded=True)
            if data['this_year']:
                courses = courses.filter(marking_period__school_year=SchoolYear.objects.get(active_year=True))
            elif not data['all_years']:
                courses = courses.filter(
                    marking_period__start_date_gte=data['date_begin'],
                    marking_period__end_date_lte=date['date_end'],
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
            
            #Figure out dates
            if data['date_begin'] and date['date_end']:
                date_begin = data['date_begin']
                date_end = date['date_end']
            elif data['marking_period']:
                mps = data['marking_period'].order_by('-end_date')
                date_begin = mps.reverse()[0].start_date
                date_end = mps[0].end_date
            elif data['this_year']:
                year = SchoolYear.objects.get(active_year=True)
                date_begin = year.start_date
                date_end = year.end_date
            else: # all of time
                date_begin = date(1980, 1, 1)
                date_end = date(2980, 1, 1)
            print date_begin
            # Pre load Discipline data
            if data['filter_disc_action'] and data['filter_disc'] and data['filter_disc_times']:
                student_disciplines = students.filter(studentdiscipline__date__range=(date_begin, date_end), studentdiscipline__action=data['filter_disc_action']).annotate(action_count=Count('studentdiscipline__action'))
            # Pre load Attendance data
            if data['filter_attn'] and data['filter_attn_times']:
                student_attendances = students.filter(student_attn__date__range=(date_begin, date_end), student_attn__status__absent=True).annotate(attn_count=Count('student_attn'))
                
            for student in students:
                # if this is a report, only calculate for selected students.
                if not 'xls' in request.POST or "selected" in request.POST:
                    num_matched = 0
                    add_to_list = True # If all criteria is met, add student to list
                    match_all = True
                    student.courses = []
                    i_courses = 0
                    
                    # For ASP
                    student.departments = []
                    for dept in Department.objects.all():
                        student.departments.append("")
                    
                    # for each grade for this student
                    course = None
                    done = False
                    grades_text = ""
                    if data['final']:
                        for course in student.course_set.filter(id__in=courses):
                            grade = course.get_final_grade(student)
                            if grade:
                                match = check_if_match(grade, data['filter'], data['grade'])
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
                    if data['each_marking_period'] or data['mid_mark']:
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
                                
                                if data['each_marking_period'] and grade.final == True and grade.override_final == False:
                                    grade_value = grade.get_grade()
                                    match = check_if_match(grade_value, data['filter'], data['grade'])
                                    if match:
                                        grades_text += str(grade.marking_period.shortname) + ':' + str(grade_value) + " "
                                        num_matched += 1
                                    else:
                                        match_all = False
                                if data['mid_mark'] and grade.final == False and grade.override_final == False:
                                    grade_value = grade.get_grade()
                                    match = check_if_match(grade_value, data['filter'], data['grade'])
                                    if match:
                                        grades_text += str(grade.marking_period.shortname) + str(grade.course) + '(mid):' + str(grade_value) + " "
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
                    if data['filter_times'] == "*" or data['filter_times'] == None:
                        if not match_all:
                            add_to_list = False
                    elif not num_matched >= int(data['filter_times']):
                        add_to_list = False
                    
                    # Check discipline
                    if data['filter_disc_action'] and data['filter_disc'] and data['filter_disc_times']:
                        try:
                            student.action_count = student_disciplines.get(id=student.id).action_count
                        except:
                            student.action_count = 0
                        if ((data['filter_disc'] == "lt" and not student.action_count < int(data['filter_disc_times'])) or 
                            (data['filter_disc'] == "lte" and not student.action_count <= int(data['filter_disc_times'])) or 
                            (data['filter_disc'] == "gt" and not student.action_count > int(data['filter_disc_times'])) or 
                            (data['filter_disc'] == "gte" and not student.action_count >= int(data['filter_disc_times']))
                        ):
                            add_to_list = False
                        else:
                            student.courses.append('%s: %s' % (data['filter_disc_action'], student.action_count))
                    
                    # Check Attendance
                    if data['filter_attn'] and data['filter_attn_times']:
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
                        
                        # add dept data for asp
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
                
            return render_to_response('schedule/grade_analytics.html', {'form': form, 'course_selection': course_selection, 'students': show_students,}, RequestContext(request, {}),)
    return render_to_response('schedule/grade_analytics.html', {'form': form,}, RequestContext(request, {}),)
