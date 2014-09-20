from django.shortcuts import render_to_response, get_object_or_404
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext

from constance import config
from ecwsp.sis.models import Student, Faculty, Cohort, SchoolYear
from ecwsp.schedule.models import Department, MarkingPeriod, Course, CourseSection

import os
import tempfile
import zipfile
from cStringIO import StringIO

from django.utils.encoding import smart_str
import requests

def setup(request):
    if request.POST:
        if 'download' in request.POST:
            cs = CanvasSync()
            return cs.run_sync()

    return render_to_response('canvas_sync/setup.html', {
        'msg':'',
    }, RequestContext(request, {}),)

class CanvasSync:
    token = config.CANVAS_TOKEN
    account_id = config.CANVAS_ACCOUNT_ID
    base_url = config.CANVAS_BASE_URL

    def run_sync(self):
        #buf = StringIO()
        response = HttpResponse(mimetype="application/zip")
        response['Content-Disposition'] = 'attachment; filename="%s"' % 'canvas_import_files.zip'
        zip_file = zipfile.ZipFile(response, mode='w')
        zip_file.writestr('users.csv', smart_str(self.gen_users()))
        zip_file.writestr('accounts.csv', smart_str(self.gen_accounts()))
        zip_file.writestr('terms.csv', smart_str(self.gen_terms()))
        zip_file.writestr('courses.csv', smart_str(self.gen_courses()))
        zip_file.writestr('sections.csv', smart_str(self.gen_sections()))
        zip_file.writestr('enrollments.csv', smart_str(self.gen_enrollments()))
        zip_file.writestr('groups.csv', smart_str(self.gen_groups()))
        zip_file.writestr('groups_membership.csv', smart_str(self.gen_groups_membership()))
        zip_file.close()

        return response

        temp_file = tempfile.TemporaryFile()
        temp_file.write(buf.getvalue())

        if False:
            params = {'access_token':self.token, 'extention':'zip'}
            #files = {'attachment': ('import.zip', temp_file)}
            files = {'attachment': ('import.zip', open('foo.zip','rb'))}
            response = requests.post(url,params=params,files=files)
            temp_file.close()

        return response
            #output = open('foo.zip', 'wb')
            #output.write(buf.getvalue())
            #output.close()

        buf.close()

    def gen_users(self):
        """ Create csv string for all users both students and faculty
        """
        users_str = u"user_id,login_id,password,first_name,last_name,email,status\n"
        students = Student.objects.all()
        for student in students:
            line = u'"%s","%s","%s","%s","%s","%s",' % (
                student.id,
                student.username,
                '',
                student.first_name,
                student.last_name,
                student.get_email,
            )
            if student.is_active:
                line += u'"active"'
            else:
                line += u'"deleted"'
            users_str += line + u'\n'
        for faculty in Faculty.objects.all():
            if faculty.username:
                line = u'"%s","%s","%s","%s","%s","%s",' % (
                    faculty.id,
                    faculty.username,
                    '',
                    faculty.first_name,
                    faculty.last_name,
                    faculty.email,
                )
                if not faculty.is_active:
                    line += u'"deleted"'
                else:
                    line += u'"active"'
                users_str += line + u'\n'
        return users_str

    def gen_accounts(self):
        """ Create csv string for all departments for Canvas accounts
        """
        result = u"account_id,parent_account_id,name,status\n"
        for department in Department.objects.all():
            line = u'"%s","%s","%s","%s"' % (
                department.id,
                '',
                department.name,
                'active',
            )
            result += line + u'\n'
        return result

    def gen_terms(self, year_is_term=True):
        """ Create csv string for marking periods for Canvas terms
        year_is_term is true then a SWoRD year will be a Canvas term
        """
        result = u"term_id,name,status,start_date,end_date\n"
        if year_is_term:
            for year in SchoolYear.objects.filter(active_year=True):
                line = u'"%s","%s","%s","%s","%s"' % (
                    year.id,
                    year.name,
                    'active',
                    year.start_date.strftime('%Y-%m-%d'),
                    year.end_date.strftime('%Y-%m-%d'),
                )
                result += line + u'\n'
        else:
            for marking_period in MarkingPeriod.objects.all():
                line = u'"%s","%s","%s","%s","%s"' % (
                    marking_period.id,
                    marking_period.name,
                    '',
                    marking_period.start_date.strftime('%Y-%m-%d'),
                    marking_period.end_date.strftime('%Y-%m-%d'),
                )
                result += line + u'\n'
        return result

    def gen_courses(self):
        """ Create csv string for courses
        """
        result = u"course_id,short_name,long_name,account_id,term_id,status,start_date,end_date\n"
        for course in Course.objects.filter(is_active=True).distinct():
            if course.department:
                department_id = course.department_id
            else:
                department_id = ""
            try:
                term_id = MarkingPeriod.objects.filter(coursesection__course=course).first().school_year_id
                start_date = course.start_date.strftime('%Y-%m-%d')
                end_date = course.end_date.strftime('%Y-%m-%d')
            except AttributeError:
                term_id = ""
                start_date = ""
                end_date = ""
            line = u'"%s","%s","%s","%s","%s","%s","%s","%s"' % (
                course.id,
                course.shortname,
                course.fullname,
                department_id,
                term_id,
                'active',
                start_date,
                end_date,
            )
            result += line + u'\n'
        return result

    def gen_sections(self):
        result = 'section_id,course_id,name,status,start_date,end_date'
        for section in CourseSection.objects.filter(marking_period__school_year__active_year=True).distinct():
            line = '{},{},{},{},{},{}'.format(
                    section.id,
                    section.course_id,
                    section.name,
                    'active',
                    section.marking_period.order_by('start_date')[0].start_date.strftime('%Y-%m-%d'),
                    section.marking_period.order_by('-end_date')[0].end_date.strftime('%Y-%m-%d'),
                    )
            result += line + '\n'
        return result

    def gen_enrollments(self):
        """ Create csv string for enrollment
        """
        result = u"course_id,user_id,role,status\n"
        for course_section in CourseSection.objects.filter(marking_period__school_year__active_year=True).distinct():
            for enrollment in course_section.enrollments.filter(is_active=True):
                line = u'"%s","%s","%s","%s"' % (
                    course_section.id,
                    enrollment.id,
                    'student',
                    'active',
                )
                result += line + u'\n'
            for teacher in course_section.teachers.all():
                line = u'"%s","%s","%s","%s"' % (
                    course_section.id,
                    teacher.id,
                    'teacher',
                    'active',
                )
                result += line + u'\n'
        return result

    def gen_groups(self):
        """ Create a csv string for groups from cohorts
        """
        result = "group_id,name,status\n"
        for cohort in Cohort.objects.all():
            if cohort.students.count():
                line = u'"%s","%s","%s"' % (
                    cohort.id,
                    cohort.name,
                    'available',
                )
                result += line + u'\n'
        return result

    def gen_groups_membership(self):
        """ Create a csv string for group memberships
        """
        result = "group_id,user_id,status\n"
        for cohort in Cohort.objects.all():
            for cohort_student in cohort.students.all():
                line = u'"%s","%s","%s"' % (
                    cohort.id,
                    cohort_student.id,
                    'accepted',
                )
                result += line + u'\n'
        return result

