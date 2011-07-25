from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import transaction

from ecwsp.sis.models import *
from ecwsp.sis.importer import *
from ecwsp.admissions.reports import *
from ecwsp.admissions.models import *
from ecwsp.admissions.forms import *
from ecwsp.administration.models import Configuration

@user_passes_test(lambda u: u.has_perm("admissions.view_applicant"), login_url='/')   
def reports(request):
    report_form = ReportForm()
    if request.POST:
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            year = report_form.cleaned_data['school_year']
            if 'applicants_to_students' in request.POST:
                return HttpResponseRedirect(reverse(applicants_to_students, args=[year.id]))
            return report_process_statistics(year)
    
    return render_to_response('admissions/report.html', {
            'report_form': report_form,
        },
        RequestContext(request, {}),
    ) 

@transaction.commit_on_success
@user_passes_test(lambda u: u.has_perm("sis.change_student") and u.has_perm("admissions.change_applicant"), login_url='/')   
def applicants_to_students(request, year_id):
    """ Copies all applicants marked as ready for export to sis students
    Does not create copies. Once student is in sis he/she cannot be updated
    from applicant data."""
    imp = Importer()
    school_year = SchoolYear.objects.get(id=year_id)
    msg = ""
    if request.POST:
        imp = Importer()
        applicants = Applicant.objects.filter(ready_for_export=True, sis_student=None, school_year=school_year)
        for appl in applicants:
            student = Student(
                fname=appl.fname,
                mname=appl.mname,
                lname=appl.lname,
                sex=appl.sex,
                ssn=appl.ssn,
                bday=appl.bday,
                unique_id=appl.unique_id,
                email=appl.email,
                year=appl.year,
            )
            if not student.username:
                student.username = imp.gen_username(student.fname, student.lname)
            student.save()
            
            add_worker = Configuration.get_or_default("Admissions to student also makes student worker", "False")
            if add_worker.value == "True":
                student.promote_to_worker()
            
            appl.sis_student = student
            appl.save()
            for sib in appl.siblings.all():
                student.siblings.add()
            for par in appl.parent_guardians.all():
                student.emergency_contacts.add(par)
            
            student.save()
            msg += "Imported <a href='/admin/sis/student/%s'>%s</a>, %s<br/>" % (student.id, student, student.username)
        msg += "<br/>Maybe you want to save this list to add students to Active Dictory or Google Apps?<br/><br/>"
    
    num = Applicant.objects.filter(ready_for_export=True, sis_student=None, school_year=school_year).count()
    msg += "There are currently %s applicants marked as ready for export. This is not a reversable process! Note usernames will be generated, you may change them later.<br/>" % str(num)
    return render_to_response('admissions/applicants_to_students.html',
                              {'msg': msg},
                              RequestContext(request, {}),) 