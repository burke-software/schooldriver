from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.db.models import Q

from ecwsp.administration.models import Configuration, Template
from ecwsp.schedule.models import Course, MarkingPeriod
from ecwsp.schedule.forms import EngradeSyncForm
from ecwsp.sis.models import Student, UserPreference, Faculty, SchoolYear
from ecwsp.sis.helper_functions import Struct
from ecwsp.sis.uno_report import replace_spreadsheet
from .models import GradeComment, Grade
from .forms import GradeUpload

import datetime
import time
import logging

@login_required
def select_grade_method(request):
    """ Select a per user preferred grading method
    Forward to previously requested page after
    """
    pref = UserPreference.objects.get_or_create(user=request.user)[0]
    if request.POST and 'choice' in request.POST:
        pref.gradebook_preference = request.POST['choice']
        pref.save()
    options = []
    if 'ecwsp.benchmark_grade' in settings.INSTALLED_APPS:
        options += ['O']
    if 'ecwsp.engrade_sync' in settings.INSTALLED_APPS:
        options += ['E']
    allow_spreadsheet = Configuration.get_or_default('grades_allow_spreadsheet_import').value
    if allow_spreadsheet == 'True':
        options += ['S']
    else:
        allow_import = False
    if request.user.has_perm('grades.change_own_grade') or request.user.has_pem('grades.change_grade'):
        options += ['M']
        allow_manual = True
    
    if not pref.gradebook_preference and len(options) == 1:
        pref.gradebook_preference = options[0]
        pref.save()
    
    if pref.gradebook_preference and (not 'override' in request.GET or request.POST):
        if 'next' in request.GET:
            next_page = request.GET['next']
            if next_page == "teacher_grade":
                return redirect('ecwsp.grades.views.teacher_grade')
    
    return render_to_response(
        'grades/select_grade_method.html',
        {'request': request, 'allow_spreadsheet': allow_spreadsheet, 'allow_manual': allow_manual},
        RequestContext(request, {}),)

@permission_required('grades.change_own_grade')
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
    pref = UserPreference.objects.get_or_create(user=request.user)[0].gradebook_preference
    
    if "ecwsp.engrade_sync" in settings.INSTALLED_APPS:
        if request.method == 'POST':
            form = EngradeSyncForm(request.POST)
            if form.is_valid():
                try:
                    from ecwsp.engrade_sync.engrade_sync import EngradeSync
                    marking_period = form.cleaned_data['marking_period']
                    include_comments = form.cleaned_data['include_comments']
                    courses = courses.filter(marking_period=marking_period)
                    es = EngradeSync()
                    errors = ""
                    for course in courses:
                        errors += es.sync_course_grades(course, marking_period, include_comments)
                    if errors:
                        messages.success(request, 'Engrade Sync attempted, but has some issues: ' + errors)
                    else:
                        messages.success(request, 'Engrade Sync successful. Please verify each course!')
                except:
                    messages.info(request, 'Engrade Sync unsuccessful. Contact an administrator.')
                    logging.error('Engrade Sync unsuccessful', exc_info=True, extra={
                        'request': request,
                    })
            else:
                messages.info(request, 'You must select a valid marking period')
        form = EngradeSyncForm()
    else:
        form = None
    return render_to_response(
        'grades/teacher_grade.html',
        {'request': request, 'courses': courses, 'form': form, 'pref': pref},
        RequestContext(request, {}),
        )
    

@permission_required('grades.change_grade')
def teacher_grade_submissions(request):
    teachers = Faculty.objects.filter(
        teacher=True,
        course__marking_period__school_year__active_year=True,
        ).distinct()
    try:
        marking_period = MarkingPeriod.objects.filter(active=True).order_by('-end_date')[0]
    except:
        marking_period = None
    courses = Course.objects.filter(marking_period=marking_period)
    
    for teacher in teachers:
        teacher.courses = courses.filter(teacher=teacher)
    
    return render_to_response(
        'grades/teacher_grade_submissions.html',
        {'teachers':teachers, 'marking_period':marking_period},
        RequestContext(request, {}),)


