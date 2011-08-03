#       tests.py
#       
#       Copyright 2010 Cristo Rey New York High School
#		Author David M Burke <david@burkesoftware.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.


from django.contrib.auth.models import User, Group
import unittest
from django.core import mail
from django.test import TestCase
from django.test.client import Client

from ecwsp.work_study.forms import *
from ecwsp.work_study.models import *
from ecwsp.administration.models import *


class TimeSheetTest(TestCase):
    def setUp(self):
        """
        Prepare users and groups for the test
        """
        config = Configuration.objects.create(name="email", value="@cristoreyny.net")
        config.save
        group = Group.objects.create(name="company")
        stuGroup = Group.objects.create(name="students")
        supUser = User.objects.create_user("super", "dburke@cristoreyny.org", "test")
        supUser.groups.add(group)
        supUser.save()
        user = User.objects.create_user("studentlog", "jstudent@cristoreyny.org", "test")
        user.groups.add(stuGroup)
        user.save()
        self.comp = WorkTeam.objects.create(team_name="fsdaf3aq3fa3fsc")
        self.comp.save()
        self.comp.login.add(supUser)
        self.comp.save()
        self.student = StudentWorker.objects.create(fname="studentaaaaa", lname="fjlkdsjfl321kev", placement=self.comp, username="jstudent")
        self.student.save()
        
        self.client = Client(HTTP_USER_AGENT = 'test')
        
    def test_supervisor(self):
        """
        Tests a supervisor logging in.
        """
        response = self.client.get('/', follow=True)
        # go to site, does it get to the log in screen?
        self.assertEquals(response.redirect_chain[0][0], 'http://testserver/accounts/login/?next=/')
        
        # supervisor logs in, goes to dashboard
        response = self.client.post('/accounts/login/?next=/', {'username':'super', 'password':'test'}, follow=True)
        self.assertContains(response, self.student.lname, msg_prefix="Student not in supervisor dash!")
        
        # supervisor creates new timesheet
        response = self.client.post('/work_study/supervisor/create_timesheet/' + str(self.student.id) + "/")
        self.assertContains(response, self.student.lname, msg_prefix="Student not in create time sheet!")
        self.assertContains(response, self.comp.team_name, msg_prefix="Company not in create time sheet!")
        self.assertContains(response, "Approved by student", msg_prefix="Not approved by student when supervisor creating")
        
        # supervisor submits new timesheet
        response = self.client.post('/work_study/supervisor/create_timesheet/' + str(self.student.id) + "/", \
            {'student': 1, 'company':1, 'date': '2010-06-15', 'time_in': '9:30 AM', 'time_lunch': "12:00 PM", \
            'time_lunch_return': '1:00 PM', 'time_out': '5:00 PM', 'performance': 3, 'student_accomplishment': 'stuacomptext', \
            'supervisor_comment': 'supcmttest'})
        self.assertContains(response, "Timesheet submitted for " + str(self.student.fname), \
            msg_prefix="Not approved by student when supervisor creating")
        self.assertEquals(TimeSheet.objects.get(student=self.student).supervisor_comment, 'supcmttest')
        self.assertEquals(TimeSheet.objects.get(student=self.student).student_accomplishment, 'stuacomptext')
        self.assertEquals(TimeSheet.objects.get(student=self.student).approved, True)
        
        # check for student email
        self.assertEquals(mail.outbox[0].subject, "Time Sheet approved for " + unicode(self.student))
        self.assertEquals(mail.outbox[0].body, u'Hello fjlkdsjfl321kev, studentaaaaa,\nYour time card was approved.')
        self.assertEquals(mail.outbox[0].to[0], unicode(self.student.username) + "@cristoreyny.net")
        
    def test_student_no_super(self, supervisor=False):
        """
        Tests a student logging in and submitting a timesheet
        In this case the student has no primary supervisor, thus no email
        """
        # student logs in, goes to student_timesheet
        response = self.client.post('/accounts/login/?next=/', {'username':'studentlog', 'password':'test'}, follow=True)
        self.assertContains(response, self.student.lname, msg_prefix="Something wrong with student_timesheet")
        self.assertContains(response, "Not yet submitted by student", msg_prefix="Something wrong with student_timesheet")
        
        # supervisor submits new timesheet
        if supervisor:  #select primary supervisor (otherwise it would be like a student choosing a non new one)
            response = self.client.post("/", \
                {'student': 1, 'company':1, 'date': '2010-06-15', 'time_in': '9:30 AM', 'time_lunch': "12:00 PM", \
                'time_lunch_return': '1:00 PM', 'time_out': '5:00 PM', 'student_accomplishment': 'stuacomptext', 'my_supervisor': 1})
        else:
            response = self.client.post("/", \
                {'student': 1, 'company':1, 'date': '2010-06-15', 'time_in': '9:30 AM', 'time_lunch': "12:00 PM", \
                'time_lunch_return': '1:00 PM', 'time_out': '5:00 PM', 'student_accomplishment': 'stuacomptext'})
        self.assertContains(response, "Timesheet has be successfully submitted, your supervisor has been notified.", \
            msg_prefix="Timesheet submission not successful")
        self.assertEquals(TimeSheet.objects.get(student=self.student).approved, False)
        self.assertEquals(TimeSheet.objects.get(student=self.student).student_accomplishment, 'stuacomptext')
        self.assertEquals(TimeSheet.objects.get(student=self.student).supervisor_key != None and \
            TimeSheet.objects.get(student=self.student).supervisor_key != "", True)
            
        
    def test_supervisor_approve(self):
        """
        After a student submits an timesheet supervisor may approve it.
        """
        self.test_student_no_super()
        response = self.client.post('/accounts/login/?next=/', {'username':'super', 'password':'test'}, follow=True)
        self.assertNotContains(response, 'href="/approve?key="', msg_prefix="supervisor_key not showing up")
        self.assertContains(response, '<td class="border"> fjlkdsjfl321kev, studentaaaaa </td>', count=2)
        
        # go to approve timesheet screen
        response = self.client.get("/work_study/approve/?key=" + str(TimeSheet.objects.get(student=self.student).supervisor_key))
        self.assertContains(response, self.student.lname, msg_prefix="Student not in create time sheet!")
        self.assertContains(response, self.comp.team_name, msg_prefix="Company not in create time sheet!")
        self.assertContains(response, "Approved by student", msg_prefix="Not approved by student when supervisor creating")
        self.assertContains(response, "stuacomptext", msg_prefix="Student accomplishment not present")
        
        # approve timesheet
        response = self.client.post("/work_study/approve/?key=" + str(TimeSheet.objects.get(student=self.student).supervisor_key), \
            {'student': 1, 'company':1, 'date': '2010-06-15', 'time_in': '9:30 AM', 'time_lunch': "12:00 PM", \
            'time_lunch_return': '1:00 PM', 'time_out': '5:00 PM', 'performance': 3, 'student_accomplishment': 'stuacomptext', \
            'supervisor_comment': 'supcmttest'})
        self.assertContains(response, "Time Card Approved!", msg_prefix="Not approved.")
        self.assertEquals(TimeSheet.objects.get(student=self.student).supervisor_comment, 'supcmttest')
        self.assertEquals(TimeSheet.objects.get(student=self.student).student_accomplishment, 'stuacomptext')
        self.assertEquals(TimeSheet.objects.get(student=self.student).approved, True)
        
    def test_supervisor_email(self):
        """
        Test a student submitting a timesheet and the supervisor getting the link
        following through on the link is already done in test_supervisor_approve
        """
        cont = Contact.objects.create(fname="tesrfdsf", email="test@contacts.com")
        cont.save()
        self.comp.contacts.add(cont)
        self.comp.save()
        self.student.primary_contact = cont
        self.student.save()
        
        # now a link should get sent
        self.test_student_no_super(supervisor=True)
        self.assertEquals(mail.outbox[0].subject, "Time Sheet for " + unicode(self.student))
        self.assertEquals(mail.outbox[0].to[0], cont.email)
