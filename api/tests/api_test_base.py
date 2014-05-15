from django.test import TestCase, Client
from django.contrib.auth.models import User
from ecwsp.schedule.models import MarkingPeriod, Course
from ecwsp.sis.models import SchoolYear, Student, Cohort
from datetime import datetime
from django.db import connection

class APITestBase(TestCase):
    """
    the base TestCase for our API
    """

    # Instructions - run the API test with the following command:
    # ./manage.py test api

    def setUp(self):
        """
        Everyone needs a test client, or so says the django doc!
        """
        self.client = Client()

        # create a normal user
        self.user = User.objects.create(
            username='normaluser',
            email='user1@email.com',
            password='foo'
        )

        # create an admin user
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='user2@email.com',
            password='bar'
        )

    def login_normal_user(self):
        """
        log in a non-admin user for the current client test session
        """
        self.client.login(username='normaluser', password='foo')

    def login_admin_user(self):
        """
        log in an admin user for the current client test session
        """
        self.client.login(username='adminuser', password='bar')

    def create_test_marking_period(self):
        """
        create a marking period for testing purposes
        """
        active_school_year = SchoolYear(
            name = '2013-2014',
            start_date = datetime.strptime('Aug 1 2013', '%b %d %Y'),
            end_date = datetime.strptime('May 31 2014', '%b %d %Y'),
            active_year = True
        )
        active_school_year.save()

        new_marking_period = MarkingPeriod(
            name = 'Test Period',
            shortname = 'TP1',
            start_date = datetime.strptime('Jan 1 2014', '%b %d %Y'),
            end_date = datetime.strptime('May 31 2014', '%b %d %Y'),
            school_year = active_school_year,
            active = True,
        )
        new_marking_period.save()
        return new_marking_period

    def create_test_course(self):
        """
        create a course for testing purposes
        """
        new_course = Course(
            fullname = "Test Course",
            shortname = "TC1"
        )
        new_course.save()
        return new_course

    def create_test_cohort(self):
        """
        create a sample cohort for testing purposes
        """
        new_cohort = Cohort(name="PROLES", primary=True)
        new_cohort.save()
        return new_cohort

    def create_test_student(self):
        """
        create a sample student for testing purposes
        """
        # student cohort table is not created in the test env
        # why? I have no idea, but I did find a past example of testing
        # in the Attendance app where this was needed
        try:
            sql = '''CREATE TABLE `sis_studentcohort` (
                `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
                `student_id` integer NOT NULL,
                `cohort_id` integer NOT NULL,
                `primary` bool NOT NULL);'''
            cursor = connection.cursor()
            cursor.execute(sql)
        except:
            pass

        new_student = Student(first_name="Joe", last_name="Schmo")
        new_student.save()
        return new_student