def view_comment_codes(request):
    comments = GradeComment.objects.all()
    msg = ""
    for comment in comments:
        msg += "%s <br/>" % (comment,)
    return render_to_response('sis/generic_msg.html', {'msg': msg,}, RequestContext(request, {}),)


@user_passes_test(lambda u: u.has_perm('schedule.change_grade') or u.has_perm('grades.change_own_grade'))
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
            from ecwsp.sis.importer import Importer
            importer = Importer(request.FILES['file'], request.user)
            error = importer.import_grades(course, import_form.cleaned_data['marking_period'])
            if error:
                messages.warning(request, error)
            else:
                course.last_grade_submission = datetime.datetime.now()
                course.save()
    else:
        import_form = GradeUpload()
        import_form.fields['marking_period'].queryset = import_form.fields['marking_period'].queryset.filter(course=course)
        
    if request.method == 'POST' and 'edit' in request.POST:
        handle_grade_save(request, course)
    
    marking_periods = course.marking_period.all().order_by('start_date')
    
    # Ensure grades exists
    for mp in marking_periods:
        for student in students:
            grade, created = Grade.objects.get_or_create(student=student, course=course, marking_period=mp)
    
    for student in students:
        student.grades = student.grade_set.filter(course=course, override_final=False)
        try:
            student.final = student.grade_set.get(course=course, override_final=True).get_grade()
            student.final_override = True
        except Grade.DoesNotExist:
            student.final = course.calculate_final_grade(student)
    
    if request.user.is_superuser or \
        request.user.has_perm('grades.change_own_final_grade') or \
        request.user.has_perm('grades.change_grade'):
        edit_final = True
    else:
        edit_final = False
    if request.user.is_superuser or \
        request.user.has_perm('grades.change_own_grade') or \
        request.user.has_perm('grades.change_grade'):
        edit = True
    else:
        edit = False
    
    letter_grade_required_for_pass = Configuration.get_or_default('letter_grade_required_for_pass', '60').value
    
    return render_to_response('grades/teacher_grade_upload.html', {
        'request': request, 
        'course': course, 
        'marking_periods': marking_periods, 
        'students': students, 
        'import_form': import_form,
        'edit': edit,
        'edit_final': edit_final,
        'letter_grade_required_for_pass': letter_grade_required_for_pass
    }, RequestContext(request, {}),)


@user_passes_test(lambda u: u.has_perm('schedule.change_grade') or u.has_perm('grades.change_own_grade'))   
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
    
    if True:
        # Libreoffice crashes sometimes, maybe 5% of the time. So try it some more!
        for x in range(0,3):
            try:
                template_path = template.get_template_path(request)
                if not template_path:
                    return HttpResponseRedirect(reverse('admin:index'))
                return replace_spreadsheet(template_path, filename, data, type)
            except:
                logging.warning('LibreOffice crashed?', exc_info=True, extra={
                    'request': request,
                })
                time.sleep(3)
        return replace_spreadsheet(template_path, filename, data, type)
    # Appy version (too buggy to use)
    #template_path = template.get_template_path(request)
    #if not template_path:
    #    return HttpResponseRedirect(reverse('admin:index'))
    #return replace_spreadsheet(template_path, filename, data, type)
    
    
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
                    LogEntry.objects.log_action(
                        user_id         = request.user.pk, 
                        content_type_id = ContentType.objects.get_for_model(grade).pk,
                        object_id       = grade.pk,
                        object_repr     = unicode(grade), 
                        action_flag     = CHANGE
                    )
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
                    logger.error('Unable to save grade', exc_info=True, extra={
                        'request': request,
                    })
    handle_final_grade_save(request, course=course)
    

