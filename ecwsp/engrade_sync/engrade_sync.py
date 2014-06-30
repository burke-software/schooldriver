from .python_engrade import *
from .models import *
from ecwsp.schedule.models import *
from ecwsp.grades.models import Grade

import sys
import datetime

class EngradeSync:
    def __init__(self):
        """ Login and get session from Engrade """
        self.api = PythonEngrade()
    
    def generate_all_teachers(self):
        """ Generates all teachers engrade accounts. Does not includes those who
        already have engrade accounts. Stores their engrade ID in teacher sync.
        returns number of new accounts """
        en_teachers = TeacherSync.objects.all()
        teachers = Faculty.objects.filter(teacher=True).exclude(id__in=en_teachers.values('teacher')).exclude(email="").exclude(fname="")
        new_teachers = []
        for teacher in teachers:
            new_teachers.append([teacher.fname + " " + teacher.lname, teacher.email])
        en_teachers = self.api.school_teacher_new(new_teachers)
        i = 0
        for teacher in teachers:
            TeacherSync.objects.create(
                teacher=teacher,
                engrade_teacher_id = en_teachers[i][0]
            )
            i += 1
        return i
        
    def get_engrade_teacher(self, teacher, create=False):
        """ Get an engrade teacher id, create if non existant
        teacher: sis.models.Faculty
        create: Create user if they don't exist. Send them an email.
        returns teacher's engrade id """
        teacher_sync = TeacherSync.objects.filter(teacher=teacher)
        if not teacher_sync.count() and create:
            teachers = [[teacher.fname + " " + teacher.lname, teacher.email]]
            en_teachers = self.api.school_teacher_new(teachers)
            TeacherSync.objects.create(
                teacher=teacher,
                engrade_teacher_id = en_teachers[0][0]
            )
        return teacher_sync[0].engrade_teacher_id 
    
    def generate_courses(self, marking_period):
        """
        Genererate all courses in Engrade for a given marking period.
        Returns list of engrade course id's
        """
        course_sections = CourseSection.objects.filter(marking_period=marking_period)
        course_ids = "" # from Engrade
        for course_section in course_sections:
            try:
                course_ids += unicode(self.get_engrade_course(course_section, marking_period)) + ", "
            except:
                course_ids += "Error creating %s, " % (course_section,)
        return course_ids
    
    def get_engrade_course(self, course_section, marking_period):
        """ Get an engrade course id, create if non existant. Creates teacher if
        non existant.
        course_section: schedule.models.CourseSection
        marking_period: unlike SWORD, engrade considers different marking
        periods as different courses
        returns engrade course id"""
        course_section_sync = CourseSectionSync.objects.filter(course_section=course_section, marking_period=marking_period)
        if not course_section_sync.exists():
            name = course_section.name
            syr = course_section.marking_period.all()[0].school_year.name
            # Figure out gp by determining the order in which the SWORD marking
            # periods occure
            gp = 0
            for mp in course_section.marking_period.order_by('start_date'):
                gp += 1
                if mp == marking_period:
                    break
            students = ""
            for student in Student.objects.filter(courseenrollment__course_section=course_section):
                students += "%s %s %s\n" % (student.fname, student.lname, student.id)
            priteach = self.get_engrade_teacher(course_section.teacher)
            engrade_id = self.api.school_class_new(name, syr, gp, students, priteach)
            course_section_sync = CourseSectionSync(course_section=course_section, marking_period=marking_period, engrade_course_id=engrade_id)
            course_section_sync.save()
        else:
            course_section_sync = course_section_sync[0]
        return course_section_sync.engrade_course_id
    
    def sync_course_grades(self, course_section, marking_period, include_comments):
        """ Loads grades from engrade into CourseSection grades for particular marking period.
        Returns: list of errors """
        try:
            engrade_course = CourseSectionSync.objects.get(course_section=course_section, marking_period=marking_period)
        except CourseSectionSync.DoesNotExist:
            return "%s does not exist in engrade. " % (course_section,)
        students = self.api.gradebook(engrade_course.engrade_course_id)
        errors = ""
        for engrade_student in students:
            try:
                student = None
                student = Student.objects.get(id=engrade_student['stuid'])
                grade = engrade_student['grade']
                model, created = Grade.objects.get_or_create(student=student, course_section=course_section, marking_period=marking_period)
                model.set_grade(grade)
                model.save()
            except:
                if student:
                    errors += '%s: %s\'s grade not set! ' % (course_section,student,)
                else:
                    errors += "%s: Student doesn't exist! " % (course_section,)
                print >> sys.stderr, "ENGRADE_SYNC:" + unicode(sys.exc_info()[0]) + unicode(sys.exc_info()[1])
        if include_comments:
            students = self.api.class_comments(engrade_course.engrade_course_id)
            for engrade_student in students:
                try:
                    student = None
                    student = Student.objects.get(id=engrade_student['stuid'])
                    comment = engrade_student['comment']
                    model, created = Grade.objects.get_or_create(student=student, course_section=course_section, marking_period=marking_period)
                    model.comment = comment
                    model.save()
                except:
                    if student:
                        errors += '%s: %s\'s comment not set! ' % (course_section,student,)
                    else:
                        errors += "%s: Student doesn't exist! " % (course_section,)
                    print >> sys.stderr, "ENGRADE_SYNC:" + unicode(sys.exc_info()[0]) + unicode(sys.exc_info()[1])
        course_section.last_grade_submission = datetime.datetime.now()
        course_section.save()
        return errors
