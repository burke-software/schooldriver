from django.test import TestCase
from ecwsp.sis.sample_tc_data import SampleTCData
from ecwsp.grades.tasks import build_grade_cache
from ecwsp.schedule.models import CourseSection
from ecwsp.grades.models import StudentYearGrade
import datetime

class GradeTestTCSampleData(TestCase):
    def setUp(self):
        self.data = SampleTCData()
        self.data.create_sample_tc_data()
        build_grade_cache()

    def verify_accuracy_of_grade_in_section_hash(self,student,section_hash):
        section_name = section_hash["name"]
        expected_grade = section_hash["grade"]
        course_section = CourseSection.objects.get(name=section_name)
        actual_grade = round(course_section.calculate_final_grade(student), 2)
        self.assertEqual(actual_grade, expected_grade)

    def test_course_section_final_grades(self):
        student = self.data.tc_student1
        expected_data = [
            {"name": "bus2-section-TC-2014-2015",    "grade":3.85},
            {"name": "span-section-TC-2014-2015",    "grade":3.42},
            {"name": "wlit-section-TC-2014-2015",    "grade":3.36},
            {"name": "geom10-section-TC-2014-2015",  "grade":1.75},
            {"name": "phys10-section-TC-2014-2015",  "grade":3.33},
            {"name": "mchrist-section-TC-2014-2015", "grade":3.45},
            {"name": "whist-section-TC-2014-2015",   "grade":3.51}
        ]
        for section_hash in expected_data:
            self.verify_accuracy_of_grade_in_section_hash(student,section_hash)

    def test_student2_course_section_final_grades(self):
        student = self.data.tc_student2
        expected_data = [
            {"name": "bus2-section-TC-2014-2015",    "grade":3.17},
            {"name": "span-section-TC-2014-2015",    "grade":3.33},
            {"name": "wlit-section-TC-2014-2015",    "grade":3.17},
            {"name": "geom10-section-TC-2014-2015",  "grade":3.17},
            {"name": "phys10-section-TC-2014-2015",  "grade":3.50},
            {"name": "mchrist-section-TC-2014-2015", "grade":3.17},
            {"name": "whist-section-TC-2014-2015",   "grade":3.33},
            {"name": "bus3-section-TC-2015-2016",    "grade":3.17},
            {"name": "span3-section-TC-2015-2016",   "grade":4.00},
            {"name": "alg11-section-TC-2015-2016",   "grade":3.00},
            {"name": "chem11-section-TC-2015-2016",  "grade":3.83},
            {"name": "ushist-section-TC-2015-2016",  "grade":3.17}
        ]
        for section_hash in expected_data:
            self.verify_accuracy_of_grade_in_section_hash(student,section_hash)

    def test_calculate_gpa_after_each_marking_period(self):
        end_dates = [datetime.date(2014,10,3),datetime.date(2014,11,14),datetime.date(2015,1,23)]
        expected_gpas = [3.31, 3.27, 3.24]
        student = self.data.tc_student1
        for i in range(3):
            gpa = student.calculate_gpa(date_report=end_dates[i])
            self.assertEqual(round(gpa, 2), expected_gpas[i])

    def test_student_2_year_grades(self):
        student = self.data.tc_student2
        year_grade_1 = StudentYearGrade.objects.get(student = student, year = self.data.year1)
        year_grade_2 = StudentYearGrade.objects.get(student = student, year = self.data.year2)
        self.assertEqual(round(year_grade_1.grade,2), 3.26)
        self.assertEqual(round(year_grade_2.grade,2), 3.43)

    def test_student2_lifetime_gpa(self):
        student = self.data.tc_student2
        year1_credits = 7
        year2_credits = 5
        year1_gpa = 3.26
        year2_gpa = 3.43
        total_points = (year1_gpa * year1_credits) + (year2_gpa * year2_credits)
        total_credits = year1_credits + year2_credits
        expected_gpa = total_points / total_credits
        actual_gpa = student.calculate_gpa()
        self.assertEqual(round(expected_gpa, 2), round(actual_gpa, 2))

