from django.contrib.auth.models import User, Group
import unittest
from django.core import mail
from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command

from ecwsp.counseling.models import *
from ecwsp.volunteer_track.models import *
from ecwsp.sis.models import Student
from constance import config

class TestVolunteerSite(TestCase):
    def setUp(self):
        self.from_email_address = config.FROM_EMAIL_ADDRESS
        self.required_hours = config.VOLUNTEER_TRACK_REQUIRED_HOURS
        self.student = Student.objects.create(mname="Harry")
        self.volunteer = Volunteer.objects.create(student=self.student)
        self.site = Site.objects.create(site_name = "A Site", site_address="123 Sesame St", site_city="new york", site_state="ny", site_zip="12345")
        self.volunteer_site = VolunteerSite.objects.create(volunteer=self.volunteer, site=self.site, )    
    
    def test_get_hours_default(self):
        """test constance settings for volunteer_track_required_hours"""
        required_hours = get_hours_default()
        self.assertEqual(self.required_hours, required_hours)
        
