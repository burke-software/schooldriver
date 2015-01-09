from ecwsp.sis.tests import SisTestMixin
from django.test import TestCase

class GradeCacheTests(SisTestMixin, TestCase):
    def setUp(self):
        super(GradeCacheTests, self).setUp()
        self.build_grade_cache()

    def test_passing_letter_grade(self):
        student = self.data.student
        section = self.data.course_section
        grades = student.grade_set.filter(course_section=section)
        for grade in grades:
            grade.set_grade('HP')
            grade.save()
        ce = student.courseenrollment_set.filter(course_section=section).first()
        self.assertEqual(ce.grade, 'P')

