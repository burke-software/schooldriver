from django.test import TestCase
from ecwsp.schedule.models import *
from constance import config
        
class DefaultCourseCreditTest(TestCase):
    """
    Test that value of course credits for a new Course object
    is set to constance default value when not otherwise specified.
    """
    def setUp(self):
        """test that course credits are set to default when not specified"""
        self.course = Course.objects.create(fullname="blah 101", shortname="blah")   
        self.course_credits = config.DEFAULT_COURSE_CREDITS
    
    def test_default_course_credits_set(self):
        self.assertEqual(self.course.credits, self.course_credits)
        

         

	    
