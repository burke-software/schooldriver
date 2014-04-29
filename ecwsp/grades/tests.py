from ecwsp.sis.models import *
from django.test import TestCase
import datetime
from models import *
import random


class GradeCalculationTests(TestCase):

    def setUp(self):
        self.student = Student.objects.create(username='ttesty')

    def test_current_vs_older(self):
        StudentYearGrade.objects.create(student=self.student, year_name='2011-2012')
        for i in range(20):
            grade = random.random()
            a_grade = Grade.objects.create(grade=grade)
            self.student.studentyeargrade_set.add(a_grade)
        syg = self.student.studentyeargrade_set.get(year_name='2011-2012')
        current = syg.calculate_grade(date_report=datetime.date.today())
        older = syg.calculate_grade()
        self.assertEqual(current, older)

