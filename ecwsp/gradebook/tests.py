from django.test import TestCase
from ecwsp.sis.tests import SisTestMixin
from ecwsp.sis.models import SchoolYear
from ecwsp.schedule.models import (
    Department, DepartmentGraduationCredits)
from .models import *
#from .sample_data import BenchmarkSisData
from ecwsp.sis.sample_data import SisData
from decimal import Decimal


class GradeCalculationTests(SisTestMixin, TestCase):
    def setUp(self):
        self.data = SisData()
        self.data.create_basics()
        self.build_grade_cache()

    def create_assignments(self, test_data):
        for data in test_data:
            assignment = Assignment.objects.create(
                name="Assignment" + str(data[2]),
                marking_period=self.data.marking_period,
                points_possible=data[0],
                course_section=self.data.course_section1,
            )
            Mark.objects.create(
                assignment=assignment, student=self.data.student, mark=data[1])
            grade = self.data.student.grade_set.get(
                marking_period=self.data.marking_period,
                course_section=self.data.course_section1)
            self.assertAlmostEquals(grade.get_grade(), Decimal(data[2]))

    def create_assignments_api(self, test_data):
        pass  # 'STUB'

    def test_basic_grades(self):
        """ Keep creating assignments for student and check the grade """
        course = self.data.course_section1
        course.save()
        # [points_possible, points_earned, cumlative expected grade]
        test_data = [
            [10, 5, 50],
            [5, 5, 66.67],
            [300, 0, 3.17],
            [50, 50, 16.44],
            [10, 10, 18.67],
            [5000, 5000, 94.33],
        ]
        self.create_assignments(test_data)
        self.create_assignments_api(test_data)

    def test_find_calculation_rule(self):
        year1, year2, year3 = SchoolYear.objects.all()[:3]
        rule1 = CalculationRule.objects.create(first_year_effective=year1)
        rule2 = CalculationRule.objects.create(first_year_effective=year2)
        active = CalculationRule.find_active_calculation_rule()
        self.assertEquals(active, year2)
        self.assertEquals(CalculationRule.find_calculation_rule(year1, rule1)
        self.assertEquals(CalculationRule.find_calculation_rule(year2, rule2)
        self.assertEquals(CalculationRule.find_calculation_rule(year3, rule2)



    def test_calculation_rule(self):
        CalculationRule.objects.create(
            first_year_effective=self.data.school_year,
            points_possible=4,
        )
        course = self.data.course_section1
        course.save()
        test_data = [
            [10, 5, 2],
            [5, 5, 2.64],
        ]
        self.create_assignments(test_data)
        self.create_assignments_api(test_data)

