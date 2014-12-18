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
        self.create_sample_tc_course_sections_year_1()
        self.create_sample_tc_course_sections_year_2()
        self.create_sample_tc_students()
        self.create_sample_tc_student_grades()

    def create_sample_tc_school_years_and_marking_periods(self):
        self.year1 = SchoolYear.objects.create(name="TC-2014-2015", start_date=datetime.date(2014,8,25), end_date=datetime.date(2015,6,19), active_year=True)
        self.year2 = SchoolYear.objects.create(name="TC-2015-2016", start_date=datetime.date(2015,8,25), end_date=datetime.date(2016,6,19), active_year=False)
        marking_periods = [
            ["S1-TC", datetime.date(2014,8,25), datetime.date(2014,10,3), self.year1],
            ["S2-TC", datetime.date(2014,10,6), datetime.date(2014,11,14), self.year1],
            ["S3-TC", datetime.date(2014,11,17), datetime.date(2015,1,23), self.year1],
            ["S4-TC", datetime.date(2015,1,27), datetime.date(2013,3,13), self.year1],
            ["S5-TC", datetime.date(2015,3,16), datetime.date(2015,5,1), self.year1],
            ["S6-TC", datetime.date(2015,5,4), datetime.date(2015,6,18), self.year1],
            ["S1-TC2", datetime.date(2015,8,25), datetime.date(2015,10,3), self.year2],
            ["S2-TC2", datetime.date(2015,10,6), datetime.date(2015,11,14), self.year2],
            ["S3-TC2", datetime.date(2015,11,17), datetime.date(2016,1,23), self.year2],
            ["S4-TC2", datetime.date(2016,1,27), datetime.date(2016,3,13), self.year2],
            ["S5-TC2", datetime.date(2016,3,16), datetime.date(2016,5,1), self.year2],
            ["S6-TC2", datetime.date(2016,5,4), datetime.date(2016,6,18), self.year2]
        ]
        marking_period_objects = []
        for MP in marking_periods:
            new_period = MarkingPeriod(name=MP[0], weight=1, start_date=MP[1], end_date=MP[2], school_year=MP[3])
            marking_period_objects.append(new_period)
        MarkingPeriod.objects.bulk_create(marking_period_objects)

    def create_sample_tc_normal_course_types(self):
        CourseType.objects.create(name='Normal-TC', weight=1, boost=0.0)

    def create_sample_tc_courses(self):
        # course = [Name, Shortname, Credits, Graded]
        courses = [
            ["Business 2",          "bus2"],
            ["Sophomore Spanish",   "span"],
            ["World Literature",    "wlit"],
            ["Geometry 10",         "geom10"],
            ["Sophomore Physics",   "phys10"],
            ["Mission of Christ",   "mchrist"],
            ["World History",       "whist"],
            ["Business 3",          "bus3"],
            ["Junior Spanish",      "span3"],
            ["Algebra 11",          "alg11"],
            ["Junior Chemistry",    "chem11"],
            ["US History",          "ushist"]
        ]
        course_objects = []
        course_type = CourseType.objects.get(name='Normal-TC')
        for C in courses:
            new_course = Course(fullname=C[0], shortname=C[1], credits=6, graded=True, course_type = course_type)
            course_objects.append(new_course)
        Course.objects.bulk_create(course_objects)

    def create_sample_tc_course_sections_year_1(self):
        course_shortnames = ["bus2", "span", "wlit", "geom10", "phys10", "mchrist", "whist"]
        for shortname in course_shortnames:
            self.create_course_section_from_shortname_and_year_name(shortname, "TC-2014-2015")

    def create_sample_tc_course_sections_year_2(self):
        course_shortnames = ["bus3", "span3", "alg11", "chem11", "ushist"]
        for shortname in course_shortnames:
            self.create_course_section_from_shortname_and_year_name(shortname, "TC-2015-2016")

    def create_course_section_from_shortname_and_year_name(self, shortname, year_name):
        section_name = shortname + "-section-%s" % year_name
        course = Course.objects.get(shortname = shortname)
        new_section = CourseSection.objects.create(course = course, name=section_name)
        self.assign_year_marking_periods_to_course_section(year_name, new_section)

    def assign_year_marking_periods_to_course_section(self, year_name, course_section):
        marking_periods = MarkingPeriod.objects.filter(school_year__name=year_name)
        for MP in marking_periods:
            course_section.marking_period.add(MP)

    def create_sample_tc_students(self):
        self.tc_student1 = Student.objects.create(first_name="David", last_name="Twin", username="dtwin")
        self.enroll_tc_student_in_course_sections(self.tc_student1)

    def enroll_tc_student_in_course_sections(self, student):
        course_shortnames = ["bus2", "span", "wlit", "geom10", "phys10", "mchrist", "whist"]
        for shortname in course_shortnames:
            section_name = shortname + "-section-TC-2014-2015"
            section = CourseSection.objects.get(name=section_name)
            CourseEnrollment.objects.create(user=student, course_section=section)

    def create_sample_tc_student_grades(self):
        student = self.tc_student1
        section_grade_data = [
            {"name": "bus2",    "grades":[3.67, 3.89, 4.00, None, None, None]},
            {"name": "span",    "grades":[3.63, 3.65, 2.98, None, None, None]},
            {"name": "wlit",    "grades":[3.48, 3.60, 3.00, None, None, None]},
            {"name": "geom10",  "grades":[2.46, 1.52, 1.28, None, None, None]},
            {"name": "phys10",  "grades":[3.28, 3.28, 3.42, None, None, None]},
            {"name": "mchrist", "grades":[3.23, 3.14, 3.97, None, None, None]},
            {"name": "whist",   "grades":[3.39, 3.51, 3.63, None, None, None]}
        ]
        for section_data in section_grade_data:
            self.save_section_marking_period_grades(
                student=student, 
                section_name=section_data["name"] + "-section-TC-2014-2015", 
                grades=section_data["grades"]
                )
                    
    def save_section_marking_period_grades(self, student, section_name, grades):
        marking_periods = self.get_marking_period_list()
        section = CourseSection.objects.get(name=section_name)
        for i in range(6):
            grade = grades[i]
            if grade is not None:
                grade_object = Grade.objects.get(
                    student=student,
                    course_section=section,
                    marking_period=marking_periods[i]
                    )
                grade_object.grade = Decimal(grade)
                grade_object.save()

    def get_marking_period_list(self):
        marking_period_names = ["S1-TC", "S2-TC", "S3-TC", "S4-TC", "S5-TC", "S6-TC"]
        marking_periods = []
        for mp_name in marking_period_names:
            marking_periods.append(MarkingPeriod.objects.get(name=mp_name))
        return marking_periods


