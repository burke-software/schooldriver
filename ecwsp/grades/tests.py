from ecwsp.sis.models import *
from ecwsp.sis.tests import SisTestMixin
from django.test import TestCase
from .models import *
from ecwsp.sis.sample_data import SisData
from ecwsp.sis.sample_tc_data import SampleTCData
from ecwsp.schedule.models import (
    CourseEnrollment, Course, CourseSection, MarkingPeriod)
import datetime
import time


class GradeCalculationTests(SisTestMixin, TestCase):
    def setUp(self):
        self.data = SisData()
        self.data.create_basics()

    def get_simple_test_data(self):
        student = self.data.student
        mp1 = self.data.marking_period
        mp2 = self.data.marking_period2
        mp3 = self.data.marking_period3
        course = self.data.course_section1
        return [
            [student, course, mp1, 100, 100],
            [student, course, mp2, 50, 75],
            [student, course, mp3, 90.5, 80.17],
        ]

    def set_grade(self, enrollment, mp, grade):
        grade_obj = Grade(enrollment=enrollment, marking_period=mp)
        grade_obj.set_grade(grade)
        grade_obj.save()

    def set_final_grade(self, enrollment, grade):
        grade_obj = FinalGrade(enrollment=enrollment)
        grade_obj.set_grade(grade)
        grade_obj.save()

    def check_grade(self, enrollment, expect, date=None):
        average = Grade.get_course_grade(enrollment, date=date)
        self.assertEquals(average, expect)

    def set_and_check_grade(self, enrollment, mp, grade, expect,
                            date=None):
        self.set_grade(enrollment, mp, grade)
        self.check_grade(enrollment, expect, date=date)

    def test_basic_grades(self):
        """ /docs/specs/course_grades.md#Rounding """
        for data in self.get_simple_test_data():
            enrollment = CourseEnrollment.objects.get(
                user=data[0], course_section=data[1])
            self.set_and_check_grade(enrollment, data[2], data[3], data[4])

    def test_course_average_respect_time(self):
        """ See /docs/specs/course_grades.md#Time and averages
        mp1 start_date=`2014-07-1` and end_date=`2014-9-1`
        mp2 start_date=`2014-9-2` and end_date=`2015-3-1`
        """
        mark1 = 50
        mark2 = 100
        student = self.data.student
        mp1 = self.data.marking_period
        mp2 = self.data.marking_period2
        date1 = datetime.date(2099, 1, 1)
        date2 = datetime.date(2014, 10, 1)
        section = self.data.course_section1
        enroll = self.data.course_enrollment
        self.set_grade(enroll, mp1, mark1)
        self.set_grade(enroll, mp2, mark2)
        self.check_grade(enroll, 75, date=date1)
        self.check_grade(enroll, 50, date=date2)

    def test_marking_period_weight(self):
        """ See /docs/specs/course_grades.md#Marking Period Weights """
        mp1 = self.data.marking_period
        mp1.weight = 1.5
        mp1.save()
        test_data = self.get_simple_test_data()
        # Adjust expected for mp1 weight of 1.5
        test_data[1][4] = 80
        test_data[2][4] = 83
        for data in test_data:
            enrollment = CourseEnrollment.objects.get(
                user=data[0], course_section=data[1])
            self.set_and_check_grade(enrollment, data[2], data[3], data[4])

    def test_final_override(self):
        """ See /docs/specs/course_grades.md#Marking Period Weights """
        test_data = self.get_simple_test_data()
        for data in test_data:
            enrollment = CourseEnrollment.objects.get(
                user=data[0], course_section=data[1])
            self.set_grade(enrollment, data[2], data[3])
        self.set_final_grade(enrollment, 82)
        self.check_grade(enrollment, 82)


