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
from django.conf import settings

import urllib
from xml.etree import ElementTree as ET

class PythonEngrade:
    ### Configurations #########################################################
    # http://ww7.engrade.com/api/key.php
    apikey = settings.ENGRADE_APIKEY
    # Admin user login
    login = settings.ENGRADE_LOGIN
    # Engrade password
    password = settings.ENGRADE_PASSWORD
    # School UID (admin must be connected to school)
    schoolid = settings.ENGRADE_SCHOOLID
    ############################################################################
    url = 'https://api.engrade.com/api/'
    
    def __dict_to_element(self, values):
        try:
            params = urllib.urlencode(values, True)
            feed = urllib.urlopen(self.url, params)
            return ET.parse(feed)
        except:
            raise Exception("Unknown error: Engrade API did not return a result.")
    
    def __check_error(self, element):
        if element.find('success').text != 'true':
            error_elements = element.findall('errors')
            error_msg = ""
            for error_tag in error_elements:
                for error in error_tag.getchildren():
                    error_msg += "%s: %s \n" % (error.tag, error.text)
            raise Exception(error_msg,)
     
    def __init__(self):
        """ Login and get session from Engrade """
        values = {
            'apikey': self.apikey,
            'apitask': 'login',
            'usr': self.login,
            'pwd': self.password,
        }
        element = self.__dict_to_element(values)
        self.__check_error(element)
        self.ses = element.find('values/ses').text
        
    def school_class_new(self, name, syr, gp, students, priteach, code=None):
        """
        name = Name of the class
        syr = School year (2YYY or 2YYY-2YYY)
        gp = Grading period (1-9)
        students = list of students, one per line in format FirstName LastName IDNumber
        priteach = the UID of the primary teacher of the class (must be connected to school)
        Options:
        code = Class code (i.e. BIO101)
        returns engrade class id
        """
        values = {
            'apitask': 'school-class-add',
            'apikey': self.apikey,
            'ses': self.ses,
            'name': name,
            'syr': syr,
            'gp': gp,
            'students': students,
            'schoolid': self.schoolid,
            'priteach': priteach,
        }
        if code:
            values['code'] = code
        element = self.__dict_to_element(values)
        self.__check_error(element)
        return element.find('values/clid').text
        
    def class_students_edit(self, clid, students):
        """
        
        clid = Engrade Class ID
        students = list of students, one per line in format FirstName LastName IDNumber
        """
        values = {
            'apitask': 'class-students-edit',
            'apikey': self.apikey,
            'ses': self.ses,
            'students': students,
            'clid': clid,
        }
        if code:
            values['code'] = code
        element = self.__dict_to_element(values)
        self.__check_error(element)
        
    def school_teacher_new(self, teachers):
        """
        teachers = [['name1', 'email1'],['name2','email2']]
        Returns [[uid1,usr1,pwd1], etc]  // Engrade User ID, username, password
        """
        values = {
            'apitask': 'school-teacher-bulk',
            'apikey': self.apikey,
            'ses': self.ses,
            'schoolid': self.schoolid,
        }
        i = 1
        for teacher in teachers:
            values['name' + str(i)] = teacher[0]
            values['email' + str(i)] = teacher[1]
            i += 1 
        element = self.__dict_to_element(values)
        self.__check_error(element)
        en_teachers = []
        i = 0
        for teacher in teachers:
            en_teacher = []
            en_teacher.append(element.find('values/uid' + str(i)).text)
            en_teacher.append(element.find('values/usr' + str(i)).text)
            en_teacher.append(element.find('values/pwd' + str(i)).text)
            en_teachers.append(en_teacher)
            i += 1
        return en_teachers
        
    def school_teacher_email(self, emails):
        """
        emails = A list of teacher emails separated by whitespaces
        This feature will send an email to each teacher listed with instructions
        for either connecting their existing Engrade account to the school or to
        create a new Engrade teacher account that will be connected to the
        school's account.
        """
        values = {
            'apitask': 'school-teacher-email',
            'apikey': self.apikey,
            'ses': self.ses,
            'schoolid': self.schoolid,
            'emails': emails,
        }
        element = self.__dict_to_element(values)
        self.__check_error(element)
        # Currently returns nothing, doesn't work.
        #return element.find('values/tid').text
        
    def gradebook(self, clid):
        """
        clid = Engrade Class ID
        
        Returns:
        students = array of students ['stuid': student id, 'percent': grade percent']
        """
        values = {
            'apitask': 'gradebook',
            'apikey': self.apikey,
            'ses': self.ses,
            'clid': clid,
        }
        element = self.__dict_to_element(values)
        self.__check_error(element)
        students = []
        for elem_student in element.findall('students/item'):
            student = {}
            student['stuid'] = elem_student.find('stuid').text
            student['percent'] = elem_student.find('percent').text
            students.append(student)
        return students
    
    def class_comments(self, clid):
        """ Get comments for one class
        clid = Engrade Class ID
        
        Returns:
        students = array of students ['stuid': student id, 'percent': grade percent, 'comment': comment]
        """
        values = {
            'apitask': 'class-comments',
            'apikey': self.apikey,
            'ses': self.ses,
            'clid': clid,
        }
        element = self.__dict_to_element(values)
        self.__check_error(element)
        students = []
        for elem_student in element.findall('comments/item'):
            try:
                student = {}
                student['comment'] = elem_student.find('comment').text
                student['stuid'] = elem_student.find('stuid').text
                student['percent'] = elem_student.find('percent').text
                students.append(student)
            except:
                pass
        return students
    
    def class_students_email(self, clid, students):
        """ Get comments for one class
        clid = Engrade Class ID
        students  = Dict of student ids with email like
        {'1111': 'student@example.com,parent@example.com'}
        """
        values = {
            'apitask': 'class-students-email',
            'apikey': self.apikey,
            'ses': self.ses,
            'clid': clid,
        }
        for student, emails in students.iteritems():
            values['email_' + str(student)] = emails
        element = self.__dict_to_element(values)
        self.__check_error(element)