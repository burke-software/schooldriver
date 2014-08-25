from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from ecwsp.administration.models import *
from ecwsp.sis.models import UserPreference, SchoolYear, Student
from ecwsp.sis.xl_report import XlReport
from models import *
from forms import *
import datetime

class BaseDisciplineFormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        super(BaseDisciplineFormSet, self).add_fields(form, index)
        form.fields["students"] = AutoCompleteSelectMultipleField('dstudent')
        form.fields['comments'].widget = forms.TextInput(attrs={'size':'50'})
        form.fields['date'].widget = adminwidgets.AdminDateWidget()
                

@user_passes_test(lambda u: u.has_perm('discipline.change_studentdiscipline'))   
def enter_discipline(request):
    DisciplineFormSet = modelformset_factory(StudentDiscipline, extra=5, formset=BaseDisciplineFormSet)
    if request.method == 'POST':
        formset = DisciplineFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Discipline records added')
            if 'addmore' in request.POST:
                formset = DisciplineFormSet(queryset=StudentDiscipline.objects.none())
                return render_to_response('discipline/enter_discipline.html', {'request': request, 'formset': formset, 'messages': messages.get_messages(request)})
            else:
                return HttpResponseRedirect(reverse('admin:discipline_studentdiscipline_changelist'))
        else:
            return render_to_response('discipline/enter_discipline.html', {'request': request, 'formset': formset})
    else:
        formset = DisciplineFormSet(queryset=StudentDiscipline.objects.none())
    return render_to_response('discipline/enter_discipline.html', {'request': request, 'formset': formset},
                              RequestContext(request, {}),)


@user_passes_test(lambda u: u.has_perm('discipline.change_studentdiscipline') or u.has_perm('sis.reports'))
def view_discipline(request):
    form = DisciplineViewForm()
    form.back = "/admin/discipline/studentdiscipline/"
    return render_to_response('discipline/view_form.html', {'request': request, 'form': form},
                              RequestContext(request, {}),)


@user_passes_test(lambda u: u.has_perm('discipline.change_studentdiscipline') or u.has_perm('sis.reports'))
def discipline_report(request, student_id):
    """Generate a complete report of a student's discipline history
    """
    from ecwsp.sis.template_report import TemplateReport
    template, created = Template.objects.get_or_create(name="Discipline Report")
    template = template.get_template_path(request)
    report = TemplateReport(request.user)
    report.filename = 'disc_report'
    
    student = Student.objects.get(id=student_id)
    disc = StudentDiscipline.objects.filter(students=student)
    
    report.data['disciplines'] = disc
    report.data['school_year'] = SchoolYear.objects.get(active_year=True)
    report.data['student'] = student
    report.data['student_year'] = student.year
    
    return report.pod_save(template)
    

@user_passes_test(lambda u: u.has_perm('discipline.change_studentdiscipline') or u.has_perm('sis.reports'))   
def discipline_list(request, type="doc", start_date=False, end_date=False):
    template = Template.objects.get_or_create(name="Discipline Daily List")[0].get_template_path(request)
    if not template:
        return HttpResponseRedirect(reverse('admin:index'))
    
    data={}
    if start_date:
        discs = StudentDiscipline.objects.filter(date__range=(start_date, end_date))
    else:
        discs = StudentDiscipline.objects.filter(date=date.today())
    
    data['disciplines'] = []
    for disc in discs:
        for student in disc.students.all():
            data['disciplines'].append(student)
    
    return pod_report(template, data, "Discipline List")

