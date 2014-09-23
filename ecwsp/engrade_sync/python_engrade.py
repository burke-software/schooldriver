from constance import config

import urllib
from xml.etree import ElementTree as ET

class PythonEngrade:
    ### Configurations #########################################################
    # http://ww7.engrade.com/api/key.php
    apikey = config.ENGRADE_APIKEY
    # Admin user login
    login = config.ENGRADE_LOGIN
    # Engrade password
    password = config.ENGRADE_PASSWORD
    # School UID (admin must be connected to school)
    schoolid = config.ENGRADE_SCHOOLID
    ############################################################################
    url = 'https://api.engrade.com/api/'

    def __dict_to_element(self, values, debug=False):
        try:
            params = urllib.urlencode(values, True)
            feed = urllib.urlopen(self.url, params)
            if debug:
                print feed.read()
                0/0
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
        i = 1
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

    def school_students_register(self, syr, gp, emails):
        """
        syr = The school year in which students have classes
        gp = The grading period in which students have classes
        email =
        email_STUID1 = The email address of the student with the student id STUID1
        email_STUID2 = The email address of the student with the student id STUID2
        ...

        Return Fields
        uid_STUID1 = The Engrade User ID for the student with the student id STUID1
        usr_STUID1 = The username for the student with the student id STUID1
        pwd_STUID1 = The password for the student with the student id STUID1
        ...

        This API call will create accounts for ALL students who DO have a class
        in the given grading period, but who do NOT yet have an account. Sending
        this call will create accounts for ALL such students whether you specify
        their email address or not. The email field is optional and, if specified,
        will allow Engrade to email the student the username and password that Engrade
        automatically generated for him/her.
        """
        values = {
            'apitask': 'sschool-students-register',
            'apikey': self.apikey,
            'ses': self.ses,
            'schoolid': self.schoolid,
            'emails': emails,
        }
        element = self.__dict_to_element(values)
        self.__check_error(element)


    def gradebook(self, clid):
        """
        clid = Engrade Class ID

        Returns:
        students = array of students ['stuid': student id, 'percent': grade percent', 'grade': Final grade (either percent or letter)]
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
            student['grade'] = elem_student.find('grade').text
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

    def school_students_register(self, syr, gp, students):
        """ This API call will create accounts for ALL students who DO have a class in the given grading period,
        but who do NOT yet have an account. Sending this call will create accounts for ALL such students whether
        you specify their email address or not. The email field is optional and, if specified, will allow Engrade
        to email the student the username and password that Engrade automatically generated for him/her.
        syr = The school year in which students have classes
        gp = The grading period in which students have classes
        students  = Dict of student ids with email like
        {'1111': 'student@example.com'}
        """
        values = {
            'apitask': 'school-students-register',
            'apikey': self.apikey,
            'ses': self.ses,
            'schoolid': self.schoolid,
            'syr': syr,
            'gp': gp,
        }
        for student, email in students.iteritems():
            values['email_' + str(student)] = email
        print values
        element = self.__dict_to_element(values, debug=True)
        self.__check_error(element)
        en_students = []
        for elem_student in element.findall('comments/item'):
            try:
                student = {}
                student['comment'] = elem_student.find('comment').text
                student['stuid'] = elem_student.find('stuid').text
                student['percent'] = elem_student.find('percent').text
                students.append(student)
            except:
                pass
        return en_students