def handle_final_grade_save(request, course=None):
    for input, value in request.POST.items():
        input = input.split('_')
        if input[0] in ["gradefinalform","coursefinalform"]:
            try:
                if input[0] == "gradefinalform":
                    student = Student.objects.get(id=input[1])
                elif input[0] == "coursefinalform":
                    course = Course.objects.get(id=input[1])
                    student = Student.objects.get(id=input[2])
                grade = value
                
                if Grade.objects.filter(course=course, override_final=True, student=student).count():
                    grade_object, created = Grade.objects.get_or_create(course=course, override_final=True, student=student)
                    if grade == "" or grade == None or grade == "None":
                        grade_object.delete()
                        LogEntry.objects.log_action(
                            user_id         = request.user.pk, 
                            content_type_id = ContentType.objects.get_for_model(grade_object).pk,
                            object_id       = grade_object.pk,
                            object_repr     = unicode(grade_object),
                            action_flag     = DELETION
                        )
                    else:
                        grade_object.set_grade(grade)
                        grade_object.save()
                        LogEntry.objects.log_action(
                            user_id         = request.user.pk, 
                            content_type_id = ContentType.objects.get_for_model(grade_object).pk,
                            object_id       = grade_object.pk,
                            object_repr     = unicode(grade_object),
                            action_flag     = CHANGE
                        ) 
                else: # final grade doesn't already exists
                    try:
                        Decimal(grade)
                        final = course.calculate_final_grade(student)
                        grade = Decimal(grade).quantize(Decimal("0.01"), ROUND_HALF_UP)
                        if grade != final:
                            grade_object, created = Grade.objects.get_or_create(course=course, override_final=True, student=student)
                            grade_object.set_grade(grade)
                            grade_object.save()
                            LogEntry.objects.log_action(
                                user_id         = request.user.pk, 
                                content_type_id = ContentType.objects.get_for_model(grade_object).pk,
                                object_id       = grade_object.pk,
                                object_repr     = unicode(grade_object), 
                                action_flag     = ADDITION
                            )
                    except: # not number
                        if not grade == "" and not grade == None and not grade == "None":
                            final = course.calculate_final_grade(student)
                            if grade != final:
                                grade_object, created = Grade.objects.get_or_create(course=course, override_final=True, student=student)
                                grade_object.set_grade(grade)
                                grade_object.save()
                                LogEntry.objects.log_action(
                                    user_id         = request.user.pk, 
                                    content_type_id = ContentType.objects.get_for_model(grade_object).pk,
                                    object_id       = grade_object.pk,
                                    object_repr     = unicode(grade_object), 
                                    action_flag     = ADDITION
                                )
            except:
                try:
                    messages.info(request, 'Error in grade for ' + unicode(Student.objects.get(id=input[1])))
                except:
                    try:
                        messages.info(request, 'Error in grade for ' + unicode(Grade.objects.get(id=input[1]).student))
                    except:
                        messages.error(request, 'Unknown error ' + unicode(input))
                        logging.error('Unable to save grade', exc_info=True, extra={
                            'request': request,
                        })
    
@permission_required('grades.change_grade')
def student_gradesheet(request, id, year_id=None):
    student = get_object_or_404(Student, id=id)
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
            grade, created = Grade.objects.get_or_create(student=student, course=course, marking_period=mp)
        course.grades = student.grade_set.filter(course=course, override_final=False)
        
        try:
            override_grade = course.grade_set.get(student=student, override_final=True)
            course.final = unicode(override_grade.get_grade())
            course.final_override = True  # effects CSS
        except:
            course.final = course.calculate_final_grade(student)
    
    marking_periods = MarkingPeriod.objects.filter(course__in=courses).distinct().order_by('start_date')
    
    letter_grade_required_for_pass = Configuration.get_or_default('letter_grade_required_for_pass', '60').value
    
    return render_to_response('grades/student_gradesheet.html', {
        'request': request,
        'student': student,
        'courses': courses,
        'marking_periods': marking_periods,
        'school_year': school_year,
        'school_years': school_years,
        'letter_grade_required_for_pass':letter_grade_required_for_pass,
    }, RequestContext(request, {}),)
