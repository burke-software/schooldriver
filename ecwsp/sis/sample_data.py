# never import * except test data (because who cares about clean tests)
from ecwsp.sis.models import *
from ecwsp.attendance.models import *
from ecwsp.grades.models import *
from ecwsp.schedule.models import *

import random
import string
import logging
import datetime

class SisData(object):
    """ Put data creation code here. sample data code not here is punishible by death .
    """
    def create_all(self):
        """ This will populate all sample data """
        self.create_basics()

    def create_required(self):
        """ A place for 100% required data """
        self.normal_type = CourseType.build_default()

    def create_basics(self):
        """ A very simple school, probably want this in mosts tests
        Depends on create_required
        """
        # Run dependencies first
        self.create_required()

        # Use bulk create a few so it looks good in demo
        SchoolYear.objects.bulk_create([
            SchoolYear(name="2013-2014", start_date=datetime.date(2013,7,1), end_date=datetime.date(2014,5,1)),
            SchoolYear(name="2014-long time", start_date=datetime.date(2014,7,1), end_date=datetime.date(2050,5,1), active_year=True),
            SchoolYear(name="2015-16", start_date=datetime.date(2015,7,1), end_date=datetime.date(2016,5,1)),
        ])
        # Set one archetypal object. If I want a year I will use this
        self.school_year = SchoolYear.objects.get(active_year=True)

        # Note bulk does not call save() and other limitations
        # so it's ok to not use bulk
        # Don't change the order, other objects depend on the id being in this order
        self.student = Student.objects.create(first_name="Joe", last_name="Student", username="jstudent")
        self.student2 = Student.objects.create(first_name="Jane", last_name="Student", username="jastudent")
        self.student3 = Student.objects.create(first_name="Tim", last_name="Duck", username="tduck")
        Student.objects.create(first_name="Molly", last_name="Maltov", username="mmaltov")

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
            { 'student' : self.student2, 'section' : self.course_section, 'mp' : self.marking_period2, 'grade' : 100 },
        ]
        for x in grade_data:
            enrollment = CourseEnrollment.objects.get(
                user=x['student'], course_section=x['section'])
            grade_object, created = Grade.objects.get_or_create(
                enrollment = enrollment,
                marking_period = x['mp']
                )
            grade_object.grade = x['grade']
            grade_object.save()

        self.grade = Grade.objects.all().first()

    def create_100_courses(self):
        for i in xrange(100):
            random_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            course = Course.objects.create(fullname="Math 101 " + random_string, shortname="Alg " + random_string, credits=1, graded=True)
            section = CourseSection.objects.create(name=course.shortname, course_id=course.id)
    
    def create_30_student_grades(self):
        course_section = CourseSection.objects.all().first()
        for i in xrange(30):
            random_string = ''.join(
                random.choice(
                    string.ascii_uppercase + string.digits
                ) for _ in range(6))
            student = Student.objects.create(
                first_name=random_string[:5],
                last_name=random_string[:-5],
                username=random_string)
            enrollment = CourseEnrollment.objects.create(
                course_section=course_section,
                user=student,
            )
            for mp in MarkingPeriod.objects.all():
                grade = Grade(enrollment=enrollment, marking_period=mp)
                grade.set_grade(random.randint(0,100))
                grade.save()

    def create_grade_scale_data(self):
        self.create_required()
        aa = Faculty.objects.create(username="aa", first_name="aa", is_superuser=True, is_staff=True)
        aa.set_password('aa')
        aa.save()
        self.student = student = Student.objects.create(first_name="Anon", last_name="Student", username="someone")

        CourseType.objects.create(name='NonCore', weight=0)
        self.non_core = CourseType.objects.get(name='NonCore')
        CourseType.objects.create(name='AP', weight=1, boost=1.0)
        self.ap = CourseType.objects.get(name='AP')
        CourseType.objects.create(name="Honors", weight = 1, boost = 0.5)
        self.honors = CourseType.objects.get(name="Honors")

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
        self.course12 = Course.objects.create(fullname="Spanish III AP", shortname="Span-H", credits=1, graded=True, course_type=self.ap)
        self.course13 = Course.objects.create(fullname="Faith & Justice Honors", shortname="Faith-H", credits=1, graded=True, course_type=self.honors)

        self.year = year = SchoolYear.objects.create(name="balt year", start_date=datetime.date(2014,7,1), end_date=datetime.date(2050,5,1), active_year=True)
        self.mp1 = mp1 = MarkingPeriod.objects.create(name="1st", weight=0.4, start_date=datetime.date(2014,7,1), end_date=datetime.date(2014,9,1), school_year=year)
        self.mp2 = mp2 = MarkingPeriod.objects.create(name="2nd", weight=0.4, start_date=datetime.date(2014,7,2), end_date=datetime.date(2014,9,2), school_year=year)
        self.mps1x = mps1x = MarkingPeriod.objects.create(name="S1X", weight=0.2, start_date=datetime.date(2014,7,2), end_date=datetime.date(2014,9,2), school_year=year)
        self.mp3 = mp3 = MarkingPeriod.objects.create(name="3rd", weight=0.4, start_date=datetime.date(2014,7,3), end_date=datetime.date(2014,9,3), school_year=year)
        self.mp4 = mp4 = MarkingPeriod.objects.create(name="4th", weight=0.4, start_date=datetime.date(2014,7,4), end_date=datetime.date(2014,9,4), school_year=year)
        self.mps2x = mps2x = MarkingPeriod.objects.create(name="S2X", weight=0.2, start_date=datetime.date(2014,7,4), end_date=datetime.date(2014,9,4), school_year=year)

        courses = Course.objects.all()
        i = 0
        for course in courses:
            i += 1
            section = CourseSection.objects.create(name=course.shortname, course=course)
            setattr(self, 'course_section' + str(i), section)
            section.marking_period.add(mp1)
            section.marking_period.add(mp2)
            if course.credits > 0:
                section.marking_period.add(mps1x)
            section.marking_period.add(mp3)
            section.marking_period.add(mp4)
            if course.credits > 0:
                section.marking_period.add(mps2x)

            if course.shortname in ['English','Precalc','Phys','Hist','Span','Photo','Faith', 'Wrt Lab']:
                # only enroll self.student in these particular classes,
                # the other ones will be used for other students later on
                CourseEnrollment.objects.create(user=student, course_section=section)
        grade_data = [
            [1, mp1, 72.7],
            [1, mp2, 77.5],
            [1, mps1x, 90],
            [1, mp3, 66.5],
            [1, mp4, 73.9],
            [1, mps2x, 79],
            [2,mp1,55],
            [2,mp2,81.4],
            [2, mps1x, 68],
            [2,mp3,73.9],
            [2,mp4,77.2],
            [2, mps2x, 52],
            [3,mp1,69.1],
            [3,mp2,70.4],
            [3, mps1x, 61],
            [3,mp3,73.8],
            [3,mp4,72.3],
            [3, mps2x, 57],
            [4,mp1,92.4],
            [4,mp2,84.4],
            [4, mps1x, 84],
            [4,mp3,72.6],
            [4,mp4,89.1],
            [4, mps2x, 81],
            [5,mp1,80.4],
            [5,mp2,72.1],
            [5, mps1x, 63],
            [5,mp3,74.4],
            [5,mp4,85.8],
            [5, mps2x, 80],
            [6,mp1,92.8],
            [6,mp2,93.6],
            [6,mp3,83.3],
            [6,mp4,90],
            [7,mp1,79.5],
            [7,mp2,83.1],
            [7, mps1x, 70],
            [7,mp3,78.3],
            [7,mp4,88.5],
            [7, mps2x, 82 ],
            [8,mp1,100],
            [8,mp2,100],
            [8,mp3,100],
            [8,mp4,100],
        ]
        final_grade = FinalGrade(grade=70)
        final_grade.set_enrollment(student, self.course_section3)
        final_grade.save()
        for x in grade_data:
            enrollment = CourseEnrollment.objects.get(
                user=student,
                course_section=getattr(self, 'course_section' + str(x[0])))
            grade = Grade.objects.get_or_create(
                enrollment=enrollment, marking_period=x[1])[0]
            grade.grade = x[2]
            grade.save()
        self.grade = Grade.objects.all().first()
        scale = self.scale = GradeScale.objects.create(name="Balt Test Scale")
        GradeScaleRule.objects.create(min_grade=0, max_grade=69.49, letter_grade='F', numeric_scale=0, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=69.50, max_grade=72.49, letter_grade='D', numeric_scale=1, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=72.50, max_grade=76.49, letter_grade='C', numeric_scale=2, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=76.50, max_grade=79.49, letter_grade='C+', numeric_scale=2.5, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=79.50, max_grade=82.49, letter_grade='B-', numeric_scale=2.7, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=82.50, max_grade=86.49, letter_grade='B', numeric_scale=3, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=86.50, max_grade=89.49, letter_grade='B+', numeric_scale=3.5, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=89.50, max_grade=92.49, letter_grade='A-', numeric_scale=3.7, grade_scale=scale)
        GradeScaleRule.objects.create(min_grade=92.50, max_grade=100, letter_grade='A', numeric_scale=4, grade_scale=scale)
        year.grade_scale = scale
        year.save()

    def create_sample_honors_and_ap_data(self):
        """
        populate the gradebook with grades matching 'Report Car With Honors'
        depends on create_grade_scale_data() being called first
        """

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


    def create_sample_student_two(self):
        """
        just some more data that might be useful
        """
        #create a sample student
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
                enrollment = CourseEnrollment.objects.get(
                    user=self.honors_student,
                    course_section=section)
                grade = Grade.objects.get_or_create(
                    enrollment=enrollment,
                    marking_period=marking_periods[i])[0]
                grade.grade = grd['grades'][i]
                grade.save()

