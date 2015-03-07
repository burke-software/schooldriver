from django.test import TestCase
from ecwsp.sis.sample_data import SisData
from ecwsp.sis.tests import SisTestMixin
from ecwsp.sis.models import Student
from ecwsp.grades.models import GradeCalculator
from ecwsp.schedule.models import CourseSection
import time


class GradeCalculationTests(SisTestMixin, TestCase):
    def setUp(self):
        self.data = SisData()
        self.data.create_basics()
        self.calc = GradeCalculator()

    def test_final_grade_speed(self):
        """ Ensure we can calculate a lot of course grades quickly """
        self.data.create_x_student_grades()
        course_section = CourseSection.objects.all().first()
        start = time.time()
        for enrollment in course_section.courseenrollment_set.all():
            self.calc.get_course_grade(enrollment)
        run_time = time.time() - start
        print(run_time)
        self.assertLess(run_time, 0.2)

    def test_gpa(self):
        self.data.create_x_student_grades(courses_per=6)
        students = Student.objects.all()
        start = time.time()
        for student in students:
            self.calc.get_student_gpa(student)
        run_time = time.time() - start
        print(run_time)
        self.assertLess(run_time, 1.0)
