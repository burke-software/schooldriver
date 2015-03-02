from django.contrib.auth.models import User, Group
import unittest
from django.core import mail
from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from ecwsp.discipline.models import *
from ecwsp.discipline.views import *
from ecwsp.discipline.forms import *
from ecwsp.administration.models import *
from ecwsp.sis.models import Student
from constance import config
import datetime

class TestDisciplineConstanceVariables(TestCase):
    def setUp(self):
        """tests for constance settings in discipline views and forms"""
        self.client = Client()
        self.user = User.objects.create_user(username="firstuser", password="12345")
        self.tardies_before_disc = config.ATTENDANCE_DISC_TARDIES_BEFORE_DISC
        self.client.login(username='firstuser',password='12345')
        self.student = Student.objects.create(mname="Harry")
        
        
    def test_tardies_before_disc(self):
        """
        test constance setting default
        currently fails because of a 404 response.
        working on this
        
        """
        content_type = ContentType.objects.get_for_model(StudentDiscipline)
        permission = Permission.objects.get(content_type=content_type, codename='change_studentdiscipline')
        request = self.client.post('discipline.views.generate_from_attendance')
        request.user = self.user
        request.user.user_permissions.add(permission)
        #response = generate_from_attendance(request)

        
    def test_discipline_merit_default_days(self):
        """tests whether the default is set for this constance config variable"""
        default_start_date = get_start_date_default()
        #default value
        self.days_back = int(config.DISCIPLINE_MERIT_DEFAULT_DAYS)
        default_date = datetime.date.today()
        work_days = (0,1,2,3,4)
        #counts back number of days from config value
        while self.days_back > 0:
            while not default_date.weekday() in work_days:
                default_date = default_date - datetime.timedelta(days=1)
            default_date = default_date - datetime.timedelta(days=1)
            self.days_back -= 1
        #default_date is number of work days from config value ago
        self.assertEqual(default_date, default_start_date)
        
    def test_get_default_one(self):
        """tests the constance config for discipline merit level one"""
        self.default_one = int(config.DISCIPLINE_MERIT_LEVEL_ONE)
        form_default = get_default_one()
        self.assertEqual(self.default_one, form_default)
    
    def test_get_default_two(self):
        """tests the constance config for discipline merit level two"""
        self.default_two = int(config.DISCIPLINE_MERIT_LEVEL_TWO)
        form_default = get_default_two()
        self.assertEqual(self.default_two, form_default)
    
    def test_get_default_three(self):
        """tests the constance config for discipline merit level three"""
        self.default_three = int(config.DISCIPLINE_MERIT_LEVEL_THREE)
        form_default = get_default_three()
        self.assertEqual(self.default_three, form_default)
    
    def test_get_default_four(self):
        """tests the constance config for discipline merit level four"""
        self.default_four = int(config.DISCIPLINE_MERIT_LEVEL_FOUR)
        form_default = get_default_four()
        self.assertEqual(self.default_four, form_default)
        

