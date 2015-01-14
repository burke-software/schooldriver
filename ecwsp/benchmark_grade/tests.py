from django.test import TestCase
from ecwsp.sis.tests import SisTestMixin
from ecwsp.schedule.models import (
    Department, DepartmentGraduationCredits, CourseSection, MarkingPeriod)
from .models import *
from .sample_data import BenchmarkSisData

from ecwsp.sis.sample_tc_data import SampleTCData
from ecwsp.grades.tasks import build_grade_cache
from ecwsp.benchmark_grade.utility import gradebook_get_average_and_pk, benchmark_calculate_course_aggregate
from decimal import Decimal

import unittest

@unittest.skip("This is going to be deprecated soon...")
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
            name="A", 
            marking_period=self.data.marking_period, 
            points_possible=3,
            course_section=course,
            category=Category.objects.get(name="Standards"),
        )
        demonstration = Demonstration.objects.create(name="1", item=item)
        mark = Mark.objects.create(
            demonstration=demonstration,
            item=item, 
            student=self.data.student, 
            mark=2.0)

        grade = self.data.student.grade_set.get(
            marking_period=self.data.marking_period,
            course_section=course)

        self.assertEquals(grade.get_grade(), 'INC')
        mark.mark = 4.0
        mark.save()
        self.assertEquals(grade.get_grade(), 4.0)


class TwinCitiesGradeCalculationTests(SisTestMixin, TestCase):
    def setUp(self):
        self.data = SampleTCData()
        self.data.create_sample_tc_data()
        self.data.create_sample_tc_benchmark_data()
        self.fetch_useful_data_and_bind_to_self()
        build_grade_cache()

    def fetch_useful_data_and_bind_to_self(self):
        self.student = self.data.tc_student3
        self.marking_period = MarkingPeriod.objects.get( name = "S1-TC" )
        self.course_section = CourseSection.objects.get( name = "bus2-section-TC-2014-2015")

    def get_benchmark_grade(self):
        """ get the benchmark grade for this particular student, 
        course_section and marking_period """
        grade, aggregate_id = gradebook_get_average_and_pk(
            student = self.student, 
            course_section = self.course_section, 
            marking_period = self.marking_period
            )
        return grade

    def force_benchmark_to_recalculate_grades(self):
        """ this wraps a function known to force a recalculation of 
        benchmark grades """
        benchmark_calculate_course_aggregate(
            student = self.student, 
            course_section = self.course_section, 
            marking_period = self.marking_period
            )

    def test_baseline_grade_calculation(self):
        """ assert benchmark is calculating correctly from the sample_data"""
        grade = self.get_benchmark_grade()
        self.assertEqual(grade, Decimal('3.70'))

    def test_grade_after_adding_new_category(self):
        """ create new Finals category and assert grades are as expected """
        self.data.create_new_category_and_adjust_all_category_weights()
        Mark.objects.create(
            item = Item.objects.get( name = "Final Exam 1" ),
            student = self.student,
            mark = 4.0
        )
        grade = self.get_benchmark_grade()
        self.assertEqual(grade, Decimal('3.75'))

    def test_adding_new_category_for_student_with_no_grade_in_the_new_category(self):
        # check the grade before adding a new category
        grade = self.get_benchmark_grade()
        self.assertEqual(grade, Decimal('3.70'))

        # add the new category and force a recalculation
        self.data.create_new_category_and_adjust_all_category_weights()
        self.force_benchmark_to_recalculate_grades()

        # check the new grade
        grade = self.get_benchmark_grade()
        self.assertEqual(grade, Decimal('3.74'))







        





