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
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.utils.decorators import method_decorator

from ecwsp.administration.models import Configuration, Template
from ecwsp.schedule.models import Course, CourseSection, MarkingPeriod
from ecwsp.schedule.forms import EngradeSyncForm
from ecwsp.sis.models import Student, UserPreference, Faculty, SchoolYear
from ecwsp.sis.helper_functions import Struct
from ecwsp.sis.uno_report import replace_spreadsheet
from .models import GradeComment, Grade
from .forms import GradeUpload
from constance import config

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
        allow_spreadsheet = False
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
    teacher = Faculty.objects.filter(username=request.user.username).first()
    all_sections = None
    if request.user.has_perm('grades.change_grade'):
        all_sections = CourseSection.objects.filter(
                course__graded=True,
                marking_period__school_year__active_year=True,
            ).order_by('coursesectionteacher__teacher__last_name').distinct()
    elif not teacher:
        messages.info(request, 'You do not have any course sections.')
        return HttpResponseRedirect(reverse('admin:index'))
    course_sections = CourseSection.objects.filter(
            course__graded=True,
            marking_period__school_year__active_year=True,
        ).filter(teachers=teacher).distinct()
    pref = UserPreference.objects.get_or_create(user=request.user)[0].gradebook_preference

    if "ecwsp.engrade_sync" in settings.INSTALLED_APPS:
        if request.method == 'POST':
            form = EngradeSyncForm(request.POST)
            if form.is_valid():
                try:
                    from ecwsp.engrade_sync.engrade_sync import EngradeSync
                    marking_period = form.cleaned_data['marking_period']
                    include_comments = form.cleaned_data['include_comments']
                    course_sections = course_sections.filter(marking_period=marking_period)
                    es = EngradeSync()
                    errors = ""
                    for course_section in course_sections:
                        errors += es.sync_course_grades(course_section, marking_period, include_comments)
                    if errors:
                        messages.success(request, 'Engrade Sync attempted, but has some issues: ' + errors)
                    else:
                        messages.success(request, 'Engrade Sync successful. Please verify each course section!')
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
        {'request': request, 'all_sections': all_sections, 'course_sections': course_sections, 'form': form, 'pref': pref},
        RequestContext(request, {}),
        )


@permission_required('grades.change_grade')
def teacher_grade_submissions(request):
    teachers = Faculty.objects.filter(
        teacher=True,
        coursesection__marking_period__school_year__active_year=True,
        ).distinct()
    try:
        marking_period = MarkingPeriod.objects.filter(active=True).order_by('-end_date')[0]
    except:
        marking_period = None
    course_sections = CourseSection.objects.filter(marking_period=marking_period)

    for teacher in teachers:
        teacher.course_sections = course_sections.filter(coursesectionteacher=teacher)

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


class StudentGradesheet(DetailView):
    model = Student
    template_name = "grades/student_grades.html"

    @method_decorator(permission_required('grades.change_grade'))
    def dispatch(self, *args, **kwargs):
        return super(StudentGradesheet, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StudentGradesheet, self).get_context_data(**kwargs)
        context['letter_grade_required_for_pass'] = config.LETTER_GRADE_REQUIRED_FOR_PASS
        context['school_years'] = SchoolYear.objects.filter(markingperiod__coursesection__enrollments=self.object).distinct()
        context['default_school_year'] = context['school_years'].first()
        return context


class CourseSectionGrades(FormMixin, DetailView):
    """ This view is for inputing grades. It supports manual entry or uploading a spreadsheet """
    model = CourseSection
    template_name = "grades/course_grades.html"
    form_class = GradeUpload

    def get_success_url(self):
        return reverse('course-section-grades', kwargs={'pk': self.object.pk})

    @method_decorator(user_passes_test(lambda u: u.has_perm('schedule.change_grade') or u.has_perm('grades.change_own_grade')))
    def dispatch(self, *args, **kwargs):
        return super(CourseSectionGrades, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CourseSectionGrades, self).get_context_data(**kwargs)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.fields['marking_period'].queryset = form.fields['marking_period'].queryset.filter(coursesection=context['coursesection'])
        context['form'] = form
        if self.request.user.is_superuser or \
            self.request.user.has_perm('grades.change_own_final_grade') or \
            self.request.user.has_perm('grades.change_grade'):
            context['edit_final'] = True
        else:
            context['edit_final'] = False
        if self.request.user.is_superuser or \
            self.request.user.has_perm('grades.change_own_grade') or \
            self.request.user.has_perm('grades.change_grade'):
            context['edit'] = True
        else:
            context['edit'] = False
        context['letter_grade_required_for_pass'] = config.LETTER_GRADE_REQUIRED_FOR_PASS
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        from ecwsp.sis.importer import Importer
        course_section = self.object
        importer = Importer(self.request.FILES['file'], self.request.user)
        error = importer.import_grades(course_section, form.cleaned_data['marking_period'])
        if error:
            messages.warning(self.request, error)
        else:
            course_section.last_grade_submission = datetime.datetime.now()
            course_section.save()
        return super(CourseSectionGrades, self).form_valid(form)


@user_passes_test(lambda u: u.has_perm('schedule.change_grade') or u.has_perm('grades.change_own_grade'))
def teacher_grade_download(request, id, type=None):
    """ Download grading spreadsheet of requested class
    id: course section id
    type: filetype (ods or xls)"""
    if not type:
        profile = UserPreference.objects.get_or_create(user=request.user)[0]
        type = profile.get_format(type="spreadsheet")
    course_section = CourseSection.objects.get(id=id)
    template, created = Template.objects.get_or_create(name="grade spreadsheet")
    filename = unicode(course_section) + "_grade"
    data={}
    data['$students'] = []
    data['$username'] = []

    for student in Student.objects.filter(courseenrollment__course_section=course_section):
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