@permission_required('discipline.change_studentdiscipline')
def generate_from_attendance(request):
    """
    Generate a list of students who meet various attendance requirements and thus
    should be given a discipline
    """
    tardies_before_disc = Configuration.get_or_default("attendance_disc_tardies_before_disc", "1").value
    conf_infraction = Configuration.get_or_default("attendance_disc_infraction", "").value
    conf_action = Configuration.get_or_default("attendance_disc_action", "").value
    
    if request.POST:
        students = Student.objects.filter(id__in=request.POST.keys())
        i=0
        for student in students:
            disc = StudentDiscipline(
                infraction=Infraction.objects.get(comment=conf_infraction),
            )
            disc.save()
            disc.students.add(student)
            action_instance = DisciplineActionInstance(
                action_id=DisciplineAction.objects.get(name=conf_action).id,
                student_discipline_id=disc.id,
            )
            action_instance.save()
            i += 1
        messages.success(request,'Created %s new record(s)' % (i,))
        return HttpResponseRedirect(reverse('admin:discipline_studentdiscipline_changelist'))
    
    year = SchoolYear.objects.get(active_year=True)
    
    students = []
    for student in Student.objects.filter(
        student_attn__date=datetime.date.today(),
        student_attn__status__tardy=True,
        student_attn__status__excused=False
        ):
        if (student.student_attn.filter(
                status__tardy=True,
                status__excused=False,
                date__range=(year.start_date,year.end_date)
            ).count() >= int(tardies_before_disc) and
            not StudentDiscipline.objects.filter(
                students=student,date=datetime.date.today()
            ).count()
            ):
            student.tardies = student.student_attn.filter(
                status__tardy=True,
                status__excused=False,
                date__range=(year.start_date,year.end_date)
            )
            students.append(student)
            
            
    return render_to_response('discipline/generate_from_attendance.html', {
        'request': request,
        'students': students,
        'tardies_before_disc': tardies_before_disc,
        'conf_infraction': conf_infraction,
        'conf_action': conf_action,
        },RequestContext(request, {}),)

