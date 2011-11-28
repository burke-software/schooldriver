#   Copyright 2011 Burke Software and Consulting LLC
#   Author Callista Goss <calli@burkesoftware.com>
#   Author David Burke <david@burkesoftware.com>
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

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.forms import ValidationError

from datetime import datetime, date

from ecwsp.volunteer_track.models import *
from ecwsp.volunteer_track.forms import *
from ecwsp.sis.models import Student

#staff: has_perm instead of filter
@user_passes_test(lambda u: u.groups.filter(name='students').count() > 0, login_url='/')    
def student_hours(request):
    try:
        student = Student.objects.get(username=request.user.username)
        volunteer = Volunteer.objects.get(student=student)
    except:
        return render_to_response('base.html', {'msg': "Student is not set as a volunteer. Please notify a system admin if you believe this is a mistake."}, RequestContext(request, {}))
    
    if volunteer.site_approval != "Accepted":
        return render_to_response('volunteer_track/dash.html', {'student': volunteer, 'msg': "Your site must be approved before you may submit hours."}, RequestContext(request, {}))
    
    VolFormSet = modelformset_factory(Hours, inputTimeForm, extra=3)
    
    formset = VolFormSet(queryset=Hours.objects.filter(student=volunteer))
    if request.method == 'POST':
        formset = VolFormSet(request.POST)
        if formset.is_valid():
            msg = "Volunteer sheet has been successfully submitted. "
            for form in formset:
                hour_model = form.save(commit=False)
                if hour_model.date and hour_model.hours:
                    hour_model.student = volunteer
                    hour_model.site = volunteer.site
                    try:
                        hour_model.full_clean()
                        hour_model.save()
                    except ValidationError, e:
                        msg += " Duplicate date found %s. " % (hour_model.date,)
            return render_to_response('volunteer_track/dash.html', {'student': volunteer, 'msg': msg}, RequestContext(request, {}))

    return render_to_response('volunteer_track/student_volunteer_hours.html', {'student': volunteer, 'form': formset,'hoursReq':volunteer.hours_required,\
                                                                               'hoursComplete':volunteer.hours_completed}, RequestContext(request, {}))
    
    
@user_passes_test(lambda u: u.groups.filter(name='students'), login_url='/')    
def student_site_approval(request):
    """ This view allows a student to choose an existing site or create a new one """
    student = Student.objects.get(username=request.user.username)
    volunteer, created = Volunteer.objects.get_or_create(student=student)
    
    if request.method == 'POST':
        if 'existing_site_submit' in request.POST:
            existing_site_form = ExistingSiteForm(request.POST, instance=volunteer)
            if existing_site_form.is_valid():
                existing_site_form.save()
                volunteer.site_approval = "Submitted"
                volunteer.save()
                return HttpResponseRedirect(reverse(change_supervisor))
                
        elif 'new_site_submit' in request.POST:
            new_site_form = NewSiteForm(request.POST, prefix="new")
            supervisor_form = SupervisorForm(request.POST, prefix="super")
            if new_site_form.is_valid() and supervisor_form.is_valid():
                site = new_site_form.save() 
                supervisor = supervisor_form.save()
                supervisor.site = site
                supervisor.save()
                volunteer.site = site
                volunteer.site_supervisor = supervisor
                volunteer.job_description = new_site_form.cleaned_data['job_description']
                volunteer.site_approval = "Submitted"
                volunteer.save()
                return HttpResponseRedirect(reverse(student_dash))
                
    if not 'existing_site_form' in locals():
        existing_site_form = ExistingSiteForm(instance=volunteer)
    if not 'new_site_form' in locals():
        new_site_form = NewSiteForm(prefix="new")
    if not 'supervisor_form' in locals():
        supervisor_form = SupervisorForm(prefix="super")
        
    return render_to_response('volunteer_track/student_site_approval.html',
                              {'student': volunteer, 'existing_site_form':existing_site_form, 'new_site_form':new_site_form, 'supervisor_form':supervisor_form}, RequestContext(request, {}))


@user_passes_test(lambda u: u.groups.filter(name='students'), login_url='/')    
def student_dash(request):
    student = Student.objects.get(username=request.user.username)
    volunteer, created = Volunteer.objects.get_or_create(student=student)
    
    if not volunteer.site:
        return HttpResponseRedirect(reverse(student_site_approval))
    
    return render_to_response('volunteer_track/dash.html', {'student': volunteer}, RequestContext(request, {}))
    
@user_passes_test(lambda u: u.groups.filter(name='students'), login_url='/')    
def change_supervisor(request):
    student = Student.objects.get(username=request.user.username)
    volunteer, created = Volunteer.objects.get_or_create(student=student)
    
    if request.method == 'POST':
        supervisor_form = SupervisorForm(request.POST)
        select_supervisor_form = SelectSupervisorForm(request.POST)
        if select_supervisor_form.is_valid() and select_supervisor_form.cleaned_data['select_existing']:
            volunteer.site_supervisor = select_supervisor_form.cleaned_data['select_existing']
            volunteer.site_approval = "Submitted"
            volunteer.save()
            return HttpResponseRedirect(reverse(student_dash))
        elif supervisor_form.is_valid():
            supervisor = supervisor_form.save()
            volunteer.site_supervisor = supervisor
            volunteer.site_approval = "Submitted"
            volunteer.save()
            if volunteer.site:
                supervisor.site = volunteer.site
                supervisor.save()
            return HttpResponseRedirect(reverse(student_dash))
    else:
        supervisor_form = SupervisorForm()
        select_supervisor_form = SelectSupervisorForm()
        select_supervisor_form.fields['select_existing'].queryset = volunteer.site.sitesupervisor_set.all()
    
    return render_to_response('volunteer_track/student_change_supervisor.html', {'student': volunteer, 'supervisor_form':supervisor_form, 'select_supervisor_form': select_supervisor_form}, RequestContext(request, {}))
    
def approve(request):
    try:
        volunteer = Volunteer.objects.get(secret_key=request.GET['key'])
    except:
        volunteer = None
    if request.POST and "approve" in request.POST:
        volunteer.hours_record = True
        volunteer.save()
        return render_to_response('base.html', {'msg': 'Volunteer hours approved for %s' % (volunteer,) }, RequestContext(request, {}))
        
    return render_to_response('volunteer_track/approve.html', {'volunteer': volunteer, }, RequestContext(request, {}))