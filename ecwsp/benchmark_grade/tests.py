from django.test import TestCase
from ecwsp.sis.tests import SisTestMixin
from ecwsp.schedule.models import (
    Department, DepartmentGraduationCredits)
from .models import *
from .sample_data import BenchmarkSisData


class GradeCalculationTests(SisTestMixin, TestCase):
    def setUp(self):
        self.data = BenchmarkSisData()
        self.data.create_basics()
        self.data.create_tc_calculation_rules()
        self.build_grade_cache()

    def test_rule_substitution(self):
        course = self.data.course_section1
        course.save()
        item = Item.objects.create(
            name="A", marking_period=self.data.marking_period, points_possible=3,
            course_section=course,
            category=Category.objects.get(name="Standards"),
        )
        demonstration = Demonstration.objects.create(name="1", item=item)
        mark = Mark.objects.create(demonstration=demonstration,
            item=item, student=self.data.student, mark=2.0)
        grade = self.data.student.grade_set.get(
            marking_period=self.data.marking_period,
            course_section=course)
        self.assertEquals(grade.get_grade(), 'INC')
        mark.mark = 4.0
        mark.save()
        self.assertEquals(grade.get_grade(), 4.0)

