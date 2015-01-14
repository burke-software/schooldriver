from ecwsp.sis.sample_data import SisData
from ecwsp.sis.models import *
from ecwsp.attendance.models import *
from ecwsp.grades.models import *
from ecwsp.schedule.models import *
from ecwsp.benchmark_grade.models import *

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
        self.create_sample_tc_school_years()
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

    def create_sample_tc_school_years(self):
        self.year1 = SchoolYear.objects.create(
            name="TC-2014-2015",
            start_date=datetime.date(2014,8,25),
            end_date=datetime.date(2015,6,19),
            active_year=True
            )
        self.year2 = SchoolYear.objects.create(
            name="TC-2015-2016",
            start_date=datetime.date(2015,8,25),
            end_date=datetime.date(2016,6,19),
            active_year=False
            )

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

        # these are just some useful lists you can use to discover courses
        self.course_shortnames_set1 = ["bus2","span","wlit","geom10","phys10","mchrist","whist"]
        self.course_shortnames_set2 = ["bus3","span3","alg11","chem11","ushist"]

    def create_sample_tc_course_sections(self):
        self.create_sample_tc_course_sections_year_1()
        self.create_sample_tc_course_sections_year_2()

    def get_course_sections_by_year_name(self, year_name):
        return CourseSection.objects.filter(name__contains=year_name)

    def create_sample_tc_course_sections_year_1(self):
        # year 1 consists of the set1 of courses
        course_shortnames = self.course_shortnames_set1
        for shortname in course_shortnames:
            self.create_course_section_from_shortname_and_year_name(shortname, "TC-2014-2015")

    def create_sample_tc_course_sections_year_2(self):
        # year two consists of the set2 of courses
        course_shortnames = self.course_shortnames_set2
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
        self.tc_student2 = Student.objects.create(first_name="Quentin", last_name="Twin", username="qtwin")
        self.tc_student3 = Student.objects.create(first_name="Lazzy", last_name="Mazzy", username="lazzymazzy")
        year1_course_sections = self.get_course_sections_by_year_name("TC-2014-2015")
        year2_course_sections = self.get_course_sections_by_year_name("TC-2015-2016")
        # enroll our first, third students in the year 1 course sections
        self.enroll_tc_student_in_course_sections(self.tc_student1, year1_course_sections)
        self.enroll_tc_student_in_course_sections(self.tc_student3, year1_course_sections)

        # enroll our second student in both years
        self.enroll_tc_student_in_course_sections(self.tc_student2, year1_course_sections)
        self.enroll_tc_student_in_course_sections(self.tc_student2, year2_course_sections)

    def enroll_tc_student_in_course_sections(self, student, course_sections):
        for section in course_sections:
            CourseEnrollment.objects.create(user=student, course_section=section)

    def create_sample_tc_student_grades(self):
        self.create_sample_tc_student1_grades()
        self.create_sample_tc_student2_grades()

    def create_sample_tc_student1_grades(self):
        student = self.tc_student1
        # this data is from an actual student
        section_grade_data = [
            {"name": "bus2-section-TC-2014-2015",    "grades":[3.67, 3.89, 4.00, None, None, None]},
            {"name": "span-section-TC-2014-2015",    "grades":[3.63, 3.65, 2.98, None, None, None]},
            {"name": "wlit-section-TC-2014-2015",    "grades":[3.48, 3.60, 3.00, None, None, None]},
            {"name": "geom10-section-TC-2014-2015",  "grades":[2.46, 1.52, 1.28, None, None, None]},
            {"name": "phys10-section-TC-2014-2015",  "grades":[3.28, 3.28, 3.42, None, None, None]},
            {"name": "mchrist-section-TC-2014-2015", "grades":[3.23, 3.14, 3.97, None, None, None]},
            {"name": "whist-section-TC-2014-2015",   "grades":[3.39, 3.51, 3.63, None, None, None]}
        ]
        self.save_all_section_grade_data(student, section_grade_data)

    def create_sample_tc_student2_grades(self):
        # ok this data is completely made up
        student = self.tc_student2
        section_grade_data = [
            {"name": "bus2-section-TC-2014-2015",    "grades":[3, 3, 4, 3, 3, 3]},
            {"name": "span-section-TC-2014-2015",    "grades":[2, 4, 4, 4, 3, 3]},
            {"name": "wlit-section-TC-2014-2015",    "grades":[3, 3, 4, 3, 3, 3]},
            {"name": "geom10-section-TC-2014-2015",  "grades":[2, 4, 4, 3, 2, 4]},
            {"name": "phys10-section-TC-2014-2015",  "grades":[3, 4, 4, 4, 3, 3]},
            {"name": "mchrist-section-TC-2014-2015", "grades":[2, 3, 4, 3, 4, 3]},
            {"name": "whist-section-TC-2014-2015",   "grades":[3, 4, 4, 4, 3, 2]}
            ]
        # I'm splitting up the years visually just so it's easier to debug
        section_grade_data += [
            {"name": "bus3-section-TC-2015-2016",    "grades":[2, 3, 4, 3, 3, 4]},
            {"name": "span3-section-TC-2015-2016",   "grades":[4, 4, 4, 4, 4, 4]},
            {"name": "alg11-section-TC-2015-2016",   "grades":[2, 3, 4, 3, 3, 3]},
            {"name": "chem11-section-TC-2015-2016",  "grades":[4, 4, 4, 4, 3, 4]},
            {"name": "ushist-section-TC-2015-2016",  "grades":[3, 3, 4, 3, 3, 3]}
        ]
        self.save_all_section_grade_data(student, section_grade_data)

    def save_all_section_grade_data(self, student, section_grade_data):
        for section_data in section_grade_data:
            self.save_section_marking_period_grades(
                student=student,
                section_name=section_data["name"],
                grades=section_data["grades"]
                )

    def save_section_marking_period_grades(self, student, section_name, grades):
        section = CourseSection.objects.get(name=section_name)
        marking_periods = list(section.marking_period.all().extra(order_by=["name"]))
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

    def create_sample_tc_benchmark_data(self):
        self.toggle_benchmark_grade_on_active_year()
        self.create_calculation_rule()
        self.create_benchmark_categories()
        self.create_calculation_rule_per_course_categories()
        self.create_sample_benchmark_items()
        self.create_sample_marks_for_sample_student()

    def toggle_benchmark_grade_on_active_year(self):
        school_year = self.year1
        school_year.benchmark_grade = True
        school_year.save()

    def create_calculation_rule(self):
        self.tc_calculation_rule = CalculationRule.objects.create(
            first_year_effective=self.year1,
            points_possible = 4,
            decimal_places = 2,
        )

    def create_benchmark_categories(self):
        Category.objects.bulk_create([
            Category(
                name="Standards",
                fixed_points_possible=4.0,
                display_in_gradebook=True,
                fixed_granularity=0.5,
                display_order=1,
            ),
            Category(
                name="Engagement",
                fixed_points_possible=4.0,
                display_in_gradebook=True,
                fixed_granularity=0.5,
                display_order=2,
            ),
            Category(
                name="Assignment Completion",
                fixed_points_possible=4.0,
                display_in_gradebook=True,
                fixed_granularity=0.5,
                display_order=3,
            ),
            Category(
                name="Daily Practice",
                display_order=4,
                display_in_gradebook=True,
                display_scale=100.00,
                display_symbol='%',
            ),
        ])
    
    def create_calculation_rule_per_course_categories(self):
        CalculationRulePerCourseCategory.objects.bulk_create([
            CalculationRulePerCourseCategory(
                category=Category.objects.get(name="Standards"),
                weight=0.7,
                calculation_rule = self.tc_calculation_rule,
            ),
            CalculationRulePerCourseCategory(
                category = Category.objects.get(name="Engagement"),
                weight = 0.1,
                calculation_rule = self.tc_calculation_rule,
            ),
            CalculationRulePerCourseCategory(
                category = Category.objects.get(name="Assignment Completion"),
                weight = 0.1,
                calculation_rule = self.tc_calculation_rule,
            ),
            CalculationRulePerCourseCategory(
                category=Category.objects.get(name="Daily Practice"),
                weight = 0.1,
                calculation_rule = self.tc_calculation_rule,
            ),
        ])

    def create_sample_benchmark_items(self):
        """ create assignment for 1 marking period in 1 course section """
        marking_period = MarkingPeriod.objects.get( name = "S1-TC" )
        course_section = CourseSection.objects.get( name = "bus2-section-TC-2014-2015")
        Item.objects.bulk_create([
            Item(
                name="Assignment1", 
                marking_period= marking_period, 
                points_possible= 4,
                course_section = course_section,
                category=Category.objects.get(name="Standards"),
            ),
            Item(
                name="Assignment2", 
                marking_period= marking_period, 
                points_possible= 4,
                course_section = course_section,
                category=Category.objects.get(name="Engagement"),
            ),
            Item(
                name="Assignment3", 
                marking_period= marking_period, 
                points_possible= 4,
                course_section = course_section,
                category=Category.objects.get(name="Assignment Completion"),
            ),
            Item(
                name="Assignment4", 
                marking_period= marking_period, 
                points_possible= 4,
                course_section = course_section,
                category=Category.objects.get(name="Daily Practice"),
            )
        ])

    def create_sample_marks_for_sample_student(self):
        Mark.objects.bulk_create([
            Mark(
                item = Item.objects.get( name = "Assignment1" ),
                student = self.tc_student3,
                mark = 4.0
            ),
            Mark(
                item = Item.objects.get( name = "Assignment2" ),
                student = self.tc_student3,
                mark = 3.0
            ),
            Mark(
                item = Item.objects.get( name = "Assignment3" ),
                student = self.tc_student3,
                mark = 2.5
            ),
            Mark(
                item = Item.objects.get( name = "Assignment4" ),
                student = self.tc_student3,
                mark = 3.5
            ),
        ])

    def create_new_category_and_adjust_all_category_weights(self):
        self.create_new_finals_category()
        self.adjust_category_weights_to_reflect_new_finals_category_addition()
        self.create_sample_finals_assignment()

    def create_new_finals_category(self):
        Category.objects.create(
            name="Finals",
            fixed_points_possible=4.0,
            display_in_gradebook=True,
            fixed_granularity=0.5,
            display_order=5,
        )

        CalculationRulePerCourseCategory.objects.create(
            category=Category.objects.get(name="Finals"),
            weight=0.05,
            calculation_rule = self.tc_calculation_rule,
        )

    def adjust_category_weights_to_reflect_new_finals_category_addition(self):
        CalculationRulePerCourseCategory.objects.filter(category__name="Standards").update(weight=0.70)
        CalculationRulePerCourseCategory.objects.filter(category__name="Assignment Completion").update(weight=0.0834)
        CalculationRulePerCourseCategory.objects.filter(category__name="Engagement").update(weight=0.0833)
        CalculationRulePerCourseCategory.objects.filter(category__name="Daily Practice").update(weight=0.0833)

    def create_sample_finals_assignment(self):
        marking_period = MarkingPeriod.objects.get( name = "S1-TC" )
        course_section = CourseSection.objects.get( name = "bus2-section-TC-2014-2015")
        Item.objects.create(
            name="Final Exam 1", 
            marking_period= marking_period, 
            points_possible= 4,
            course_section = course_section,
            category=Category.objects.get(name="Finals"),
        )


            

