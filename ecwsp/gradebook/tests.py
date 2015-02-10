from django.test import TestCase
from ecwsp.sis.tests import SisTestMixin
from ecwsp.sis.models import SchoolYear
from ecwsp.schedule.models import (
    Department)
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient 
from ecwsp.gradebook.models import Assignment
from ecwsp.schedule.models import Course, CourseSection
from .models import *
from .exceptions import WeightContainsNone
#from .sample_data import BenchmarkSisData
from ecwsp.sis.sample_data import SisData
from decimal import Decimal
from decimal import InvalidOperation
import unittest
import json

class AssignmentViewsetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.course = Course.objects.create(id=1, fullname="first course", shortname="first")
        self.section = CourseSection.objects.create(course=self.course, name="section one")
        self.assignment = Assignment.objects.create(name="first assignment", course_section=self.section)
        self.data = {'name': 'first assignment', 'course_section': self.section.pk}
		
    def test_get_assignment_list(self):
        response = self.client.get(reverse('assignment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
		
    def test_get_assignment_detail(self):
        response = self.client.get(reverse('assignment-detail', args=(self.assignment.pk,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_assignment(self):
        response = self.client.post(reverse('assignment-list'), self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		
    def test_put_assignment(self):
        request = self.client.post(reverse('assignment-list'), self.data, format='json')
        #data to update initially posted data
        data_two = {'name': 'second name', 'course_section': self.section.pk}
        response = self.client.put(reverse('assignment-detail', args=(self.assignment.pk,)), data_two)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
		
    def test_delete_assignment(self):
        response = self.client.delete(reverse('assignment-detail', args=(self.assignment.pk,)))
        self.assertEqual(response.status_code, 204)
	
@unittest.skip("Gradebook is an unreleased backend right now, we can unskip when it's ready")
class GradeCalculationTests(SisTestMixin, TestCase):
    def setUp(self):
        self.data = SisData()
        self.data.create_basics()
        self.build_grade_cache()
        self.data.course_section1.save()

    def create_assignment(
            self, points_possible, category=None, assignment_type=None):
        return Assignment.objects.create(
            name="A",
            marking_period=self.data.marking_period,
            points_possible=points_possible,
            course_section=self.data.course_section1,
            category=category,
            assignment_type=assignment_type,
        )

    def create_and_check_mark(
            self, assignment, mark, check, demonstration=None):
        Mark.objects.create(
            assignment=assignment, student=self.data.student, mark=mark,
            demonstration=demonstration
        )
        grade = self.data.student.grade_set.get(
            marking_period=self.data.marking_period,
            course_section=self.data.course_section1)
        try:
            check = Decimal(check)
            self.assertAlmostEquals(grade.get_grade(), check)
        except (InvalidOperation, TypeError):  # Letter grade
            check = str(check)
            self.assertEquals(grade.get_grade(), check)

    def create_assignments(self, test_data):
        for data in test_data:
            assignment = self.create_assignment(data[0])
            self.create_and_check_mark(assignment, data[1], data[2])

    def create_assignments_api(self, test_data):
        pass  # 'STUB'

    def test_basic_grades(self):
        """ Keep creating assignments for student and check the grade """
        # [points_possible, points_earned, cumlative expected grade]
        test_data = [
            [10, 5, 50],
            [5, 5, 66.67],
            [300, 0, 3.17],
            [50, 50, 16.44],
            [10, 10, 18.67],
            [5000, 5000, 94.33],
            [5000, None, 94.33],
        ]
        self.create_assignments(test_data)

    def test_basic_grades_edge_high(self):
        """ Keep creating assignments for student and check the grade
        checking edge cases """
        test_data = [
            [10, 10, 100],
            [10, None, 100],
        ]
        self.create_assignments(test_data)

    def test_basic_grades_edge_low(self):
        test_data = [
            [10, None, ''],
            [10, 0, 0],
        ]
        self.create_assignments(test_data)


    def test_find_calculation_rule(self):
        year1 = SchoolYear.objects.get(name="2013-2014")
        year2 = SchoolYear.objects.get(name="2014-long time")
        year3 = SchoolYear.objects.get(name="2015-16")
        rule1 = CalculationRule.objects.create(first_year_effective=year1)
        rule2 = CalculationRule.objects.create(first_year_effective=year2)
        active = CalculationRule.find_active_calculation_rule()
        self.assertEquals(active, rule2)
        self.assertEquals(CalculationRule.find_calculation_rule(year1), rule1)
        self.assertEquals(CalculationRule.find_calculation_rule(year2), rule2)
        self.assertEquals(CalculationRule.find_calculation_rule(year3), rule2)

    def test_calculation_rule(self):
        CalculationRule.objects.create(
            first_year_effective=self.data.school_year,
            points_possible=4,
        )
        test_data = [
            [10, 5, 2],
            [5, 5, 2.67],
        ]
        self.create_assignments(test_data)
        self.create_assignments_api(test_data)

    def test_calc_rule_per_course_category_department(self):
        dept_eng = Department.objects.create(name="English")
        dept_math = Department.objects.create(name="Math")
        course_section = self.data.course_section1
        course_section.save()
        course_section.course.department = dept_eng
        course_section.course.save()
        calc_rule = CalculationRule.objects.create(
            first_year_effective=self.data.school_year,
        )

        cat1 = AssignmentCategory.objects.create(name="Standards")
        only_math_rule = CalculationRulePerCourseCategory.objects.create(
            category=cat1,
            weight=1,
            calculation_rule=calc_rule,
        )
        only_math_rule.apply_to_departments.add(dept_math)
        only_eng_rule = CalculationRulePerCourseCategory.objects.create(
            category=cat1,
            weight=5,
            calculation_rule=calc_rule,
        )
        only_eng_rule.apply_to_departments.add(dept_eng)

        cat2 = AssignmentCategory.objects.create(name="Engagement")
        all_rule = CalculationRulePerCourseCategory.objects.create(
            category=cat2,
            weight=1,
            calculation_rule=calc_rule,
        )
        test_data = [
            [10, 5, 50, cat1],
            [10, 5, 50, cat2],
        ]
        for data in test_data:
            assignment = self.create_assignment(data[0], category=data[3])
            self.create_and_check_mark(assignment, data[1], data[2])
        course_section.course.department = dept_math
        course_section.course.save()
        test_data = [
            [10, 5, 50, cat1],
            [10, 5, 50, cat2],
        ]
        for data in test_data:
            assignment = self.create_assignment(data[0], category=data[3])
            self.create_and_check_mark(assignment, data[1], data[2])

    def test_calc_rule_per_course_category(self):
        calc_rule = CalculationRule.objects.create(
            first_year_effective=self.data.school_year,
        )
        cat1 = AssignmentCategory.objects.create(name="Standards")
        cat2 = AssignmentCategory.objects.create(name="Engagement")
        cat3 = AssignmentCategory.objects.create(name="Engagement")
        CalculationRulePerCourseCategory.objects.create(
            category=cat1,
            weight=0.7,
            calculation_rule=calc_rule,
        )
        CalculationRulePerCourseCategory.objects.create(
            category=cat2,
            weight=0.3,
            calculation_rule=calc_rule,
        )
        CalculationRulePerCourseCategory.objects.create(
            category=cat3,
            weight=5,
            calculation_rule=calc_rule,
        )
        test_data = [
            [10, 0, 0, cat1],
            [10, 10, 30, cat2],
            [10, 10, 30, cat2],
            [30, 27, 28.2, cat2],
        ]
        for data in test_data:
            assignment = self.create_assignment(data[0], category=data[3])
            self.create_and_check_mark(assignment, data[1], data[2])
        # Test invalid weight
        assignment = self.create_assignment(
            10, category=None)
        self.assertRaises(
            WeightContainsNone,
            self.create_and_check_mark, assignment, 10, 66.67)

    def test_rule_substitution(self):
        course = self.data.course_section1
        calc_rule = CalculationRule.objects.create(
            first_year_effective=self.data.school_year,
        )
        sub_rule = CalculationRuleSubstitution.objects.create(
            operator='<',
            match_value='3.0',
            display_as='INC',
            calculation_rule=calc_rule,
        )
        test_data = [
            [4, 3, 75],
            [4, 2.5, 'INC'],
            [4, 4, 'INC'],
            [4, 3, 'INC'],
        ]
        for data in test_data:
            assignment = self.create_assignment(data[0])
            self.create_and_check_mark(assignment, data[1], data[2])

    def test_rule_substitution_depts(self):
        dept_eng = Department.objects.create(name="English")
        dept_math = Department.objects.create(name="Math")
        course = self.data.course_section1
        course.course.department = dept_eng
        course.course.save()
        calc_rule = CalculationRule.objects.create(
            first_year_effective=self.data.school_year,
        )
        eng_sub_rule = CalculationRuleSubstitution.objects.create(
            operator='<',
            match_value='3.0',
            display_as='ENG',
            calculation_rule=calc_rule,
        )
        eng_sub_rule.apply_to_departments.add(dept_eng)
        math_sub_rule = CalculationRuleSubstitution.objects.create(
            operator='>=',
            match_value='3.0',
            display_as='MATH',
            calculation_rule=calc_rule,
        )
        math_sub_rule.apply_to_departments.add(dept_math)
        test_data = [
            [4, 4, 100],
            [4, 2.5, 'ENG'],
            [4, 4, 'ENG'],
        ]
        for data in test_data:
            assignment = self.create_assignment(data[0])
            self.create_and_check_mark(assignment, data[1], data[2])

    def test_assignment_type(self):
        type1 = AssignmentType.objects.create(name="A", weight=0.4)
        type2 = AssignmentType.objects.create(name="A", weight=0.5)
        type3 = AssignmentType.objects.create(name="A", weight=0.1)
        test_data = [
            [10, 5, 50, type1],
            [10, 5, 50, type1],
            [10, 8, 66.67, type2],
            [10, 10, 70, type3],
        ]
        for data in test_data:
            assignment = self.create_assignment(
                data[0], assignment_type=data[3])
            self.create_and_check_mark(assignment, data[1], data[2])
        assignment = self.create_assignment(
            10, assignment_type=None)
        self.assertRaises(
            WeightContainsNone,
            self.create_and_check_mark, assignment, 10, 1)

    def test_assignment_type_and_category(self):
        type1 = AssignmentType.objects.create(name="A", weight=0.4)
        type2 = AssignmentType.objects.create(name="A", weight=0.6)
        calc_rule = CalculationRule.objects.create(
            first_year_effective=self.data.school_year,
        )
        cat1 = AssignmentCategory.objects.create(name="Standards")
        cat2 = AssignmentCategory.objects.create(name="Engagement")
        CalculationRulePerCourseCategory.objects.create(
            category=cat1,
            weight=0.7,
            calculation_rule=calc_rule,
        )
        CalculationRulePerCourseCategory.objects.create(
            category=cat2,
            weight=0.3,
            calculation_rule=calc_rule,
        )
        test_data = [
            [10, 10, 100, type1, cat1],
            [10, 0, 70, type1, cat2],
            [10, 0, 28, type2, cat1],
            [10, 0, 28, type2, cat2],
            [6, 5, 33.62, type2, cat2],
        ]
        for data in test_data:
            assignment = self.create_assignment(
                data[0], assignment_type=data[3], category=data[4])
            self.create_and_check_mark(assignment, data[1], data[2])


    def test_demonstration(self):
        cat1 = AssignmentCategory.objects.create(
            name="Standards", allow_multiple_demonstrations=True)
        cat2 = AssignmentCategory.objects.create(name="No demon")
        assignment1 = self.create_assignment(4, category=cat1)
        assignment2 = self.create_assignment(4, category=cat1)
        assignment3 = self.create_assignment(5, category=cat2)
        assignment4 = self.create_assignment(6, category=cat2)
        demonstration1 = Demonstration.objects.create(assignment=assignment1)
        demonstration2 = Demonstration.objects.create(assignment=assignment1)
        demonstration3 = Demonstration.objects.create(assignment=assignment1)
        demonstration4 = Demonstration.objects.create(assignment=assignment2)
        self.create_and_check_mark(
            assignment1, 1, 25, demonstration=demonstration1)
        self.create_and_check_mark(
            assignment1, 4, 100, demonstration=demonstration2)
        self.create_and_check_mark(
            assignment1, 2, 100, demonstration=demonstration3)
        self.create_and_check_mark(
            assignment2, 3, 87.5, demonstration=demonstration4)
        self.create_and_check_mark(assignment3, 3, 76.92)
        self.create_and_check_mark(assignment4, 4, 73.68)