class GradeBaltTests(SisTestMixin, TestCase):
    """ These test ensure we meet requirements defined by Cristo Rey Baltimore including
    Grade scales, course weights, and letter grades
    Sample data is anonomized real grade data """

    def populate_database(self):
        """ Override, not using traditional test data """
        self.data = SisData()
        self.data.create_grade_scale_data()
        self.data.create_sample_honors_and_ap_data()

    def test_grade_get_grade(self):
        grade = self.data.grade
        self.assertAlmostEquals(grade.get_grade(), Decimal(72.70))
        self.assertEquals(grade.get_grade(letter=True), 'C')
        self.assertEquals(grade.get_grade(letter_and_number=True), '72.70 (C)')

    def test_letter_grade(self):
        mp1 = self.data.mp1
        mp2 = self.data.mp2
        mp3 = self.data.mp3
        mp4 = self.data.mp4
        test_data = [
            [mp1, 1, 'C'],
            [mp1, 2, 'F'],
            [mp1, 3, 'F'],
            [mp1, 4, 'A-'],
            [mp1, 5, 'B-'],
            [mp1, 6, 'A'],
            [mp1, 7, 'B-'],
            [mp1, 8, 'A'],
            [mp2, 1, 'C+'],
            [mp2, 2, 'B-'],
            [mp2, 3, 'D'],
            [mp2, 4, 'B'],
            [mp2, 5, 'D'],
            [mp2, 6, 'A'],
            [mp2, 7, 'B'],
            [mp2, 8, 'A'],
            [mp3, 1, 'F'],
            [mp3, 2, 'C'],
            [mp3, 3, 'C'],
            [mp3, 4, 'C'],
            [mp3, 5, 'C'],
            [mp3, 6, 'B'],
            [mp3, 7, 'C+'],
            [mp3, 8, 'A'],
            [mp4, 1, 'C'],
            [mp4, 2, 'C+'],
            [mp4, 3, 'D'],
            [mp4, 4, 'B+'],
            [mp4, 5, 'B'],
            [mp4, 6, 'A-'],
            [mp4, 7, 'B+'],
            [mp4, 8, 'A'],
        ]
        for x in test_data:
            grade = Grade.objects.get(
                student = self.data.student,
                marking_period=x[0],
                course_section=getattr(self.data, 'course_section' + str(x[1]))
                )
            self.assertEqual(grade.get_grade(letter=True), x[2])

    def test_snx_grade(self):
        """ Really just a normal run of the mill Marking Period grade
        Balt uses s1x, s2x as tests that affect final grades
        """
        grade = Grade.objects.get(marking_period=self.data.mps1x, course_section=self.data.course_section1)
        self.assertEqual(grade.get_grade(), 90)
        grade = Grade.objects.get(marking_period=self.data.mps2x, course_section=self.data.course_section1)
        self.assertEqual(grade.get_grade(), 79)

    def test_partial_course_average_grade(self):
        """ Tests getting the average of some but not all marking period averages """
        s1_ids = [self.data.mp1.id ,self.data.mp2.id ,self.data.mps1x.id]
        s2_ids = [self.data.mp3.id ,self.data.mp4.id ,self.data.mps2x.id]
        test_data = [
            [1, s1_ids, 78.08, 'C+'],
            [1, s2_ids, 71.96, 'D'],
            [2, s1_ids, 68.16, 'F'],
            [2, s2_ids, 70.84, 'D'],
            [3, s1_ids, 68.0, 'F'],
            [3, s2_ids, 69.84, 'D'],
            [4, s1_ids, 87.52, 'B+'],
            [4, s2_ids, 80.88, 'B-'],
            [5, s1_ids, 73.6, 'C'],
            [5, s2_ids, 80.08, 'B-'],
            [6, s1_ids, 93.2, 'A'],
            [6, s2_ids, 86.65, 'B+'],
            [7, s1_ids, 79.04, 'C+'],
            [7, s2_ids, 83.12, 'B'],
            [8, s1_ids, 100, 'A'],
            [8, s2_ids, 100, 'A'],
        ]
        for x in test_data:
            ce = CourseEnrollment.objects.get(user=self.data.student, course_section=getattr(self.data, 'course_section' + str(x[0])))
            self.assertAlmostEqual(ce.get_average_for_marking_periods(x[1]), Decimal(x[2]))
            self.assertEqual(ce.get_average_for_marking_periods(x[1], letter=True), x[3])

    def test_average_partial_round_before_letter(self):
        """ Example:
            ave(75.49, 77.50) = 76.495 = 76.50 = C+
            See /docs/specs/grade_scales.md
        """
        score1 = 75.49
        score2 = 77.50
        s1_ids = [self.data.mp1.id ,self.data.mp2.id]
        student = self.data.student
        course = Course.objects.create(
            fullname="Some", shortname="some", credits=1, graded=True)
        section = CourseSection.objects.create(
            name=course.shortname, course=course)
        ce = CourseEnrollment.objects.create(
            user=student,
            course_section=section)
        grade1 = Grade.objects.get_or_create(
            student=student,
            course_section=section,
            marking_period=self.data.mp1)[0]
        grade2 = Grade.objects.get_or_create(
            student=student,
            course_section=section,
            marking_period=self.data.mp2)[0]
        grade1.set_grade(score1)
        grade1.save()
        grade2.set_grade(score2)
        grade2.save()
        self.assertEqual(ce.get_average_for_marking_periods(s1_ids, letter=True), 'C+')


    def test_scaled_average(self):
        """ Tests an asinine method for averages by converting to non linear scale first """
        test_data = [
            [self.data.mp1, Decimal(2.0)],
            [self.data.mp2, Decimal(2.4)],
            [self.data.mp3, Decimal(1.9)],
            [self.data.mp4, Decimal(2.8)],
        ]
        for x in test_data:
            smpg = StudentMarkingPeriodGrade.objects.get(student=self.data.student, marking_period=x[0])
            self.assertAlmostEqual(smpg.get_scaled_average(rounding=1), x[1])

    def test_average(self):
        test_data = [
            [self.data.mps1x, 72.7],
            [self.data.mps2x, 71.8],
        ]
        for x in test_data:
            smpg = StudentMarkingPeriodGrade.objects.get(student=self.data.student, marking_period=x[0])
            self.assertAlmostEqual(smpg.get_average(rounding=1), Decimal(x[1]))

    def test_scaled_multiple_mp_average(self):
        test_data = [
            [[self.data.mp1.id, self.data.mp2.id, self.data.mps1x.id], Decimal(1.9)],
            [[self.data.mp3.id, self.data.mp4.id, self.data.mps2x.id], Decimal(2.1)],
        ]
        for x in test_data:
            average = Grade.get_scaled_multiple_mp_average(self.data.student, x[0], rounding=1)
            self.assertAlmostEqual(average, x[1])

    def test_scaled_final_year_average(self):
        test_data = [
            [self.data.year, Decimal(2.2)],
        ]
        for x in test_data:
            year_grade = self.data.student.studentyeargrade_set.get(year=x[0])
            average = year_grade.get_grade(numeric_scale=True, rounding=1, prescale=True)
            self.assertAlmostEqual(average, x[1])

    def test_balt_gpa(self):
        gpa = self.data.student.calculate_gpa(rounding=1, prescale=True)
        self.assertAlmostEqual(gpa, Decimal(2.2))

    def test_final_grade(self):
        test_data = [
            [1, 'C'],
            [2, 'D'],
            [3, 'D'],
            [4, 'B'],
            [5, 'C+'],
            [6, 'A-'],
            [7, 'B-'],
            [8, 'A'],
        ]
        for x in test_data:
            ce = CourseEnrollment.objects.get(
                user=self.data.student,
                course_section=getattr(self.data, 'course_section' + str(x[0])))
            with self.assertNumQueries(1):
                self.assertEqual(ce.get_grade(letter=True), x[1])

    def test_honors_and_ap_scaled_grades(self):
        """
        assert that the honors and ap grades receive correct boost by
        replicating the grades in our manual spreadsheet
        """

        # Now, test that the scaled averages are correct
        test_data = [
            {'mp': self.data.mp1, 'boosted': Decimal(4.0), 'unboosted': Decimal(3.7)},
            {'mp': self.data.mp2, 'boosted': Decimal(3.6), 'unboosted': Decimal(3.3)},
            {'mp': self.data.mp3, 'boosted': Decimal(3.7), 'unboosted': Decimal(3.4)},
            {'mp': self.data.mp4, 'boosted': Decimal(3.5), 'unboosted': Decimal(3.2)}
        ]
        for x in test_data:
            smpg = StudentMarkingPeriodGrade.objects.get(student=self.data.honors_student, marking_period=x['mp'])
            self.assertAlmostEqual(smpg.get_scaled_average(rounding=1), x['boosted'])
            self.assertAlmostEqual(smpg.get_scaled_average(rounding=1, boost=False), x['unboosted'])

    def test_honors_and_ap_student_year_grade(self):
        """
        assert that the end of the year grade is correct
        """

        # try without pre-scaling
        year_grade = self.data.honors_student.studentyeargrade_set.get(year=self.data.year)
        average = year_grade.get_grade(numeric_scale=True, rounding=1)
        self.assertAlmostEqual(average, Decimal(3.8))

        # try with pre-scaling
        year_grade = self.data.honors_student.studentyeargrade_set.get(year=self.data.year)
        average = year_grade.get_grade(numeric_scale=True, rounding=1, prescale=True)
        self.assertAlmostEqual(average, Decimal(3.6))

        # try with pre-scaling but without boost
        year_grade = self.data.honors_student.studentyeargrade_set.get(year=self.data.year)
        average = year_grade.get_grade(numeric_scale=True, rounding=1, prescale=True, boost=False)
        self.assertAlmostEqual(average, Decimal(3.3))

    def test_honors_and_ap_letter_grades(self):
        """
        assert that the end-of-semester and final letter grades are correct

        for individual course sections that is...
        """
        expected_grades = [
            {'section': 'English-H', 's1': 'B+', 's2': 'B',  'final': 'B' },
            {'section': 'Precalc-H', 's1': 'B',  's2': 'B-', 'final': 'B' },
            {'section': 'Phys',      's1': 'A-', 's2': 'A-', 'final': 'A-'},
            {'section': 'Hist-AP',   's1': 'B-', 's2': 'B',  'final': 'B' },
            {'section': 'Span',      's1': 'A-', 's2': 'B',  'final': 'B+'},
            {'section': 'Photo',     's1': 'A',  's2': 'A',  'final': 'A' },
            {'section': 'Faith',     's1': 'B+', 's2': 'A-', 'final': 'B+'},
            {'section': 'Wrt Lab',   's1': 'A',  's2': 'A',  'final': 'A' }
            ]

        # first check final grades
        for x in expected_grades:
            section = CourseSection.objects.get(name = x['section'])
            ce = CourseEnrollment.objects.get(
                user = self.data.honors_student,
                course_section = section,
                )
            with self.assertNumQueries(1):
                self.assertEqual(ce.get_grade(letter=True), x['final'])

            sm1_grade = ce.get_average_for_marking_periods(
                marking_periods = [self.data.mp1.id, self.data.mp2.id, self.data.mps1x.id],
                letter = True,
                )
            sm2_grade = ce.get_average_for_marking_periods(
                marking_periods = [self.data.mp3.id, self.data.mp4.id, self.data.mps2x.id],
                letter = True,
                )

            self.assertEqual(sm1_grade, x['s1'])
            self.assertEqual(sm2_grade, x['s2'])

    def test_honors_student_gpa(self):
        """
        test that the student's gpa after 1 year is correct!
        """
        gpa = self.data.honors_student.calculate_gpa(rounding=1, prescale=True)
        self.assertAlmostEqual(gpa, Decimal(3.6))


