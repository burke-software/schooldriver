from ecwsp.sis.sample_data import SisData
from ecwsp.sis.models import *
from ecwsp.attendance.models import *
from ecwsp.grades.models import *
from ecwsp.schedule.models import *

import datetime

class SampleTCData(SisData):
    """some useful data modeled after Cristo Rey Twin Cities actual data"""

    def create_sample_tc_data(self):
        self.create_sample_tc_school_years_and_marking_periods()
        self.create_sample_tc_normal_course_types()
        self.create_sample_tc_courses()
        self.create_sample_tc_course_sections()
        self.create_sample_tc_students()
        self.create_sample_tc_student_grades()

    def create_sample_tc_school_years_and_marking_periods(self):
        year = SchoolYear.objects.create(name="TC 2014-2015", start_date=datetime.date(2014,8,25), end_date=datetime.date(2015,6,19), active_year=True)
        marking_periods = [
            ["S1-TC", datetime.date(2014,8,25), datetime.date(2014,10,3)],
            ["S2-TC", datetime.date(2014,10,6), datetime.date(2014,11,14)],
            ["S3-TC", datetime.date(2014,11,17), datetime.date(2015,1,23)],
            ["S4-TC", datetime.date(2015,1,27), datetime.date(2013,3,13)],
            ["S5-TC", datetime.date(2015,3,16), datetime.date(2015,5,1)],
            ["S6-TC", datetime.date(2015,5,4), datetime.date(2015,6,18)]
        ]
        marking_period_objects = []
        for MP in marking_periods:
            new_period = MarkingPeriod(name=MP[0], weight=1, start_date=MP[1], end_date=MP[2], school_year=year)
            marking_period_objects.append(new_period)
        MarkingPeriod.objects.bulk_create(marking_period_objects)

    def create_sample_tc_normal_course_types(self):
        CourseType.objects.create(name='Normal-TC', weight=1, boost=0.0)

    def create_sample_tc_courses(self):
        # course = [Name, Shortname, Credits, Graded]
        courses = [
            ["Business 2",          "bus2",     6, True],
            ["Sophomore Spanish",   "span",     6, True],
            ["World Literature",    "wlit",     6, True],
            ["Geometry 10",         "geom10",   6, True],
            ["Sophomore Physics",   "phys10",   6, True],
            ["Mission of Christ",   "mchrist",  6, True],
            ["World History",       "whist",    6, True]
        ]
        course_objects = []
        course_type = CourseType.objects.get(name='Normal-TC')
        for C in courses:
            new_course = Course(fullname=C[0], shortname=C[1], credits=C[2], graded=C[3], course_type = course_type)
            course_objects.append(new_course)
        Course.objects.bulk_create(course_objects)

    def create_sample_tc_course_sections(self):
        marking_periods = MarkingPeriod.objects.filter(school_year__name="TC 2014-2015")
        course_shortnames = ["bus2", "span", "wlit", "geom10", "phys10", "mchrist", "whist"]
        for shortname in course_shortnames:
            # all section names wil just be in the form of "wlit-section1"
            section_name = shortname + "-section1"
            course = Course.objects.get(shortname = shortname)
            new_section = CourseSection.objects.create(course = course, name=section_name)
            for MP in marking_periods:
                new_section.marking_period.add(MP)

    def create_sample_tc_students(self):
        self.tc_student1 = Student.objects.create(first_name="David", last_name="Twin", username="dtwin")
        self.enroll_tc_student_in_course_sections(self.tc_student1)

    def enroll_tc_student_in_course_sections(self, student):
        course_shortnames = ["bus2", "span", "wlit", "geom10", "phys10", "mchrist", "whist"]
        for shortname in course_shortnames:
            section_name = shortname + "-section1"
            section = CourseSection.objects.get(name=section_name)
            CourseEnrollment.objects.create(user=student, course_section=section)

    def create_sample_tc_student_grades(self):
        student = self.tc_student1
        section_grade_data = [
            {"name": "bus2-section1",    "grades":[3.67, 3.89, 4.00, None, None, None]},
            {"name": "span-section1",    "grades":[3.63, 3.65, "IN", None, None, None]},
            {"name": "wlit-section1",    "grades":[3.48, 3.60, 3.00, None, None, None]},
            {"name": "geom10-section1",  "grades":["IN", "IN", "IN", None, None, None]},
            {"name": "phys10-section1",  "grades":[3.28, 3.28, 3.42, None, None, None]},
            {"name": "mchrist-section1", "grades":[3.23, "IN", 3.97, None, None, None]},
            {"name": "whist-section1",   "grades":[3.39, 3.51, 3.63, None, None, None]}
        ]
        for section_data in section_grade_data:
            self.save_section_marking_period_grades(
                student=student, 
                section_name=section_data["name"], 
                grades=section_data["grades"]
                )
                    
    def save_section_marking_period_grades(self, student, section_name, grades):
        marking_periods = self.get_marking_period_list()
        section = CourseSection.objects.get(name=section_name)
        for grade in grades:
            if grade is not None:
                i = grades.index(grade)
                grade = Grade.objects.get(
                    student=student,
                    course_section=section,
                    marking_period=marking_periods[i]
                    )
                grade.grade = grade
                grade.save()

    def get_marking_period_list(self):
        marking_period_names = ["S1-TC", "S2-TC", "S3-TC", "S4-TC", "S5-TC", "S6-TC"]
        marking_periods = []
        for mp_name in marking_period_names:
            marking_periods.append(MarkingPeriod.objects.get(name=mp_name))
        return marking_periods


