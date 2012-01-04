#   Copyright 2011 David M Burke
#   Author David M Burke <david@burkesoftware.com>
#   
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
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
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.core.urlresolvers import reverse
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from ecwsp.administration.models import *
from ecwsp.sis.models import UserPreference, SchoolYear
from ecwsp.sis.xlsReport import *
from models import *
from forms import *

class BaseDisciplineFormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        super(BaseDisciplineFormSet, self).add_fields(form, index)
        form.fields["students"] = AutoCompleteSelectMultipleField('dstudent')
        form.fields['comments'].widget = forms.TextInput(attrs={'size':'50'})
        form.fields['date'].widget = adminwidgets.AdminDateWidget()
                

@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/')    
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


@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/') 
def view_discipline(request):
    form = DisciplineViewForm()
    form.back = "/admin/discipline/studentdiscipline/"
    return render_to_response('discipline/view_form.html', {'request': request, 'form': form},
                              RequestContext(request, {}),)


@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/') 
def discipline_report(request, student_id):
    """Generate a complete report of a student's discipline history
    """
    template, created = Template.objects.get_or_create(name="Discipline Report")
    
    school_name, created = Configuration.objects.get_or_create(name="School Name")
    school_name = school_name.value
    
    student = Student.objects.get(id=student_id)
    disc = StudentDiscipline.objects.filter(students=student)
    
    data = get_default_data()
    data['disciplines'] = disc
    data['school_year'] = SchoolYear.objects.get(active_year=True)
    data['student'] = student
    data['student_year'] = student.year
    
    template_path = template.get_template_path(request)
    if not template_path:
        return HttpResponseRedirect(reverse('admin:index')) 
    
    return pod_save("disc_report", ".odt", data, template_path)
    

@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/')    
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


@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/')    
def discipline_report_view(request):
    if request.method == 'POST':
        form = DisciplineStudentStatistics(request.POST)
        honor_form = HonorForm(request.POST)
        if form.is_valid():
            data = []
            start, end = form.get_dates()
            if 'student' in request.POST:
                students = Student.objects.all()
                if not form.cleaned_data['include_deleted'] :
                    students = students.exclude(inactive=True)
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
                         
                    pref.get_additional_student_fields(stats, student, students, titles)
                    if add: data.append(stats)
                
                report = xlsReport(data, titles, "disc_stats.xls", heading="Discipline Stats")
                
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
                
                report.addSheet(data, titles=titles, heading="By Teachers")
                return report.finish()
                
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
                report = xlsReport(data, titles, "disc_stats.xls", heading="Discipline Stats")
                return report.finish()
        else:
            return render_to_response('discipline/disc_report.html', {'request': request, 'form': form},
                                      RequestContext(request, {}),)
            
    else:
        form = DisciplineStudentStatistics()
        honor_form = HonorForm()
    return render_to_response('discipline/disc_report.html', {'request': request, 'form': form, 'honor_form':honor_form,},
                              RequestContext(request, {}),)