@user_passes_test(lambda u: u.has_perm('discipline.change_studentdiscipline') or u.has_perm('sis.reports'))
def discipline_report_view(request):
    form = DisciplineStudentStatistics()
    merit_form = MeritForm()
    if request.method == 'POST':
        if 'merit' in request.POST:
            merit_form = MeritForm(request.POST)
            if merit_form.is_valid():
                from ecwsp.sis.template_report import TemplateReport
                report = TemplateReport(request.user)
                report.filename = 'Merit Handouts'
                l1 = merit_form.cleaned_data['level_one']
                l2 = merit_form.cleaned_data['level_two']
                l3 = merit_form.cleaned_data['level_three']
                l4 = merit_form.cleaned_data['level_four']
                start_date = merit_form.cleaned_data['start_date']
                end_date = merit_form.cleaned_data['end_date']
                
                students = Student.objects.filter(is_active=True)
                if merit_form.cleaned_data['sort_by'] == 'year':
                    students = students.order_by('year')
                elif merit_form.cleaned_data['sort_by'] == 'cohort':
                    students = students.order_by('cache_cohort')
                disciplines = StudentDiscipline.objects.filter(date__range=(start_date, end_date)).values('students').annotate(Count('pk'))
                for student in students:
                    disc = 0
                    for discipline in disciplines:
                        if discipline['students'] == student.id:
                            disc = discipline['pk__count']
                            break
                    student.disc_count = disc
                    if student.disc_count <= l1:
                        student.merit_level = 1
                    elif student.disc_count <= l2:
                        student.merit_level = 2
                    elif student.disc_count <= l3:
                        student.merit_level = 3
                    elif student.disc_count <= l4:
                        student.merit_level = 4
                report.data['students'] = students
                template = Template.objects.get_or_create(name="Merit Level Handout")[0]
                template = template.get_template_path(request)
                if template:
                    return report.pod_save(template)
        else:
            form = DisciplineStudentStatistics(request.POST)
            if form.is_valid():
                data = []
                start, end = form.get_dates()
                if 'student' in request.POST:
                    students = Student.objects.all()
                    school_year = SchoolYear.objects.get(active_year=True)
                    if form.cleaned_data['date_begin']:
                        if SchoolYear.objects.filter(end_date__gte=form.cleaned_data['date_begin']):
                            school_year = SchoolYear.objects.filter(end_date__gte=form.cleaned_data['date_begin']).order_by('start_date')[0]
                            # students belonging to this school year
                            students = students.filter(coursesection__marking_period__school_year__exact=school_year).distinct()
                    if not form.cleaned_data['include_deleted'] :
                        students = students.exclude(is_active=False)
                    if form.cleaned_data['order_by'] == "Year":
                        students = students.order_by('year')
                    subtitles = ["Student",]
                    titles = ["","Infractions",]
                    for infr in Infraction.objects.all():
                        titles.append("")
                    titles.pop()
                    titles.append("Actions")
                    for infr in Infraction.objects.all():
                        subtitles.append(unicode(infr))
                    for action in DisciplineAction.objects.all():
                        subtitles.append(unicode(action))
                        titles.append("")
                    titles.pop()
                    data.append(subtitles)
                    
                    pref = UserPreference.objects.get_or_create(user=request.user)[0]
                    for student in students:
                        disciplines = student.studentdiscipline_set.all()
                        disciplines = disciplines.filter(date__range=(start, end))
                        stats = [unicode(student),]
                        
                        add = True
                        for infr in Infraction.objects.all():
                            number = disciplines.filter(infraction=infr, students=student).count()
                            stats.append(number)
                            # check for filter
                            if form.cleaned_data['infraction'] == infr:
                                infraction_discipline = disciplines.filter(infraction=form.cleaned_data['infraction'])
                                if number < form.cleaned_data['minimum_infraction']:
                                    add = False
                        for action in DisciplineAction.objects.all():
                            actions = disciplines.filter(disciplineactioninstance__action=action, students=student).count()
                            stats.append(actions)
                            # check for filter
                            if form.cleaned_data['action'] == action:
                                if actions < form.cleaned_data['minimum_action']:
                                    add = False
                             
                        if add: data.append(stats)
                    
                    report = XlReport(file_name="disc_stats")
                    report.add_sheet(data, header_row=titles, title="Discipline Stats", heading="Discipline Stats")
                    
                    # By Teacher
                    data = []
                    titles = ['teacher']
                    for action in DisciplineAction.objects.all():
                        titles.append(action)
                    
                    teachers = Faculty.objects.filter(studentdiscipline__isnull=False).distinct()
                    disciplines = StudentDiscipline.objects.filter(date__range=(start, end))
                    
                    for teacher in teachers:
                        row = [teacher]
                        for action in DisciplineAction.objects.all():
                            row.append(disciplines.filter(teacher=teacher, action=action).count())
                        data.append(row)
                    
                    report.add_sheet(data, header_row=titles, heading="By Teachers")
                    return report.as_download()
                    
                elif 'aggr' in request.POST:
                    disciplines = StudentDiscipline.objects.filter(date__range=(start, end))
                    if form.cleaned_data['this_year']:
                        school_start = SchoolYear.objects.get(active_year=True).start_date
                        school_end = SchoolYear.objects.get(active_year=True).end_date
                        disciplines = disciplines.filter(date__range=(school_start, school_end))
                    elif not form.cleaned_data['this_year'] and not form.cleaned_data['all_years']:
                        disciplines = disciplines.filter(date__range=(form.cleaned_data['date_begin'], form.cleaned_data['date_end']))
                    
                    stats = []
                    titles = []
                    for infr in Infraction.objects.all():
                        titles.append(infr)
                        number = disciplines.filter(infraction=infr).count()
                        stats.append(number)
                    
                    for action in DisciplineAction.objects.all():
                        titles.append(action)
                        number = 0
                        for a in DisciplineActionInstance.objects.filter(action=action):
                            number += a.quantity
                        stats.append(number)
                        
                    data.append(stats)
                    report = XlReport(file_name="disc_stats")
                    report.add_sheet(data, header_row=titles, title="Discipline Stats", heading="Discipline Stats")
                    return report.as_download()
            else:
                return render_to_response('discipline/disc_report.html', {'request': request, 'form': form},
                                          RequestContext(request, {}),)    
    return render_to_response('discipline/disc_report.html', {'request': request, 'form': form, 'merit_form':merit_form,},
                              RequestContext(request, {}),)
