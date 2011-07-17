#       Copyright 2011 David M Burke <david@davidmburke.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from ecwsp.engrade_sync.python_engrade import *
from ecwsp.engrade_sync.models import *
from ecwsp.schedule.models import *

class EngradeSync:
    def __init__(self):
        """ Login and get session from Engrade """
        self.api = PythonEngrade()
        
    def get_engrade_teacher(self, teacher):
        """ Get an engrade teacher id, create if non existant
        teacher: sis.models.Faculty
        returns teacher's engrade id """
        teacher_sync = TeacherSync.objects.filter(teacher=teacher)
        if not teacher_sync.count():
            pass # Must figure out user creation first
        return teacher_sync[0].engrade_teacher_id 
        
    def get_engrade_course(self, course, marking_period):
        """ Get an engrade course id, create if non existant. Creates teacher if
        non existant.
        course: schedule.models.Course
        marking_period: unlike SWORD, engrade considers different marking
        periods as different courses
        returns engrade course id"""
        course_sync = CourseSync.objects.filter(course=course, marking_period=marking_period)
        if not course_sync.count():
            name = course.shortname
            syr = course.marking_period.all()[0].school_year.name
            # Figure out gp by determining the order in which the SWORD marking
            # periods occure
            gp = 0
            for mp in course.marking_period.order_by('start_date'):
                gp += 1
                if mp == marking_period:
                    break
            students = ""
            for student in course.get_enrolled_students():
                students += "%s %s %s\n" % (student.fname, student.lname, student.id)
            priteach = self.get_engrade_teacher(course.teacher)
            engrade_id = self.api.schoolclassnew(name, syr, gp, students, priteach)
            course_sync = CourseSync(course=course, marking_period=marking_period, engrade_course_id=engrade_id)
            course_sync.save()
        else:
            course_sync = course_sync[0]
        return course_sync.engrade_course_id
    
    def sync_course_grades(self, course, marking_period, include_comments):
        """ Loads grades from engrade into Course grades for particular marking period."""
        engrade_course = CourseSync.objects.get(course=course, marking_period=marking_period)
        students = self.api.gradebook(engrade_course.engrade_course_id)
        for engrade_student in students:
            student = Student.objects.get(id=engrade_student['stuid'])
            grade = engrade_student['percent']
            model, created = Grade.objects.get_or_create(student=student, course=course, marking_period=marking_period, final=True)
            model.set_grade(grade)
            model.save()
        if include_comments:
            students = self.api.class_comments(engrade_course.engrade_course_id)
            for engrade_student in students:
                student = Student.objects.get(id=engrade_student['stuid'])
                comment = engrade_student['comment']
                model, created = Grade.objects.get_or_create(student=student, course=course, marking_period=marking_period, final=True)
                model.comment = comment
                model.save()