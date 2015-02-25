# never import * except test data (because who cares about clean tests)
from ecwsp.sis.models import *
from ecwsp.attendance.models import *
from ecwsp.admissions.models import *
from ecwsp.grades.models import *
from ecwsp.schedule.models import *
from ecwsp.grades.tasks import *

import random
import string
import logging
import datetime

class SisData(object):
    """ Put data creation code here. sample data code not here is punishible by death .
        Grammatical and spelling errors, however... --------------------^
    """
    def create_all(self):
        """ This will populate all sample data """
        self.create_basics()
        self.create_admissions_choice_data()

    def create_required(self):
        """ A place for 100% required data """
        self.normal_type = CourseType.build_default()

    def create_basics(self):
        """ A very simple school, probably want this in mosts tests
        Depends on create_required
        """
        # Run dependencies first
        self.create_required()

        # Add graduating classes, birthdays, etc. that won't get outdated
        now = datetime.datetime.now()
        
        graduated_year = now.year - 1
        senior_year = now.year
        junior_year = now.year + 1
        sophomore_year = now.year + 2
        freshman_year = now.year + 3

        self.class_year0 = ClassYear.objects.create(year=graduated_year, full_name="Class of " + str(graduated_year))
        self.class_year1 = ClassYear.objects.create(year=senior_year, full_name="Class of " + str(senior_year))
        self.class_year2 = ClassYear.objects.create(year=junior_year, full_name="Class of " + str(junior_year))
        self.class_year3 = ClassYear.objects.create(year=sophomore_year, full_name="Class of " + str(sophomore_year))
        self.class_year4 = ClassYear.objects.create(year=freshman_year, full_name="Class of " + str(freshman_year))

        # Populate grade levels
        GradeLevel.objects.bulk_create([
            GradeLevel(id=9, name="Freshman"),
            GradeLevel(id=10, name="Sophomore"),
            GradeLevel(id=11, name="Junior"),
            GradeLevel(id=12, name="Senior"),
        ])

        # Populate some school years based on the current month/year
        school_year_base = now.year
        # If in 2015 and not yet August, active year will be 2014-2015. After August 1 it'll be 2015-2016
        if now.month < 8:
            school_year_base = now.year - 1

        SchoolYear.objects.bulk_create([
            SchoolYear(name=str(school_year_base+2)+"-"+str(school_year_base+3), start_date=datetime.date(school_year_base+2,8,1), end_date=datetime.date(school_year_base + 3,7,31)),
            SchoolYear(name=str(school_year_base+1)+"-"+str(school_year_base+2), start_date=datetime.date(school_year_base+1,8,1), end_date=datetime.date(school_year_base + 2,7,31)),
            SchoolYear(name=str(school_year_base)+"-"+str(school_year_base+1), start_date=datetime.date(school_year_base,8,1), end_date=datetime.date(school_year_base+1,7,31), active_year=True),
            SchoolYear(name=str(school_year_base-1)+"-"+str(school_year_base), start_date=datetime.date(school_year_base-1,8,1), end_date=datetime.date(school_year_base,7,31)),
            SchoolYear(name=str(school_year_base-2)+"-"+str(school_year_base-1), start_date=datetime.date(school_year_base-2,8,1), end_date=datetime.date(school_year_base-1,7,31)),
            SchoolYear(name=str(school_year_base-3)+"-"+str(school_year_base-2), start_date=datetime.date(school_year_base-3,8,1), end_date=datetime.date(school_year_base-2,7,31)),
        ])
        # Set one archetypal object. If I want a year I will use this
        self.school_year = SchoolYear.objects.get(active_year=True)

        def random_birthday(class_year):
            day = random.randint(1,28)
            month = random.randint(1,12)
            offset = 0
            if (month > 8): # If you're born in September, your birth year will be 1 earlier
                offset = 1
            year = class_year.year - 18 - offset
            return datetime.date(year, month, day)

        def random_ssn():
            first_three = random.randint(100,999)
            middle_two = random.randint(10,99)
            last_four = random.randint(1000,9999)
            ssn_string = str(first_three) + "-" + str(middle_two) + "-" + str(last_four)
            return ssn_string

        # Note bulk does not call save() and other limitations
        # so it's ok to not use bulk
        # Don't change the order, other objects depend on the id being in this order
        self.student   = Student.objects.create(first_name="Alex", last_name="Jackson", username="ajackson", sex="M", class_of_year=self.class_year1, bday=random_birthday(self.class_year1), ssn=random_ssn())
        self.student2  = Student.objects.create(first_name="Pat", last_name="Williams", username="pwilliams", mname="Logan", sex="F", class_of_year=self.class_year2, bday=random_birthday(self.class_year2), ssn=random_ssn())
        self.student3  = Student.objects.create(first_name="Chris", last_name="Robinson", username="crobinson", sex="M", class_of_year=self.class_year3, bday=random_birthday(self.class_year3), ssn=random_ssn())
        self.student4  = Student.objects.create(first_name="Terry", last_name="Harris", username="tharris", mname="Quinn", sex="F", class_of_year=self.class_year4, bday=random_birthday(self.class_year4), ssn=random_ssn())
        self.student5  = Student.objects.create(first_name="Ashton", last_name="Thomas", username="athomas", sex="M", class_of_year=self.class_year1, bday=random_birthday(self.class_year1), ssn=random_ssn())
        self.student6  = Student.objects.create(first_name="Ashley", last_name="James", username="ajames", mname="Drew", sex="F", class_of_year=self.class_year2, bday=random_birthday(self.class_year2))
        self.student7  = Student.objects.create(first_name="Cameron", last_name="Lee", username="clee", sex="M", class_of_year=self.class_year3, bday=random_birthday(self.class_year3), ssn=random_ssn())
        self.student8  = Student.objects.create(first_name="Casey", last_name="Jones", username="cjones", mname="Cameron", sex="F", class_of_year=self.class_year4, bday=random_birthday(self.class_year4), ssn=random_ssn())
        self.student9  = Student.objects.create(first_name="Drew", last_name="Jenkins", username="djenkins", sex="M", class_of_year=self.class_year1, bday=random_birthday(self.class_year1), ssn=random_ssn())
        self.student10 = Student.objects.create(first_name="Hayden", last_name="Carter", username="hcarter", sex="F", class_of_year=self.class_year2, bday=random_birthday(self.class_year2), ssn=random_ssn())
        self.student11 = Student.objects.create(first_name="Jordan", last_name="Brown", username="jbrown", sex="M", class_of_year=self.class_year3, bday=random_birthday(self.class_year3), ssn=random_ssn())
        self.student12 = Student.objects.create(first_name="Logan", last_name="Walker", username="lwalker", mname="Alex", sex="F", class_of_year=self.class_year4, bday=random_birthday(self.class_year4), ssn=random_ssn())
        self.student13 = Student.objects.create(first_name="Micah", last_name="Lewis", username="mlewis", sex="M", class_of_year=self.class_year1, bday=random_birthday(self.class_year1), ssn=random_ssn())
        self.student14 = Student.objects.create(first_name="Morgan", last_name="Johnson", username="mjohnson", sex="F", class_of_year=self.class_year2, bday=random_birthday(self.class_year2))
        self.student15 = Student.objects.create(first_name="Parker", last_name="Scott", username="pscott", sex="M", class_of_year=self.class_year3, bday=random_birthday(self.class_year3), ssn=random_ssn())
        self.student16 = Student.objects.create(first_name="Quinn", last_name="Brooks", username="qbrooks", mname="Taylor", sex="F", class_of_year=self.class_year4, bday=random_birthday(self.class_year4), ssn=random_ssn())
        self.student17 = Student.objects.create(first_name="Riley", last_name="Richardson", username="rrichardson", sex="M", class_of_year=self.class_year1, bday=random_birthday(self.class_year1), ssn=random_ssn())
        self.student18 = Student.objects.create(first_name="Sidney", last_name="Sanders", username="ssanders", sex="F", class_of_year=self.class_year2, bday=random_birthday(self.class_year2), ssn=random_ssn())
        self.student19 = Student.objects.create(first_name="Taylor", last_name="Bell", username="tbell", sex="M", class_of_year=self.class_year3, bday=random_birthday(self.class_year3), ssn=random_ssn())


        MarkingPeriod.objects.bulk_create([
            MarkingPeriod(name="tri1 2014", start_date=datetime.date(2014,7,1), end_date=datetime.date(2014,9,1), school_year=self.school_year, monday=True, friday=True),
            MarkingPeriod(name="tri2 2014", start_date=datetime.date(2014,9,2), end_date=datetime.date(2015,3,1), school_year=self.school_year, monday=True, friday=True),
            MarkingPeriod(name="tri3 2014", start_date=datetime.date(2015,3,2), end_date=datetime.date(2050,5,1), school_year=self.school_year, monday=True, friday=True),
        ])
        self.marking_period = MarkingPeriod.objects.get(name="tri1 2014")
        self.marking_period2 = MarkingPeriod.objects.get(name="tri2 2014")
        self.marking_period3 = MarkingPeriod.objects.get(name="tri3 2014")

        self.teacher1 = self.faculty = Faculty.objects.create(username="dburke", first_name="david", last_name="burke", teacher=True)
        self.teacher2 = Faculty.objects.create(username="jbayes", first_name="jeff", last_name="bayes", teacher=True)
        aa = Faculty.objects.create(username="aa", first_name="aa", is_superuser=True, is_staff=True)
        aa.set_password('aa')
        aa.save()
        admin = Faculty.objects.create(username="admin", first_name="admin", is_superuser=True, is_staff=True)
        admin.set_password('admin')
        admin.save()

        Course.objects.bulk_create([
            Course(fullname="Math 101", shortname="Math101", credits=3, graded=True),
            Course(fullname="History 101", shortname="Hist101", credits=3, graded=True),
            Course(fullname="Homeroom FX 2011", shortname="FX1", homeroom=True, credits=1),
            Course(fullname="Homeroom FX 2012", shortname="FX2", homeroom=True, credits=1),
        ])
        self.course = Course.objects.get(fullname="Math 101")
        self.course2 = Course.objects.get(fullname="History 101")

        CourseSection.objects.bulk_create([
            CourseSection(course_id=self.course.id, name="Math A"),
            CourseSection(course_id=self.course.id, name="Math B"),
            CourseSection(course_id=self.course2.id, name="History A"),
            CourseSection(course_id=self.course2.id, name="History 1 MP only"),
        ])
        self.course_section = self.course_section1 = CourseSection.objects.get(name="Math A")
        self.course_section2 = CourseSection.objects.get(name="Math B")
        self.course_section3 = CourseSection.objects.get(name="History A")
        self.course_section4 = CourseSection.objects.get(name="History 1 MP only")

        Period.objects.bulk_create([
            Period(name="Homeroom (M)", start_time=datetime.time(8), end_time=datetime.time(8, 50)),
            Period(name="First Period", start_time=datetime.time(9), end_time=datetime.time(9, 50)),
            Period(name="Second Period", start_time=datetime.time(10), end_time=datetime.time(10, 50)),
        ])
        self.period = Period.objects.get(name="Homeroom (M)")

        CourseMeet.objects.bulk_create([
            CourseMeet(course_section_id=self.course_section.id, period=self.period, day="1"),
            CourseMeet(course_section_id=self.course_section3.id, period=self.period, day="2"),
        ])

        self.course_section1.marking_period.add(self.marking_period)
        self.course_section1.marking_period.add(self.marking_period2)
        self.course_section1.marking_period.add(self.marking_period3)
        self.course_section2.marking_period.add(self.marking_period)
        self.course_section2.marking_period.add(self.marking_period2)
        self.course_section2.marking_period.add(self.marking_period3)
        self.course_section4.marking_period.add(self.marking_period)

        self.enroll1 = CourseSectionTeacher.objects.create(course_section=self.course_section, teacher=self.teacher1)
        self.enroll2 = CourseSectionTeacher.objects.create(course_section=self.course_section3, teacher=self.teacher2)
        self.present = AttendanceStatus.objects.create(name="Present", code="P", teacher_selectable=True)
        self.absent = AttendanceStatus.objects.create(name="Absent", code="A", teacher_selectable=True, absent=True)
        self.excused = AttendanceStatus.objects.create(name="Absent Excused", code="AX", absent=True, excused=True)

        CourseEnrollment.objects.bulk_create([
            CourseEnrollment(user=self.student, course_section=self.course_section),
            CourseEnrollment(user=self.student, course_section=self.course_section2),
            CourseEnrollment(user=self.student, course_section=self.course_section4),
            CourseEnrollment(user=self.student2, course_section=self.course_section),
        ])
        self.course_enrollment = CourseEnrollment.objects.all().first()

        grade_data = [
            { 'student' : self.student2, 'section' : self.course_section2, 'mp' : self.marking_period, 'grade' : 75 },
            { 'student' : self.student2, 'section' : self.course_section, 'mp' : self.marking_period2, 'grade' : 100 },
            { 'student' : self.student3, 'section' : self.course_section, 'mp' : self.marking_period2, 'grade' : 88 },
        ]
        for x in grade_data:
            grade_object, created = Grade.objects.get_or_create(
                student = x['student'],
                course_section = x['section'],
                marking_period = x['mp']
                )
            grade_object.grade = x['grade']
            grade_object.save()

        self.grade = Grade.objects.all().first()
        build_grade_cache()

    def create_100_courses(self):
        for i in xrange(100):
            random_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            course = Course.objects.create(fullname="Math 101 " + random_string, shortname="Alg " + random_string, credits=1, graded=True)
            CourseSection.objects.create(name=course.shortname, course_id=course.id)

    def create_aa_superuser(self):
        aa = Faculty.objects.create(username="aa", first_name="aa", is_superuser=True, is_staff=True)
        aa.set_password('aa')
        aa.save()

    def create_admissions_choice_data(self):
        LanguageChoice.objects.create( name = "English" )
        EthnicityChoice.objects.create( name = "Hispanic/Latino" )
        HeardAboutUsOption.objects.create( name = "Radio" )
        ReligionChoice.objects.create( name = "Roman Catholic" )
        FeederSchool.objects.create( name = "Adamson Middle" )

    def create_balt_like_sample_data(self):
        self.create_required()
        self.create_course_types()
        self.create_courses()
        self.create_years_and_marking_periods()
        self.assign_marking_periods_to_course_sections()
        self.create_grade_scale_rules()
        self.create_sample_students()

    def create_course_types(self):
        CourseType.objects.create(name='NonCore', weight=0)
        self.non_core = CourseType.objects.get(name='NonCore')
        CourseType.objects.create(name='AP', weight=1, boost=1.0)
        self.ap = CourseType.objects.get(name='AP')
        CourseType.objects.create(name="Honors", weight = 1, boost = 0.5)
        self.honors = CourseType.objects.get(name="Honors")

    def create_courses(self):
        self.course1 = Course.objects.create(fullname="English", shortname="English", credits=1, course_type=self.ap, graded=True)
        self.course2 = Course.objects.create(fullname="Precalculus", shortname="Precalc", credits=1, graded=True)
        self.course3 = Course.objects.create(fullname="Physics", shortname="Phys", credits=1, graded=True)
        self.course4 = Course.objects.create(fullname="Modern World History", shortname="Hist", credits=1, graded=True)
        self.course5 = Course.objects.create(fullname="Spanish III", shortname="Span", credits=1, graded=True)
        self.course6 = Course.objects.create(fullname="Photojournalism", shortname="Photo", credits=1, course_type=self.non_core, graded=True)
        self.course7 = Course.objects.create(fullname="Faith & Justice", shortname="Faith", credits=1, graded=True)
        self.course8 = Course.objects.create(fullname="Writing Lab 12", shortname="Wrt Lab", credits=1, course_type=self.non_core, graded=True)
        self.course9 = Course.objects.create(fullname="English Honors", shortname="English-H", credits=1, course_type=self.honors, graded=True)
        self.course10 = Course.objects.create(fullname="Precalculus Honors", shortname="Precalc-H", credits=1, course_type=self.honors, graded=True)
        self.course11 = Course.objects.create(fullname="AP Modern World History", shortname="Hist-AP", credits=1, course_type=self.ap, graded=True)
        self.course12 = Course.objects.create(fullname="Spanish III AP", shortname="Span-AP", credits=1, graded=True, course_type=self.ap)
        self.course13 = Course.objects.create(fullname="Faith & Justice Honors", shortname="Faith-H", credits=1, graded=True, course_type=self.honors)

    def create_years_and_marking_periods(self):
        self.year = year = SchoolYear.objects.create(name="balt year", start_date=datetime.date(2014,7,1), end_date=datetime.date(2050,5,1), active_year=True)
        self.mp1 = MarkingPeriod.objects.create(name="1st", weight=0.4, start_date=datetime.date(2014,7,1), end_date=datetime.date(2014,9,1), school_year=year)
        self.mp2 = MarkingPeriod.objects.create(name="2nd", weight=0.4, start_date=datetime.date(2014,7,2), end_date=datetime.date(2014,9,2), school_year=year)
        self.mps1x = MarkingPeriod.objects.create(name="S1X", weight=0.2, start_date=datetime.date(2014,7,2), end_date=datetime.date(2014,9,2), school_year=year)
        self.mp3 = MarkingPeriod.objects.create(name="3rd", weight=0.4, start_date=datetime.date(2014,7,3), end_date=datetime.date(2014,9,3), school_year=year)
        self.mp4 = MarkingPeriod.objects.create(name="4th", weight=0.4, start_date=datetime.date(2014,7,4), end_date=datetime.date(2014,9,4), school_year=year)
        self.mps2x = MarkingPeriod.objects.create(name="S2X", weight=0.2, start_date=datetime.date(2014,7,4), end_date=datetime.date(2014,9,4), school_year=year)

    def assign_marking_periods_to_course_sections(self):
        courses = Course.objects.all()
        i = 0
        for course in courses:
            i += 1
            section = CourseSection.objects.create(name=course.shortname, course=course)
            setattr(self, 'course_section' + str(i), section)
            section.marking_period.add(self.mp1)
            section.marking_period.add(self.mp2)
            if course.credits > 0:
                section.marking_period.add(self.mps1x)
            section.marking_period.add(self.mp3)
            section.marking_period.add(self.mp4)
            if course.credits > 0:
                section.marking_period.add(self.mps2x)

    def create_grade_scale_rules(self):
        self.scale = scale = GradeScale.objects.create(name="Balt Test Scale")
        GradeScaleRule.objects.create(min_grade=0, max_grade=69.49, letter_grade='F', numeric_scale=0, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=69.50, max_grade=72.49, letter_grade='D', numeric_scale=1, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=72.50, max_grade=76.49, letter_grade='C', numeric_scale=2, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=76.50, max_grade=79.49, letter_grade='C+', numeric_scale=2.5, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=79.50, max_grade=82.49, letter_grade='B-', numeric_scale=2.7, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=82.50, max_grade=86.49, letter_grade='B', numeric_scale=3, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=86.50, max_grade=89.49, letter_grade='B+', numeric_scale=3.5, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=89.50, max_grade=92.49, letter_grade='A-', numeric_scale=3.7, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=92.50, max_grade=100, letter_grade='A', numeric_scale=4, grade_scale=scale)
        self.year.grade_scale = scale
        self.year.save()

    def create_sample_students(self):
        self.create_sample_normal_student()
        self.create_sample_honors_student()
        self.create_sample_honors_student_two()

    def create_sample_normal_student(self):
        self.student = Student.objects.create(first_name="Anon", last_name="Student", username="someone")
        shortname_list = ['English','Precalc','Phys','Hist','Span','Photo','Faith', 'Wrt Lab']
        self.enroll_student_in_sections(self.student, shortname_list)

        known_grades = [
            {'section': 'English',   'grades': [72.7, 77.5, 90,   66.5, 73.9, 79  ]},
            {'section': 'Precalc',   'grades': [55,   81.4, 68,   73.9, 77.2, 52 ]},
            {'section': 'Phys',      'grades': [69.1, 70.4, 61,   73.8, 72.3, 57 ]},
            {'section': 'Hist',      'grades': [92.4, 84.4, 84,   72.6, 89.1, 81 ]},
            {'section': 'Span',      'grades': [80.4, 72.1, 63,   74.4, 85.8, 80  ]},
            {'section': 'Photo',     'grades': [92.8, 93.6, None, 83.3, 90,   None ]},
            {'section': 'Faith',     'grades': [79.5, 83.1, 70,   78.3, 88.5, 82 ]},
            {'section': 'Wrt Lab',   'grades': [100,  100,  None, 100,  100,  None ]},
        ]

        self.populate_student_grades(self.student, known_grades)

        # There is an override grade for this student, so let's register that here
        Grade.objects.create(student=self.student, course_section=self.course_section3, override_final=True, grade=70)

    def create_sample_honors_student(self):
        # here we have an honors student
        self.honors_student = Student.objects.create(first_name="Snotty", last_name="McGillicuddy", username="snottymc")

        # let's enroll him in each one of these sections
        shortname_list = ['English-H', 'Precalc-H', 'Phys', 'Hist-AP', 'Span', 'Photo', 'Faith', 'Wrt Lab']
        self.enroll_student_in_sections(self.honors_student, shortname_list)

        # now assign these grades to our honors student
        # Format: {'section': name, 'grades': [1, 2, s1x, 3, 4, s2x]
        known_grades = [
            {'section': 'English-H',    'grades': [89.1, 90.1, 89,   83.4, 82.4, 84  ]},
            {'section': 'Precalc-H',    'grades': [95.9, 80.3, 80,   89.5, 77.8, 73  ]},
            {'section': 'Phys',         'grades': [93.2, 89.9, 92,   92.8, 90.4, None ]},
            {'section': 'Hist-AP',      'grades': [87.3, 78.7, 80,   81.1, 85,   None ]},
            {'section': 'Span',         'grades': [91.4, 88.6, 91,   88.1, 88,   71  ]},
            {'section': 'Photo',        'grades': [100,  95,   None, 97.8, 100,  None ]},
            {'section': 'Faith',        'grades': [88.1, 87.3, 88,   88.8, 91.5, None ]},
            {'section': 'Wrt Lab',      'grades': [100,  100,  None, 100,  100,  None ]},
        ]
        self.populate_student_grades(self.honors_student, known_grades)


    def create_sample_honors_student_two(self):
        self.sample_student1 = Student.objects.create(first_name="Price", last_name="Isright", username="priceisright")

        # let's enroll him in each one of these sections
        shortname_list = ['English', 'Precalc', 'Phys', 'Hist', 'Span-AP', 'Photo', 'Faith-H', 'Wrt Lab']
        self.enroll_student_in_sections(self.sample_student1, shortname_list)

        # now assign these grades to our honors student
        # Format: {'section': name, 'grades': [1, 2, s1x, 3, 4, s2x]
        known_grades = [
            {'section': 'English',  'grades': [95, 96, 89,   78, 87, 88  ]},
            {'section': 'Precalc',  'grades': [87, 78, 80,   89, 98, 88  ]},
            {'section': 'Phys',     'grades': [76, 88, 92,   88, 87, 94 ]},
            {'section': 'Hist',     'grades': [79, 90, 80,   76, 99, 90 ]},
            {'section': 'Span-AP',  'grades': [98, 87, 91,   98, 92, 67 ]},
            {'section': 'Photo',    'grades': [88,  98,  67, 84, 92,  90 ]},
            {'section': 'Faith-H',  'grades': [78, 88, 88,   98, 92, 90 ]},
            {'section': 'Wrt Lab',  'grades': [100,  100,  100, 100,  100, 100]},
        ]

        self.populate_student_grades(self.sample_student1, known_grades)

    def enroll_student_in_sections(self, student, shortname_list):
        """
        enroll the student in each section listed in the shortname_list
        """
        for shortname in shortname_list:
            section = CourseSection.objects.get(name=shortname)
            CourseEnrollment.objects.create(user=student, course_section=section)

    def populate_student_grades(self, student, grade_hash):
        """
        helper method for populating a bunch of student grades

        see examples above for syntax of the grade_hash
        """
        marking_periods = [self.mp1, self.mp2, self.mps1x, self.mp3, self.mp4, self.mps2x]
        for grd in grade_hash:
            section = CourseSection.objects.get(name=grd['section'])
            for i in range(6):
                grade = Grade.objects.get(
                    student = student,
                    course_section_id = section.id,
                    marking_period = marking_periods[i]
                    )
                grade.grade = grd['grades'][i]
                grade.save()


