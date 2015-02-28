from django.test import TestCase
from ecwsp.sis.sample_data import SisData
from ecwsp.sis.tests import SisTestMixin
from ecwsp.grades.models import Grade
from ecwsp.schedule.models import CourseSection
import time


class GradeCalculationTests(SisTestMixin, TestCase):
    def setUp(self):
        self.data = SisData()
        self.data.create_basics()
        self.data.create_30_student_grades()

    def test_final_grade_speed(self):
        """ Ensure we can calculate a lot of course grades quickly """
        course_section = CourseSection.objects.all().first()
        start = time.time()
        for enrollment in course_section.courseenrollment_set.all():
            Grade.get_course_grade(enrollment)
        run_time = time.time() - start
        self.assertLess(run_time, 0.3)
