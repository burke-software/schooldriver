from ecwsp.sis.tests import SisTestMixin
from django.test import TestCase
from ecwsp.sis.models import GradeScaleRule, GradeScale
from ecwsp.grades.models import Grade
import time
from decimal import Decimal

class GradeScaleTests(SisTestMixin, TestCase):
    def setUp(self):
        super(GradeScaleTests, self).setUp()
        self.build_grade_cache()
        scale = self.scale = GradeScale.objects.create(name="test")
        GradeScaleRule.objects.create(min_grade=50, max_grade=Decimal('59.99'), letter_grade='F', numeric_scale=1, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=60, max_grade=69.99, letter_grade='D', numeric_scale=1.5, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=70, max_grade=79.99, letter_grade='C', numeric_scale=2, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=80, max_grade=89.99, letter_grade='B', numeric_scale=3, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=90, max_grade=90, letter_grade='A', numeric_scale=4, grade_scale=scale)
        self.data.school_year.grade_scale = scale
        self.data.school_year.save()

    def test_grade_scale(self):
        scale = self.scale
        self.assertEqual(scale.to_letter(50), 'F')
        self.assertEqual(scale.to_letter(Decimal('59.99')), 'F')
        self.assertEqual(scale.to_letter(55.34234), 'F')
        self.assertEqual(scale.to_letter(1000), None)
        self.assertEqual(scale.to_numeric(50), 1)

        grade = Grade.objects.get(
            student = self.data.student2,
            course_section = self.data.course_section2,
            marking_period = self.data.marking_period
            )
        # this grade is known to be "75"
        self.assertEqual(grade.get_grade(letter=True), 'C')

    def test_scale_lookup_speed(self):
        grade = Grade.objects.get(
            student = self.data.student2,
            course_section = self.data.course_section2,
            marking_period = self.data.marking_period
            )
        start = time.time()
        i = 1000
        for _ in range(i):
            grade.get_grade(letter=True)
        end = time.time()
        run_time = end - start
        print '{} scale lookups took {} seconds'.format(i, run_time)
        with self.assertNumQueries(1):
            grade.get_grade(letter=True)