class GradeCacheTests(SisTestMixin, TestCase):
    def setUp(self):
        super(GradeCacheTests, self).setUp()

    def test_passing_letter_grade(self):
        student = self.data.student
        section = self.data.course_section
        grades = student.grade_set.filter(course_section=section)
        for grade in grades:
            grade.set_grade('HP')
            grade.save()
        ce = student.courseenrollment_set.filter(course_section=section).first()
        self.assertEqual(ce.grade, 'P')


class GradeScaleTests(SisTestMixin, TestCase):
    def setUp(self):
        super(GradeScaleTests, self).setUp()
        scale = self.scale = GradeScale.objects.create(name="test")
        GradeScaleRule.objects.create(min_grade=50, max_grade=59.99, letter_grade='F', numeric_scale=1, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=60, max_grade=69.99, letter_grade='D', numeric_scale=1.5, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=70, max_grade=79.99, letter_grade='C', numeric_scale=2, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=80, max_grade=89.99, letter_grade='B', numeric_scale=3, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=90, max_grade=90, letter_grade='A', numeric_scale=4, grade_scale=scale)
        self.data.school_year.grade_scale = scale
        self.data.school_year.save()

    def test_grade_scale(self):
        scale = self.scale
        self.assertEqual(scale.to_letter(50), 'F')
        self.assertEqual(scale.to_letter(59.99), 'F')
        self.assertEqual(scale.to_letter(55.34234), 'F')
        self.assertEqual(scale.to_letter(1000), None)
        self.assertEqual(scale.to_numeric(50), 1)

        grade = self.data.grade
        self.assertEqual(grade.get_grade(letter=True), 'F')  # 50

    def test_scale_lookup_speed(self):
        grade = self.data.grade
        start = time.time()
        i = 1000
        for _ in range(i):
            grade.get_grade(letter=True)
        end = time.time()
        run_time = end - start
        print '{} scale lookups took {} seconds'.format(i, run_time)
        with self.assertNumQueries(1):
            grade.get_grade(letter=True)

class GradeTestTCSampleData(TestCase):
    def setUp(self):
        self.data = SampleTCData()
        self.data.create_sample_tc_data()

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

