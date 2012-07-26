from django.conf import settings

from ecwsp.sis.models import Student, Faculty
from ecwsp.schedule.models import Department, MarkingPeriod

import os
import tempfile
import zipfile
from cStringIO import StringIO

from django.utils.encoding import smart_str
import requests


class CanvasSync:
    token = settings.CANVAS_TOKEN
    account_id = settings.CANVAS_ACCOUNT_ID
    base_url = settings.CANVAS_BASE_URL
    
    def run_sync(self):
        users_str = self.gen_users()
        buf = StringIO()
        zip_file = zipfile.ZipFile(buf, mode='w')
        zip_file.writestr('users.csv', smart_str(users_str))
        zip_file.close()
        
        temp_file = tempfile.TemporaryFile()
        temp_file.write(buf.getvalue())
        
        
        url = self.base_url + '/api/v1/accounts/2/sis_imports'
        params = {'access_token':self.token, 'extention':'zip'}
        #files = {'attachment': ('import.zip', temp_file)}
        files = {'attachment': ('import.zip', open('foo.zip','rb'))}
        response = requests.post(url,params=params,files=files)
        temp_file.close()
        
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
                student.fname,
                student.lname,
                student.email,
            )
            if student.inactive:
                line += u'"deleted"'
            else:
                line += u'"active"'
            users_str += line + u'\n'
        for faculty in Faculty.objects.all():
            if faculty.username:
                line = u'"%s","%s","%s","%s","%s","%s",' % (
                    faculty.id,
                    faculty.username,
                    '',
                    faculty.fname,
                    faculty.lname,
                    faculty.email,
                )
                if faculty.inactive:
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
                '',
            )
            result += line + u'\n'
        return result
    
    def gen_terms(self):
        """ Create csv string for marking periods for Canvas terms
        """
        result = u"term_id,name,status,start_date,end_date\n"
        for marking_period in MarkingPeriod.objects.all():
            line = u'"%s","%s","%s","%s","%s"' % (
                marking_period.id,
                marking_period.name,
                '',
                marking_period.start_date,
                marking_period.end_date,
            )
            result += line + u'\n'
        return result
        
    def gen_courses(self):
        """ Create csv string for courses
        """
        result = u"course_id,short_name,long_name,account_id,term_id,status\n"
        for course in Cou
        
        