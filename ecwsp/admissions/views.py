from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
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

@permission_required('admissions.view_applicant') 
def reports(request):
    report_form = ReportForm()
    if request.POST:
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            year = report_form.cleaned_data['school_year']
            if 'applicants_to_students' in request.POST:
                return HttpResponseRedirect(reverse(applicants_to_students, args=[year[0].id]))
            elif 'funnel' in request.POST:
                year_ids = ''
                for year_item in year.values('id'):
                    year_ids += str(year_item['id']) + ','
                if year_ids:
                    year_ids = year_ids[:-1]
                return HttpResponseRedirect(reverse(funnel) + '?year_ids=%s' % (year_ids))
            return report_process_statistics(year)
    
    return render_to_response('admissions/report.html', {
            'report_form': report_form,
        },
        RequestContext(request, {}),
    )

@permission_required('admissions.view_applicant')
def funnel(request):
    years = SchoolYear.objects.filter(id__in=request.GET['year_ids'].split(','))
    levels = AdmissionLevel.objects.all().order_by('order')
    applicants = Applicant.objects.filter(school_year__in=years).distinct()
    
    level_css_classes = ('one', 'two', 'three', 'four', 'five', 'six',)
    i = 0
    for level in levels:
        try:
            level.css_class = level_css_classes[i]
        except:
            level.css_class = 'six'
        i += 1
    
    i = 0
    running_total = 0
    running_male = 0
    running_female = 0
    for level in reversed(levels): # don't use levels.reverse() it makes a copy not reference!
        running_total += applicants.filter(level=level).count()
        running_male += applicants.filter(level=level, sex='M').count()
        running_female += applicants.filter(level=level, sex='F').count()
        
        level.students = running_total
        level.male = running_male
        try:
            level.male_p = float(level.male) / float(level.students)
        except ZeroDivisionError:
            level.male_p = 0
        level.female = running_female
        try:
            level.female_p = float(level.female) / float(level.students)
        except ZeroDivisionError:
            level.female_p = 0
            
        # Current
        level.c_students = applicants.filter(level=level).count()
        level.c_male = applicants.filter(level=level, sex='M').count()
        try:
            level.c_male_p = float(level.c_male) / float(level.c_students)
        except ZeroDivisionError:
            level.c_male_p = 0
        level.c_female = applicants.filter(level=level, sex='F').count()
        try:
            level.c_female_p = float(level.c_female) / float(level.c_students)
        except ZeroDivisionError:
            level.c_female_p = 0
        
        i += 1
        
        level.decisions = ApplicationDecisionOption.objects.filter(level=level)
        for decision in level.decisions:
            
            decision.students = applicants.filter(level=level,application_decision=decision).count()
            decision.male = applicants.filter(level=level,application_decision=decision,sex='M').count()
            try:
                decision.male_p = float(decision.male) / float(level.students)
            except ZeroDivisionError:
                decision.male_p = 0
            decision.female = applicants.filter(level=level,application_decision=decision,sex='F').count()
            try:
                decision.female_p = float(decision.female) / float(level.students)
            except ZeroDivisionError:
                decision.female_p = 0
            
        
    return render_to_response('admissions/funnel.html', {
            'years': years,
            'levels': levels,
        },
        RequestContext(request, {}),
    )
    

@permission_required('admissions.change_applicant')
def ajax_check_duplicate_applicant(request, fname, lname):
    applicants = Applicant.objects.filter(fname=fname, lname=lname)
    data = ""
    for applicant in applicants:
        data += '<a href="%s" target="_blank">%s %s %s - %s</a><br/>' % (reverse('admin:admissions_applicant_change', args=(applicant.id,)), applicant.fname, applicant.mname, applicant.lname, applicant.bday)
    return HttpResponse(data)


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
                pic=appl.pic,
                family_preferred_language=appl.family_preferred_language,
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
            for contact in student.emergency_contacts.filter(primary_contact=True):
                contact.cache_student_addresses()
            msg += "Imported <a href='/admin/sis/student/%s'>%s</a>, %s<br/>" % (student.id, student, student.username)
        msg += "<br/>Maybe you want to save this list to add students to Active Directory or Google Apps?<br/><br/>"
    
    num = Applicant.objects.filter(ready_for_export=True, sis_student=None, school_year=school_year).count()
    msg += "There are currently %s applicants marked as ready for export. This is not a reversable process! Note usernames will be generated, you may change them later.<br/>" % str(num)
    return render_to_response('admissions/applicants_to_students.html',
                              {'msg': msg},
                              RequestContext(request, {}),) 