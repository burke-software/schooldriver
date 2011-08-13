#   Copyright 2011 David M Burke
#   Author Callista Goss <calli@burkesoftware.com>
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
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType

from datetime import datetime, date

from ecwsp.volunteer_track.models import *
from ecwsp.volunteer_track.forms import *
from ecwsp.sis.models import Student

#staff: has_perm instead of filter
@user_passes_test(lambda u: u.groups.filter(name='students').count() > 0, login_url='/')    
def student_volunteer(request):
    #if site not approved/no contract/else all goes here.
    #send it StudentName, cohort, siteName, siteSup, hoursReq, hoursComplete <-see work_study.views.py
    
    try:
        student = Student.objects.get(username=request.user.username)
        volunteer = Volunteer.objects.get(student=student)
    except:
        return render_to_response('base.html', {'msg': "Student is not set as a volunteer. Please notify a system admin if you believe this is a mistake."}, RequestContext(request, {}))
    
    
    VolFormSet = modelformset_factory(Hours, inputTimeForm, extra=3)
    formset = VolFormSet(queryset=Hours.objects.filter(student=volunteer))
    if request.method == 'POST':
        formset = VolFormSet(request.POST)
        if formset.is_valid():
            for form in formset.forms:
                instance = form.save(commit=False)
                if instance:
                    if instance.date and instance.hours:
                        instance.student = volunteer
                        instance.timestamp = datetime.now
                        instance.save()
                    else:
                        pass
                else:
                    pass
            return render_to_response('base.html', {'student': True, 'msg': "Volunteer sheet has been successfully submitted."}, RequestContext(request, {}))
    #send it StudentName, cohort, siteName, siteSup, hoursReq, hoursComplete <-see work_study.views.py
    return render_to_response('volunteer_track/student_volunteer_hours.html', {'student': True, 'form': formset, 'studentName': volunteer, 'cohort':volunteer.student.cache_cohort,\
                                                                               'siteName':volunteer.site,'supName':volunteer.site_supervisor,'hoursReq':volunteer.hours_required,\
                                                                               'hoursComplete':volunteer.hours_completed}, RequestContext(request, {}))
    
    
@user_passes_test(lambda u: u.groups.filter(name='students').count() > 0, login_url='/')    
def student_site_approval(request):
    student = Student.objects.get(username=request.user.username)
    volunteer, created = Volunteer.objects.get_or_create(student=student)
    
    job_description = jobDescriptionForm(instance=volunteer)
    required = volunteer.hours_required
    if(volunteer.site_approval=='Accepted'):
        return student_contract(request)
    elif(volunteer.site_approval=='Submitted' or volunteer.site_approval=='Resubmitted') :
        return render_to_response('base.html', {'msg': "You have submitted your site for approval, but it has not been accepted or rejected yet.\
                                                If this is a mistake, contact your volunteer director."}, RequestContext(request, {}))
    elif volunteer.site_approval=='Rejected':
        msg = 'Your last site request was rejected with the following comment: \"' + volunteer.comment + '.\"  Please adjust your request.'
        site_form = siteForm(instance = volunteer)
    else:
        msg = ''
        site_form = siteForm()
    if request.method == 'POST':
        site_form = siteForm(request.POST)
        print site_form.query
        job_description = jobDescriptionForm(request.POST, instance=volunteer)
        if site_form.is_valid():
            if job_description.is_valid():
                print job_description.job_description
                if volunteer.site_approval=='Rejected':
                    volunteer.site_approval = 'Resubmitted'
                else:
                    volunteer.site_approval = 'Submitted'
                    volunteer.save()
                    site_form.save()
                    job_description.save()
                    return render_to_response('base.html', {'student': True, 'msg': "Site request was successfully submitted."}, RequestContext(request, {}))
    return render_to_response('volunteer_track/student_site_approval.html', {'site_form':site_form, 'job_desc':job_description,'hoursReq':required, 'redo':msg,\
                                                                                 'studentName':volunteer, 'cohort':volunteer.student.cache_cohort,}, RequestContext(request, {}))

@user_passes_test(lambda u: u.groups.filter(name='students').count() > 0, login_url='/')
def student_contract(request):
    try:
        student = Student.objects.get(username=request.user.username)
        volunteer = Volunteer.objects.get(student=student)
    except:
        return render_to_response('base.html', {'msg': "Student is not set as a volunteer. Please notify a system admin if you believe this is a mistake."}, RequestContext(request, {}))
    if(volunteer.contract):
        return student_volunteer(request)
    else:
        return render_to_response('base.html', {'msg': "site approval"}, RequestContext(request, {}))