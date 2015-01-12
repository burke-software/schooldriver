from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.utils.decorators import method_decorator
from ecwsp.schedule.models import CourseSection
from ecwsp.sis.models import UserPreference
from ecwsp.administration.models import Template
from .models import GradeComment
from .forms import GradeUpload
from constance import config


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
    

def view_comment_codes(request):
    comments = GradeComment.objects.all()
    msg = ""
    for comment in comments:
        msg += "%s <br/>" % (comment,)
    return render_to_response('sis/generic_msg.html', {'msg': msg,}, RequestContext(request, {}),)

@user_passes_test(lambda u: u.has_perm('schedule.change_grade') or u.has_perm('grades.change_own_grade'))
def teacher_grade_download(request, id, type=None):
    """ Download grading spreadsheet of requested class
    id: course section id
    type: filetype (ods or xls)"""
    if not type:
        profile = UserPreference.objects.get_or_create(user=request.user)[0]
        type = profile.get_format(type="spreadsheet")
    course_section = CourseSection.objects.get(id=id)
    template = Template.objects.get_or_create(name="grade spreadsheet")[0]
    filename = unicode(course_section) + "_grade"
    data = {}
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