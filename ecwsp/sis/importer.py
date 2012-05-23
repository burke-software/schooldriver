#       import.py
#       
#       Copyright 2010-2012 Burke Software and Consulting
#       Author David M Burke <david@burkesoftware.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
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
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.db import transaction

from ecwsp.admissions.models import *
from ecwsp.sis.models import *
from ecwsp.schedule.models import *
from ecwsp.sis.xlsReport import *
from ecwsp.sis.uno_report import *
from ecwsp.attendance.models import *

import xlrd
import re
from heapq import merge
from datetime import time
import datetime
import sys
from decimal import *
import subprocess

class Importer:
    def __init__(self, file=None, user=None):
        """Opens file. If not xls, convert to xls using uno
        supports any file Openoffice.org supports"""
        if file:
            self.file = file
            if file.name[-3:] == "xls":
                self.book = xlrd.open_workbook(file_contents=file.read())
            else: # convert to xls
                destination = open('/tmp/' + file.name, 'wb+')
                destination.write(file.read())
                destination.close()
                document = uno_open('/tmp/' + str(file.name))
                tmp, filename, content = uno_save(document, file.name, "xls")
                self.book = xlrd.open_workbook(tmp.name)
            self.error_data = {}
            self.error_titles = {}
            self.errors = 0
            self.user = user
    
    def do_mysql_backup(self, database='default'):
        args = []
        database = settings.DATABASES[database]
        if 'USER' in database:
            args += ["--user=%s" % database['USER']]
        if 'PASSWORD' in database:
            args += ["--password=%s" % database['PASSWORD']]
        if 'HOSTNAME' in database:
            args += ["--host=%s" % database['HOSTNAME']]
        if 'PORT' in database and database['PORT']:
            args += ["--port=%s" % database['PORT']]
        args += [database['NAME']]
        
        #below is only available in python 2.7. Until I have time to talk with David about updating the server, using older coding
        #mysql_as_string = subprocess.check_output('mysqldump %s' % (' '.join(args),),shell=True)        
        mysql_as_string = subprocess.Popen('mysqldump %s' % (' '.join(args),),shell=True).communicate()[0]
        return ContentFile(mysql_as_string)
        
    def make_log_entry(self, user_note=""):
        self.log = ImportLog(user=self.user, user_note=user_note, import_file=self.file)
        file_name = datetime.datetime.now().strftime("%Y%m%d%H%M") + ".sql"
        if settings.BASE_URL != 'http://localhost:8000':
            self.log.sql_backup.save(file_name, self.do_mysql_backup())
        self.log.save()
        # Clean up old log files
        for import_log in ImportLog.objects.filter(date__lt=datetime.datetime.now() - datetime.timedelta(60)):
            import_log.delete()
        
    def handle_error(self, row, colname, exc, name):
        """ Add error infomation to exception list and error_date which will be
        transfered to html and a xls file. Also print to stderr. """
        transaction.rollback()
        if not hasattr(colname, "value") or colname.value:
            value_row = []
            for cell in row:
                value_row += [cell.value]
            error = "Error at: " + str(colname) + " " + unicode(exc[0]) + unicode(exc[1])
            value_row += [error]
            self.error_data[name] += [value_row]
            self.errors += 1
    
    def sanitize_item(self, name, value):
        """ Checks to make sure column and cell have data, if not ignore them
        Returns true is valid data """
        if value and value.value != "" and name and name.value != "":
            name = unicode.lower(unicode(name.value))
            value = value.value
            if type(value) is float:
                value = str(value).rstrip('0').rstrip('.')
            return True, name, value
        return False, name, value
    
    def gen_username(self, fname, lname):
        """Generate a unique username for a MdlUser based on first and last name
        Try first the first letter of the first name plus the last name
        if fail, try adding more letters of the first name
        if fail, add an incrementing number to the end.
        This function should always find a name and never fail except in
        absurd scenarios with many users and limited varchar space
        """
        # We have to kill blanks now; consider a stupid case like fname=" Joe" lname="Student"
        # username would end up being just "student", which is no bueno
        fname = "".join(fname.split());
        lname = "".join(lname.split());
        try:
            i = 1
            username = unicode(fname[:i]) + unicode(lname)
            while MdlUser.objects.filter(username=username).count() > 0:
                i += 1
                username = unicode(fname[:i]) + unicode(lname)
                if username == "": raise UsernameError
        except:
            number = 1
            username = unicode(fname[:i]) + unicode(lname) + unicode(number)
            while MdlUser.objects.filter(username=username).count() > 0:
                number += 1
                username = unicode(fname[:i]) + unicode(lname) + unicode(number)
        return unicode.lower(username)
    
    def import_number(self, value):
        phonePattern = re.compile(r'''
                    # don't match beginning of string, number can start anywhere
        (\d{3})     # area code is 3 digits (e.g. '800')
        \D*         # optional separator is any number of non-digits
        (\d{3})     # trunk is 3 digits (e.g. '555')
        \D*         # optional separator
        (\d{4})     # rest of number is 4 digits (e.g. '1212')
        \D*         # optional separator
        (\d*)       # extension is optional and can be any number of digits
        $           # end of string
        ''', re.VERBOSE)
        a, b, c, ext = phonePattern.search(value).groups()
        if ext == "0000":
            ext = ""
        return a + "-" + b + "-" + c, ext
    
    def convert_date(self, value):
        """Tries to convert various ways of storing a date to a python date"""
        try:
            return datetime.datetime.strptime(str(value), "%Y-%m-%d")
        except: pass
        try:
            return datetime.datetime.strptime(str(value), "%m-%d-%Y")
        except: pass
        try:
            return date(*(xlrd.xldate_as_tuple(float(value), 0)[0:3]))
        except: pass
        try:
            return datetime.datetime.strptime(str(value), "%Y%m%d")
        except: pass
        try:
            date_split = value.split("-")
            return datetime.datetime.strptime(str(date_split[0] + "-" +date_split[1]), "%Y-%m")
        except: pass
        return None
    
    def get_student(self, items, allow_none=False, try_secondary=False):
        """ Lookup a student based on id, unique id, username, or ssn
        items: name and value from the imported data
        allow_none: Allow not finding a student. If False an exceptions
        try_secondary: 
        is reaised if the student isn't found. default False"""
        for (name, value) in items:
            is_ok, name, value = self.sanitize_item(name, value)
            if is_ok:
                if name == "student id":
                    return Student.objects.get(id=value)
                elif name == "student unique id":
                    return Student.objects.get(unique_id=value)
                elif name == "hs_student_id": # Naviance
                    try:
                        return Student.objects.get(unique_id=value)
                    except:
                        return Student.objects.get(id=value)
                elif name == "student username":
                    return Student.objects.get(username=value)
                elif name == "ssn" or name == "social security number" or name == "student ssn":
                    ssn = str(value).translate(None, '- _') # Because student clearing house likes stray _
                    ssn = ssn[:3] + '-' + ssn[3:5] + '-' + ssn[-4:] # xxx-xx-xxxx
                    return Student.objects.get(ssn=ssn)
        
        # No ID....try secondary keys.
        if try_secondary:
            fname = None
            lname = None
            mname = None
            address = None
            for (name, value) in items:
                is_ok, name, value = self.sanitize_item(name, value)
                if is_ok:
                    if name in ['first name','first_name','fname']:
                        fname = value
                    elif name in ['last name','last_name','lname']:
                        lname = value
                    elif name in ['middle name','middle_name','mname']:
                        mname = value
                    elif name in ['address','street address', 'street_address']:
                        address = value
            if fname and lname:
                if mname:
                    if Student.objects.filter(fname=fname,lname=lname,mname=mname).count() == 1:
                        return Student.objects.get(fname=fname,lname=lname,mname=mname)
                if address:
                    if Student.objects.filter(fname=fname,lname=lname,address=address).count() == 1:
                        return Student.objects.get(fname=fname,lname=lname,address=address)
                if Student.objects.filter(fname=fname,lname=lname).count() == 1:
                    return Student.objects.get(fname=fname,lname=lname)
        
        if not allow_none:
            raise Exception("Could not find student, check unique id, username, or id")
    
    def convert_day(self, value):
        """ Converts day of week to ISO day of week number
        Ex: Monday returns 1"""
        value = unicode.lower(unicode(value))
        if value == "monday" or value == "m": return 1
        elif value == "tuesday" or value == "t": return 2
        elif value == "wednesday" or value == "w": return 3
        elif value == "thursday" or value == "th": return 4
        elif value == "friday" or value == "f": return 5
        elif value == "saturday" or value == "sat": return 6
        elif value == "sunday" or value == "sun": return 7
        else: return value
    
    def convert_time(self, value):
        """Tries to convert various ways of storing a date to a python time
        Includes excel date format"""
        pdate = None
        try:
            pdate = datetime.strptime(str(value), "%H-%M-%S")
        except:
            pdate = time(*(xlrd.xldate_as_tuple(float(value), 0)[3:]))
        return pdate
    
    def determine_truth(self, value):
        value = unicode(value)
        value = unicode.lower(value)
        if value == "true" or value == "yes" or value == "y" or value == True or value == 1 or value == "1" or value == "1.0":
            return True
        else:
            return False
    
    def log_and_commit(self, object, inserted=None, updated=None, addition=True):
        if addition:
            LogEntry.objects.log_action(
                user_id         = self.user.pk, 
                content_type_id = ContentType.objects.get_for_model(object).pk,
                object_id       = object.pk,
                object_repr     = unicode(object), 
                action_flag     = ADDITION
            )
            if inserted != None:
                inserted += 1
        else:
            LogEntry.objects.log_action(
                user_id         = self.user.pk, 
                content_type_id = ContentType.objects.get_for_model(object).pk,
                object_id       = object.pk,
                object_repr     = unicode(object), 
                action_flag     = CHANGE
            )
            if updated != None:
                updated += 1
        transaction.commit()
        return inserted, updated
    
    def import_prep(self, sheet):
        x = 0
        header = sheet.row(x)
        x += 1
        inserted = 0
        updated = 0
        header_values = []
        for cell in header:
            header_values += [cell.value]
        header_values += ['Error']
        self.error_titles[sheet.name] = [header_values]
        self.error_data[sheet.name] = []
        return (x, header, inserted, updated)
    
    def get_sheet_by_case_insensitive_name(self, name):
        """ Use xlrd to get a sheet, but ignore case! """
        i = 0
        for sheet_name in self.book.sheet_names():
            if sheet_name.lower() == name.lower():
                return self.book.sheet_by_index(i)
            i += 1
    
    def magic_import_everything(self):
        """Import a workbook using sheet names to determine what to import"""
        self.make_log_entry()
        inserted = 0
        updated = 0
        msg = ""
        
        sheet = self.get_sheet_by_case_insensitive_name("students")
        if sheet:
            inserted, updated = self.import_students(sheet)
            msg += "%s students inserted, %s students updated. <br/>" % (inserted, updated)
        sheet = self.get_sheet_by_case_insensitive_name("emergency contact")
        if sheet:
            inserted, updated = self.import_emergency_contacts(sheet)
            msg += "%s emergency contacts inserted, %s emergency contacts updated. <br/>" % (inserted, updated)
        sheet = self.get_sheet_by_case_insensitive_name("faculty")
        if sheet:
            inserted, updated = self.import_faculty(sheet)
            msg += "%s faculty inserted, %s faculty updated. <br/>" % (inserted, updated)
        sheet = self.get_sheet_by_case_insensitive_name("attendance")
        if sheet:
            inserted = self.import_attendance(sheet)
            msg += "%s attendance records inserted. <br/>" % (inserted)
        sheet = self.get_sheet_by_case_insensitive_name("discipline")
        if sheet:
            inserted = self.import_discipline(sheet)
            msg += "%s discipline records inserted. <br/>" % (inserted)
        sheet = self.get_sheet_by_case_insensitive_name("school year")
        if sheet:
            inserted = self.import_year(sheet)
            msg += "%s year records inserted. <br/>" % (inserted)
        sheet = self.get_sheet_by_case_insensitive_name("marking period")
        if sheet:
            inserted = self.import_mp(sheet)
            msg += "%s marking period records inserted. <br/>" % (inserted)
        sheet = self.get_sheet_by_case_insensitive_name("days off")
        if sheet:
            inserted = self.import_days_off(sheet)
            msg += "%s days off records inserted. <br/>" % (inserted)
        sheet = self.get_sheet_by_case_insensitive_name("period")
        if sheet:
            inserted, updated = self.import_period(sheet)
            msg += "%s period records inserted. %s period records updated.<br/>" % (inserted, updated)
        sheet = self.get_sheet_by_case_insensitive_name("cohort")
        if sheet:
            inserted = self.import_cohort(sheet)
            msg += "%s cohort records inserted. <br/>" % (inserted)
        sheet = self.get_sheet_by_case_insensitive_name("course")
        if sheet:
            inserted, updated = self.import_course(sheet)
            msg += "%s course records inserted and %s updated. <br/>" % (inserted, updated)
        sheet = self.get_sheet_by_case_insensitive_name("course enrollment")
        if sheet:
            inserted = self.import_course_enrollment(sheet)
            msg += "%s course enrollment records inserted. <br/>" % (inserted)
        sheet = self.get_sheet_by_case_insensitive_name("grade")
        if sheet:
            inserted, updated = self.import_grades_admin(sheet)
            msg += "%s grades inserted, %s grades updated. <br/>" % (inserted, updated)
        sheet = self.get_sheet_by_case_insensitive_name("grade comments")
        if sheet:
            inserted, updated = self.import_grades_comment(sheet)
            msg += "%s grades comments inserted, %s grades comments updated. <br/>" % (inserted, updated)
        sheet = self.get_sheet_by_case_insensitive_name("standard test")
        if sheet:
            inserted = self.import_standard_test(sheet)
            msg += "%s standard tests inserted <br/>" % (inserted)
        sheet = self.get_sheet_by_case_insensitive_name("course meet")
        if sheet:
            inserted, updated = self.import_course_meet(sheet)
            msg += "%s course meets inserted, %s course meets updated. <br/>" % (inserted, updated)
        sheet = self.get_sheet_by_case_insensitive_name("workteam")
        if sheet:
            inserted, updated = self.import_workteams(sheet)
            msg += "%s workteams inserted, %s workteams updated. <br/>" % (inserted, updated)
        sheet = self.get_sheet_by_case_insensitive_name("student worker")
        if sheet:
            inserted, updated = self.import_student_workers(sheet)
            msg += "%s workers inserted, %s workers updated. <br/>" % (inserted, updated)
        sheet = self.get_sheet_by_case_insensitive_name("company contact")
        if sheet:
            inserted, updated = self.import_company_contacts(sheet)
            msg += "%s company contacts inserted, %s company contacts updated. <br/>" % (inserted, updated)
        sheet = self.get_sheet_by_case_insensitive_name("applicant")
        if sheet:
            inserted, updated = self.import_applicants(sheet)
            msg += "%s applicants inserted, %s applicants updated <br/>" % (inserted, updated)
        sheet = self.get_sheet_by_case_insensitive_name("adm checks")
        if sheet:
            inserted, updated = self.import_admissions_checks(sheet)
            msg += "%s admission checks inserted,<br/>" % (inserted,)
        sheet = self.get_sheet_by_case_insensitive_name("adm log")
        if sheet:
            inserted, updated = self.import_admissions_log(sheet)
            msg += "%s admission contact log entries inserted,<br/>" % (inserted,)
        sheet = self.get_sheet_by_case_insensitive_name("alumni note")
        if sheet:
            inserted, updated = self.import_alumni_note(sheet)
            msg += "%s alumni note entries inserted,<br/>" % (inserted,) 
        sheet = self.get_sheet_by_case_insensitive_name("college enrollment")
        if sheet:
            inserted, updated = self.import_college_enrollment(sheet)
            msg += "%s college enrollments inserted, %s college enrollments updated. <br/>" % (inserted, updated)
        sheet = self.get_sheet_by_case_insensitive_name("benchmarks")
        if sheet:
            inserted, updated = self.import_benchmarks(sheet)
            msg += "%s benchmarks inserted, %s benchmarks updated <br/>" % (inserted, updated)
        sheet = self.get_sheet_by_case_insensitive_name("company contract")
        if sheet:
            inserted, updated = self.import_contract_information(sheet)
            msg += "%s contracts inserted, %s contracts updated <br/>" % (inserted, updated)
        
        if msg == "":
            msg = "No files found. Check if sheets are named correctly. "
        
        msg += unicode(self.errors) + " error(s). "
        
        filename = 'import_error.xls'
        if len(self.error_data):
            self.log.errors = True
            self.log.save()
            report = customXls("")
            save = False
            for key, error_page in self.error_data.items():
                if len(error_page):
                    save = True
                    report.addSheet(error_page, self.error_titles[key][0], heading=key, heading_top=False)
            if save:
                report.save(filename)
            else:
                filename = None
        return msg, filename
    
    def import_just_standard_test(self, test=None):
        inserted = 0
        msg = ""
        try:
            sheet = self.book.sheet_by_index(0) # Just get the first one
            inserted = self.import_standard_test(sheet, test)
            msg += "%s standard tests inserted <br/>" % (inserted)
        except: pass
        
        if msg == "":
            msg = "No files found. Check if sheets are named correctly. "
        
        msg += unicode(self.errors) + " error(s). "
        
        filename = 'import_error.xls'
        if len(self.error_data):
            report = customXls("")
            save = False
            for key, error_page in self.error_data.items():
                if len(error_page):
                    save = True
                    report.addSheet(error_page, self.error_titles[key][0], heading=key, heading_top=False)
            if save:
                report.save(filename)
            else:
                filename = None
        return msg, filename
    
    def import_benchmarks(self, sheet, test=None):
        """Import Standardized tests. Does not allow updates.
        test: if the test named is already known. """
        from ecwsp.omr.models import Benchmark, MeasurementTopic
        from ecwsp.omr.models import Department as omrDepartment
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = False
                    topic = b_name = number = year = measurement_topic_description = measurement_topic_department = None
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "benchmark":
                                b_name = value
                            elif name == "number":
                                number = value
                            elif name == "year":
                                year = value
                            elif name in ["measurement_topics", "measurement topic", "measurement topics"]:
                                topic = value
                            elif name in ["measurement_topics description", "measurement topic description", "measurement topics description"]:
                                measurement_topic_description = value
                            elif name in ["measurement_topics department", "measurement topic department", "measurement topics department"]:
                                measurement_topic_department = value
                    if measurement_topic_department:
                        measurement_topic_department = omrDepartment.objects.get_or_create(name=measurement_topic_department)[0]
                    if topic:
                        # Secondary key for measurement topic is department + name.
                        if measurement_topic_department == "":
                            measurement_topic_department = None
                        topic = MeasurementTopic.objects.get_or_create(name=topic, department=measurement_topic_department)[0]
                    if measurement_topic_description and topic:
                        topic.description = measurement_topic_description
                        topic.save()
                    if measurement_topic_department and topic:
                        topic.department = measurement_topic_department
                        topic.save()
                    model, created = Benchmark.objects.get_or_create(number=number, name=b_name)
                    #if number and Benchmark.objects.filter(number=number).count():
                    #    model = Benchmark.objects.filter(number=number)[0]
                    #else:
                    #    model = Benchmark(number=number)
                    #    created = True
                    if year:
                        try:
                            model.year = GradeLevel.objects.get(name=year)
                        except:
                            model.year = GradeLevel.objects.get(id=year)
                    model.full_clean()
                    model.save()
                    model.measurement_topics.add(topic)
                    self.log_and_commit(model, addition=created)
                    if created:
                        inserted += 1
                    else:
                        updated += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted, updated
    
    def import_standard_test(self, sheet, known_test=None):
        """Import Standardized tests. Does not allow updates.
        test: if the test named is already known. """
        x, header, inserted, updated = self.import_prep(sheet)
        test = known_test
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = False
                    model = StandardTestResult()
                    is_plan = False
                    test = None
                    if known_test:
                        test = known_test
                        model.test = test
                    model.student = self.get_student(items)
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "test name":
                                test, created = StandardTest.objects.get_or_create(name=value)
                                model.test = test
                            elif name in ["date","test_date","test date"]:
                                model.date = self.convert_date(value)
                            elif name == "is_plan":
                                is_plan = self.determine_truth(value)
                                if is_plan:
                                    test = StandardTest.objects.get_or_create(name="PLAN")
                                    model.test = test
                            elif name[:9] == "category ":
                                model.save()
                                category, created = StandardCategory.objects.get_or_create(name=name[9:], test=test)
                                grade, created = StandardCategoryGrade.objects.get_or_create(category=category, result=model, grade=value)
                            elif name in ["verbal", "math", "writing", "english", "reading", "science", "composite"]: # Naviance
                                model.save()
                                category = StandardCategory.objects.get_or_create(name=name, test=test)[0]
                                grade = StandardCategoryGrade.objects.get_or_create(category=category, result=model, grade=value)[0]
                            elif name in ["show_on_reports","show on reports","show on report"]:
                                model.show_on_reports = self.determine_truth(value)
                    model.full_clean()
                    model.save()
                    self.log_and_commit(model, addition=True)
                    inserted += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted
    
    def import_alumni_note(self, sheet):
        from ecwsp.alumni.models import Alumni, AlumniNote, AlumniNoteCategory
        x, header, inserted, updated = self.import_prep(sheet)
        name = None
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    student = self.get_student(items,try_secondary=True)
                    category = note = date = user = None
                    if hasattr(student, 'alumni'):
                        alumni = student.alumni
                    else:
                        alumni = Alumni(student=student)
                        alumni.save()
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "category":
                                category = AlumniNoteCategory.objects.get_or_create(name=value)[0]
                            elif name == "note":
                                note = value
                            elif name == "date":
                                date = self.convert_date(value)
                            elif name == "user":
                                user = User.objects.get(username=value)
                    note, created = AlumniNote.objects.get_or_create(
                        alumni=alumni,
                        category=category,
                        note=note,
                        date=date,
                        user=user,
                    )
                    if created:
                        self.log_and_commit(note, addition=created)
                        inserted += 1
                            
                except:
                    if hasattr(sheet, 'name'):
                        self.handle_error(row, name, sys.exc_info(), sheet.name)
                    else:
                        self.handle_error(row, name, sys.exc_info(), "Unknown")
            x += 1
        return inserted, updated
    
    def import_college_enrollment(self, sheet):
        from ecwsp.alumni.models import Alumni, College, CollegeEnrollment
        x, header, inserted, updated = self.import_prep(sheet)
        name = None
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    student = self.get_student(items,try_secondary=True)
                    search_date = code = college_name = state = year = type = begin = end = None
                    status = graduated = graduation_date = degree_title = major = record_found = None
                    if hasattr(student, 'alumni'):
                        alumni = student.alumni
                        alumni_created = False
                    else:
                        alumni = Alumni(student=student)
                        alumni.save()
                        alumni_created = True
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "search date":
                                search_date = self.convert_date(value)
                            elif name in ["college code", 'college code/branch','college_code/branch']:
                                code = value
                            elif name in ['name', 'college name','college_name']:
                                college_name = value
                            elif name in ['state', 'college state', 'college_state']:
                                state = value
                            elif name in ['year', '2-year/4-year', '2-year / 4-year']:
                                if value == "4-year": value = "4"
                                elif value == "2-year": value = "2"
                                year = value
                            elif name in ['type', 'public/private', 'public / private']:
                                type = value
                            elif name in ['begin', 'enrollment begin','enrollment_begin']:
                                begin = self.convert_date(value)
                            elif name in ['end', 'enrollment end','enrollment_end']:
                                end = self.convert_date(value)
                            elif name in ['status', 'enrollment status','enrollment_status']:
                                status = value.strip()
                            elif name in ['graduated', 'graduated?']:
                                graduated = self.determine_truth(value)
                            elif name in ['graduation date', 'graduation_date']:
                                graduation_date = self.convert_date(value)
                            elif name in ['degree_title', 'degree title']:
                                degree_title = value
                            elif name in ['major']:
                                major = value
                            elif name in ['record_found', 'record_found_y/n']:
                                record_found = self.determine_truth(value)
                                
                    if record_found:
                        # First get or create college
                        college, c_created = College.objects.get_or_create(code=code)
                        if c_created:
                            college.name = college_name
                            college.state = state
                            college.type = type
                            college.save()
                        if not graduated and begin:
                        # Get or create enrollment based on secondary key
                            model, created = CollegeEnrollment.objects.get_or_create(
                                college=college,
                                program_years=year,
                                begin=begin,
                                end=end,
                                status=status,
                                alumni=alumni,
                            )
                            model.search_date = search_date
                            model.graduated = graduated
                            model.graduation_date = graduation_date
                            model.degree_title = degree_title
                            model.major = major
                        
                            model.full_clean()
                            model.save()
                            self.log_and_commit(model, addition=created)
                            if created:
                                inserted += 1
                            else:
                                updated += 1
                        elif not alumni.college_override:
                            # Graduated but no enrollment data
                            alumni.graduated  = graduated
                            alumni.graduation_date = graduation_date
                            if not alumni.college:
                                alumni.college = college
                            alumni.full_clean()
                            alumni.save()
                            self.log_and_commit(alumni, addition=alumni_created)
                            if alumni_created:
                                inserted += 1
                            else:
                                updated += 1
                    else:
                        self.log_and_commit(alumni, addition=alumni_created)
                        if alumni_created:
                            inserted += 1
                        else:
                            updated += 1
                except:
                    if hasattr(sheet, 'name'):
                        self.handle_error(row, name, sys.exc_info(), sheet.name)
                    else:
                        self.handle_error(row, name, sys.exc_info(), "Unknown")
            x += 1
        return inserted, updated
    
    def import_cohort(self, sheet):
        """Import cohorts. Does not allow updates. """
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = False
                    model = None
                    student = model.student = self.get_student(items)
                    student_cohort = None
                    
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "cohort name":
                                model, created = Cohort.objects.get_or_create(name=value)
                                if created: model.save()
                            elif name == "primary":
                                if self.determine_truth(value):
                                    try:
                                        student_cohort = StudentCohort.objects.get(student=student, cohort=model)
                                        student_cohort.primary = True
                                    except: pass
                    model.students.add(student)
                    model.full_clean()
                    model.save()
                    if student_cohort: student_cohort.save()
                    self.log_and_commit(model, addition=True)
                    inserted += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted
    
    #@transaction.commit_manually
    def import_course_enrollment(self, sheet):
        """Import course enrollments. Does not allow updates. """
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = False
                    model = CourseEnrollment()
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "course":
                                model.course = Course.objects.get(fullname=value)
                            elif name == "user":
                                try:
                                    model.user = MdlUser.objects.get(username=value)
                                except:
                                    try:
                                        model.user = MdlUser.objects.get(id=value)
                                    except:
                                        model.user = MdlUser.objects.get(unique_id=value)
                            elif name == "role":
                                model.role = unicode(value)
                            elif name == "year":
                                try:
                                    model.year = GradeLevel.objects.get(name=value)
                                except: pass
                                model.year = GradeLevel.objects.get(id=value)
                    model.full_clean()
                    model.save()
                    self.log_and_commit(model, addition=True)
                    inserted += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted
    
    #@transaction.commit_manually
    def import_faculty(self, sheet):
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    model = None
                    created = False
                    comment = ""
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "username":
                                model, created = Faculty.objects.get_or_create(username=value)
                            elif name == "first name":
                                model.fname = value
                            elif name == "last name":
                                model.lname = value
                            elif name == "is teacher":
                                model.teacher = self.determine_truth(value)
                    model.save()
                    if created:
                        self.log_and_commit(model, addition=True)
                        inserted += 1
                    else:
                        self.log_and_commit(model, addition=False)
                        updated += 1 
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted, updated
    
    #@transaction.commit_manually
    def import_grades_comment(self, sheet):
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    model = None
                    created = False
                    comment = ""
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "id":
                                model, created = GradeComment.objects.get_or_create(id=value)
                            elif name == "comment":
                                model.comment = value
                    model.save()
                    if created:
                        self.log_and_commit(model, addition=True)
                        inserted += 1
                    else:
                        self.log_and_commit(model, addition=False)
                        updated += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted, updated
    
    def import_grades_admin(self, sheet):
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = False
                    grade = None
                    letter_grade = None
                    student = self.get_student(items)
                    course = None
                    final = False
                    marking_period = None
                    override_final = False
                    comment = ""
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "grade":
                                grade = value
                            elif name == "comment code":
                                for cc in str(value).strip().split(','):
                                    try:
                                        comment += unicode(GradeComment.objects.get(id=int(float(str(cc).strip()))).comment) + " "
                                    except:
                                        if comment:
                                            comment += unicode(cc) + " IS NOT VALID COMMENT CODE! "
                            elif name == "comment":
                                comment = unicode(value) + " "
                            elif name == "course":
                                course = Course.objects.get(fullname=value)
                            elif name == "marking period":
                                marking_period = MarkingPeriod.objects.get(name=value)
                            elif name == "override final":
                                override_final = self.determine_truth(value)
                    if student and course and grade:
                        model, created = Grade.objects.get_or_create(student=student, course=course, marking_period=marking_period, override_final=override_final)
                        model.comment = comment
                        model.set_grade(grade)
                        model.override_final = override_final
                        model.save()
                        if created:
                            self.log_and_commit(model, addition=True)
                            inserted += 1
                        else:
                            self.log_and_commit(model, addition=False)
                            updated += 1
                    else:
                        raise Exception('Requires student, course, and grade')
                except:
                    self.handle_error(row, header, sys.exc_info(), sheet.name)
            x += 1
        return inserted, updated
    
    #@transaction\.commit_manually
    def import_course(self, sheet):
        """Import Courses. Does allow updates. """
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    location = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = False
                    model = None
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "fullname":
                                model, created = Course.objects.get_or_create(fullname=value)
                            elif name == "shortname":
                                model.shortname = unicode(value)
                            elif name == "description":
                                model.description = unicode(value)
                            elif name == "active":
                                model.active = value
                            elif name == "teacher username" or name == "teacher":
                                model.teacher = Faculty.objects.get(username=value)
                            elif name == "location":
                                location, c = Location.objects.get_or_create(name=value)
                                if c: location.save()
                            elif name == "level":
                                try:
                                    model.level = GradeLevel.objects.get(name=value)
                                except:
                                    model.level = GradeLevel.objects.get(id=value)
                            elif name == "homeroom":
                                model.homeroom = value
                            elif name == "graded":
                                model.graded = value
                            elif name == "department":
                                model.department, created = Department.objects.get_or_create(name=value)
                            elif name[:14] == "marking period":
                                model.save()
                                model.marking_period.add(MarkingPeriod.objects.get(name=value))
                            elif name == "enroll cohort":
                                model.save()
                                cohort, created = Cohort.objects.get_or_create(name=value)
                                model.add_cohort(cohort)
                    model.full_clean()
                    model.save()
                    if created:
                        self.log_and_commit(model, addition=True)
                        inserted += 1
                    else:
                        self.log_and_commit(model, addition=False)
                        updated += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted, updated
    
    #@transaction\.commit_manually
    def import_course_meet(self, sheet):
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = False
                    course = None
                    period = None
                    day = None
                    location = None
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "course" or name == "course fullname":
                                course = Course.objects.get(fullname=value)
                            elif name == "period":
                                period = Period.objects.get(name=value)
                            elif name == "day":
                                day = self.convert_day(value)
                            elif name == "location":
                                location = Location.objects.get_or_create(name=value)[0]
                    if course and period and day:
                        meet, created = CourseMeet.objects.get_or_create(course=course, period=period, day=day)
                        if location:
                            meet.location = location
                            meet.save()
                        if created:
                            inserted += 1
                        else:
                            updated += 1
                    else:
                        raise Exception('Requires course, period, and day')
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted, updated
                
    #@transaction\.commit_manually
    def import_period(self, sheet):
        """Import periods. Does not allow updates. """
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = False
                    model = Period()
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "name":
                               model, created = Period.objects.get_or_create(name=value)
                            elif name == "start time":
                                model.start_time = self.convert_time(value)
                            elif name == "end time":
                                model.end_time = self.convert_time(value)
                    model.full_clean()
                    model.save()
                    if created:
                        self.log_and_commit(model, addition=True)
                        inserted += 1
                    else:
                        self.log_and_commit(model, addition=False)
                        updated += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted, updated
    
    #@transaction\.commit_manually
    def import_days_off(self, sheet):
        """Import days off for a marking period. Does not allow updates. """
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = False
                    model = DaysOff()
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "date":
                               model.date = self.convert_date(value)
                            elif name == "marking period":
                                model.marking_period = MarkingPeriod.objects.get(name=value)
                    model.full_clean()
                    model.save()
                    self.log_and_commit(model, addition=True)
                    inserted += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted
    
    #@transaction\.commit_manually
    def import_mp(self, sheet):
        """Import marking periods. Does not allow updates. """
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = False
                    model = MarkingPeriod()
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "name":
                                model.name = unicode(value)
                            if name == "shortname" or name == "short name":
                                model.shortname = unicode(value)
                            elif name == "start date":
                               model.start_date = self.convert_date(value)
                            elif name == "end date":
                                model.end_date = self.convert_date(value)
                            elif name == "school year":
                                model.school_year = SchoolYear.objects.get(name=value)
                            elif name == "monday":
                                if value == "True" or value == "Yes" or value == True or value == 1:
                                    model.monday = True
                            elif name == "tuesday":
                                if value == "True" or value == "Yes" or value == True or value == 1:
                                    model.tuesday = True
                            elif name == "wednesday":
                                if value == "True" or value == "Yes" or value == True or value == 1:
                                    model.wednesday = True
                            elif name == "thursday":
                                if value == "True" or value == "Yes" or value == True or value == 1:
                                    model.thursday = True
                            elif name == "friday":
                                if value == "True" or value == "Yes" or value == True or value == 1:
                                    model.friday = True
                            elif name == "saturday":
                                if value == "True" or value == "Yes" or value == True or value == 1:
                                    model.saturday = True
                            elif name == "sunday":
                                if value == "True" or value == "Yes" or value == True or value == 1:
                                    model.sunday = True
                    model.full_clean()
                    model.save()
                    self.log_and_commit(model, addition=True)
                    inserted += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted
    
    #@transaction\.commit_manually
    def import_year(self, sheet):
        """Import school year. Does not allow updates. """
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = False
                    model = SchoolYear()
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "name":
                                model.name = unicode(value)
                            elif name == "start date":
                               model.start_date = self.convert_date(value)
                            elif name == "end date":
                                model.end_date = self.convert_date(value)
                            elif name == "active year":
                                if value == "True" or value == "Yes" or value == True or value == 1:
                                    model.active_year = True
                    model.full_clean()
                    model.save()
                    self.log_and_commit(model, addition=True)
                    inserted += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted
    
    #@transaction\.commit_manually
    def import_discipline(self, sheet):
        """Import discipline linking them to each a student. Does not allow updates. 
        If a infraction or action doesn't already exist, it is created"""
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            model = None
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = False
                    model = StudentDiscipline()
                    action_instance = None
                    student = self.get_student(items)
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "date":
                               model.date = self.convert_date(value)
                            elif name == "teacher username":
                                model.teacher = Faculty.objects.get(username=value)
                            elif name == "infraction":
                                infr, created = PresetComment.objects.get_or_create(comment__iexact=value)
                                if created:
                                    infr.comment = value 
                                    infr.save()
                                model.infraction = infr
                            elif name == "comments":
                                model.comments = unicode(value)
                            elif name == "action":
                                action, created = DisciplineAction.objects.get_or_create(name__iexact=value)
                                if created: action.save()
                                model.save()
                                action_instance = DisciplineActionInstance(action=action, student_discipline=model)
                            elif name == "action quantity":
                                action_instance.quantity = value       
                    model.full_clean()
                    model.save()
                    model.students.add(student)
                    if action_instance: action_instance.save()
                    self.log_and_commit(model, addition=True)
                    inserted += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted
    
    #@transaction\.commit_manually
    def import_attendance(self, sheet):
        """Import attendance linking them to each a student. Does not allow updates. 
        If a status doesn't already exist, it is created"""
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name  = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = False
                    model = StudentAttendance()
                    name = "student"
                    model.student = self.get_student(items)
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "date":
                               model.date = self.convert_date(value)
                            elif name == "status":
                                status, created = AttendanceStatus.objects.get_or_create(name=value)
                                if created: 
                                    status.name = unicode(value)
                                    status.save()
                                model.status = status
                            elif name == "code":
                                model.status = AttendanceStatus.objects.get(code=value)
                            elif name == "notes":
                                model.notes = unicode(value)
                    model.full_clean()
                    model.save()
                    self.log_and_commit(model, addition=True)
                    inserted += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted
    
    #@transaction\.commit_manually
    def import_emergency_contacts(self, sheet):
        """Import emergency contacts. Link to student by either username or
        unique id. Will attempt to lookup duplicates and update instead of 
        create by using get_or_create on
        student and fname and lname and relationship"""
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = False
                    model = None
                    id = None
                    fname = None
                    mname = None
                    lname = None
                    relationship = None
                    email = None
                    street = None
                    city = state = None
                    zips = None # not sure why I can't use zip
                    unknown_number = None
                    work = None
                    home = None
                    cell = None
                    primary = False
                    applicant = None
                    student = self.get_student(items, allow_none=True)
                    
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "emergency contact id":
                                id = value
                            elif name == "applicant id":
                                from ecwsp.admissions.models import Applicant
                                applicant = Applicant.objects.get(id=value)
                            elif name == "first name":
                                fname = value
                            elif name == "last name":
                                lname = value
                            elif name == "relationship":
                                relationship = value
                            elif name == "email":
                                email = value
                            elif name == "number":
                                unknown_number = value
                            elif name == "home number":
                                home = value
                            elif name == "cell number":
                                cell = value
                            elif name == "work number":
                                work = value
                            elif name == "primary":
                                primary = self.determine_truth(value)
                            elif name == "street":
                                street = value
                            elif name == "city":
                                city = value
                            elif name == "state":
                                state = value
                            elif name == "zip":
                                zips = value
                            elif name =="middle name":
                                mname = value
                    if id:
                        model, created = EmergencyContact.objects.get_or_create(id=id)
                    elif student and fname and lname:
                        # Secondary key, good enough to find unique emergency contact
                        ecs = EmergencyContact.objects.filter(fname=fname, lname=lname, student=student)
                        if ecs.count() == 1:
                            model = ecs[0]
                        else:
                           model = EmergencyContact()
                    elif applicant and fname and lname:
                        ecs = EmergencyContact.objects.filter(fname=fname, lname=lname, applicant=applicant)
                        if ecs.count() == 1:
                            model = ecs[0]
                        else:
                           model = EmergencyContact()
                    else:
                        model = EmergencyContact()
                    if fname: model.fname = fname
                    if mname: model.mname = mname
                    if lname: model.lname = lname
                    if email: model.email = email
                    if street: model.street = street
                    if city: model.city = city
                    if state: model.state = state
                    if zips: model.zip = zips
                    model.primary_contact = primary
                    if relationship: model.relationship_to_student = relationship
                    model.full_clean()
                    model.save()
                    if student: model.student_set.add(student)
                    if applicant: model.applicant_set.add(applicant)
                    if unknown_number:
                        number, extension = self.import_number(unknown_number)
                        ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="" , contact=model)
                        ecNumber.contact = model
                        ecNumber.save()
                    if home:    
                        number, extension = self.import_number(home)
                        ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="H" , contact=model)
                        ecNumber.contact = model
                        ecNumber.save()
                    if cell:    
                        number, extension = self.import_number(cell)
                        ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="C" , contact=model)
                        ecNumber.contact = model
                        ecNumber.save()
                    if work:    
                        number, extension = self.import_number(work)
                        ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="W" , contact=model)
                        ecNumber.contact = model
                        ecNumber.save()
                    model.save()
                    if model.id:
                        self.log_and_commit(model, addition=False)
                        updated += 1
                    else:
                        self.log_and_commit(model, addition=True)
                        inserted += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted, updated
    
    #@transaction.commit_manually
    def import_students(self, sheet):
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    p_fname = p_mname = p_lname = p_relationship_to_student = p_street = p_city = None
                    p_state = p_zip = p_email = home = cell = work = other = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = False
                    model = None
                    password = None
                    custom_fields = []
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "id":
                                try:
                                    model = Student.objects.get(id=value)
                                    created = False
                                except:
                                    raise Exception("Student ID not found. ID should not be set when creating new student, use unique ID for this.")
                            elif name == "unique id" or name == "unique_id":
                                if model:
                                    model.unique_id = value
                                else:
                                    students = Student.objects.filter(unique_id=value)
                                    if students:
                                        model = students[0]
                                        created = False
                                    else:
                                        model = Student(unique_id=value)
                                        created = True
                            elif name == "username":
                                if model:
                                    model.username = value
                                else:
                                    students = Student.objects.filter(username=value)
                                    if students:
                                        model = students[0]
                                        created = False
                                    else:
                                        model = Student(username=value)
                                        created = True
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok and model:
                            if name in ['first name','first_name','fname']:
                                model.fname = value
                            elif name == "last name" or name == "lname":
                                model.lname = value
                            elif name == "alert":
                                model.alert = value
                            elif name == "grad date":
                                model.grad_date = self.convert_date(value)
                            elif name == "gender" or name == "sex":
                                model.sex = unicode.upper(value)
                            elif name == "birth date" or name == "birthday" or name == "birth day" or name == "bday":
                                model.bday = self.convert_date(value)
                            elif name == "year" or name == "grade level":
                                try:
                                    model.year = GradeLevel.objects.get(name=value)
                                except:
                                    model.year = GradeLevel.objects.get(id=value)
                            elif name == "picture":
                                model.pic = value
                            
                            elif name == "parent e-mail" or name == "parent email" or name == "parentemail" or name == "parent__email":
                                model.parent_email = value
                            elif name == "middle name" or name == "mname":
                                model.mname = value
                            elif name == "homeroom":
                                model.home_room = value
                            elif name == "ssn" or name == "social security":
                                model.ssn = value
                            elif name in ['preferred language', 'language', 'family preferred language']:
                                language = LanguageChoice.objects.get_or_create(name=value)[0]
                                model.name = language
                            elif name == "deleted":
                                model.deleted = self.determine_truth(value)
                            
                            # Import emergency contact shortcut
                            elif name in ["parent first name", 'parent 1 first name']:
                                p_fname = value
                            elif name in ["parent middle name", 'parent 1 middle name']:
                                p_mname = value
                            elif name in ['parent last name', 'parent 1 last name']:
                                p_lname = value
                            elif name in ['parent relationship to student', 'parent 1 relationship to student']:
                                p_relationship_to_student = value
                            elif name in ['parent street', 'parent 1 street']:
                                p_street = value
                            elif name in ['parent city', 'parent 1 city']:
                                p_city = value
                            elif name in ['parent state', 'parent 1 state']:
                                p_state = value
                            elif name in ['parent zip', 'parent 1 zip']:
                                p_zip = value
                            elif name in ["parent e-mail", "parent email", "parentemail", "parent__email", 'parent 1 email', 'parent 1 e-mail']:
                                p_email = value
                            elif name in ['parent home number', 'parent 1 home number', 'parent home phone', 'parent 1 home phone']:
                                home = value
                            elif name in ['parent cell number', 'parent 1 cell number', 'parent cell phone', 'parent 1 cell phone']:
                                cell = value
                            elif name in ['parent work number', 'parent 1 work number', 'parent work phone', 'parent 1 work phone']:
                                work = value
                            elif name in ['parent number', 'parent 1 number', 'parent other number', 'parent 1 other number', 'parent phone', 'parent 1 phone', 'parent other phone', 'parent 1 other phone']:
                                other = value
                            elif name == "password":
                                password = value
                                
                            # Custom
                            elif name.split() and name.split()[0] == "custom":
                                custom_fields.append([name.split()[1], value])
                                
                    if not model.username and model.fname and model.lname:
                        model.username = self.gen_username(model.fname, model.lname)
                    model.save()
                    if password:
                        user = User.objects.get(username = model.username)
                        user.set_password(password)
                        user.save()
                        model.save()
                    for (custom_field, value) in custom_fields:
                        model.set_custom_value(custom_field, value)
                    
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "student phone":    
                                number, extension = self.import_number(value)
                                contactModel, contactCreated = StudentNumber.objects.get_or_create(number=number, ext=extension, type="H" , student=model)
                                contactModel.save()
                            elif name == "student cell ph" or name == "student cell" or name == "student cell phone":
                                number, extension = self.import_number(value)
                                contactModel, contactCreated = StudentNumber.objects.get_or_create(number=number, ext=extension, type="C" , student=model)
                                contactModel.save()
                            elif name == "student phone other":
                                number, extension = self.import_number(value)
                                contactModel, contactCreated = StudentNumber.objects.get_or_create(number=number, ext=extension, type="O" , student=model)
                                contactModel.save()
                            elif name == "student phone work":
                                number, extension = self.import_number(value)
                                contactModel, contactCreated = StudentNumber.objects.get_or_create(number=number, ext=extension, type="W" , student=model)
                                contactModel.save()
                            elif name == "primary cohort":
                                cohort = Cohort.objects.get_or_create(name=value)[0]
                                student_cohort = StudentCohort.objects.get_or_create(student=model, cohort=cohort)[0]
                                student_cohort.primary = True
                                student_cohort.save()
                    # add emergency contacts (parents)
                    if p_lname and p_fname:
                        ecs = EmergencyContact.objects.filter(fname=p_fname, lname=p_lname, street=p_street)
                        if ecs.count():
                            model.emergency_contacts.add(ecs[0])
                        else:
                            ec = EmergencyContact(
                                fname = p_fname,
                                mname = p_mname,
                                lname = p_lname,
                                relationship_to_student = p_relationship_to_student,
                                street = p_street,
                                city = p_city,
                                state = p_state,
                                zip = p_zip,
                                email=  p_email,
                                primary_contact = True,
                            )
                            ec.save()
                            if other:
                                number, extension = self.import_number(other)
                                ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="" , contact=ec)
                                ecNumber.contact = ec
                                ecNumber.save()
                            if home:    
                                number, extension = self.import_number(home)
                                ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="H" , contact=ec)
                                ecNumber.contact = ec
                                ecNumber.save()
                            if cell:    
                                number, extension = self.import_number(cell)
                                ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="C" , contact=ec)
                                ecNumber.contact = ec
                                ecNumber.save()
                            if work:    
                                number, extension = self.import_number(work)
                                ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="W" , contact=ec)
                                ecNumber.contact = ec
                                ecNumber.save()
                            model.emergency_contacts.add(ec)
                    if created:
                        self.log_and_commit(model, addition=True)
                        inserted += 1
                    else:
                        self.log_and_commit(model, addition=False)
                        updated += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
                x += 1
        return inserted, updated
    
    
    #@transaction\.commit_manually
    def import_applicants(self, sheet):
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    p_fname = p_mname = p_lname = p_relationship_to_student = p_street = p_city = None
                    p_state = p_zip = p_email = home = cell = work = other = None
                    p2_fname = p2_mname = p2_lname = p2_relationship_to_student = p2_street = p2_city = None
                    p2_state = p2_zip = p2_email = home2 = cell2 = work2 = other2 = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = True
                    model = Applicant()
                    model.save()
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "id":
                                model = Applicant.objects.get(id=value)
                                created = False
                                model.save()
                            elif name == "first name" or name == "fname":
                                    model.fname = value
                            elif name == "last name" or name == "lname":
                                model.lname = value
                            elif name == "middle name" or name == "mname":
                                model.mname = value
                            elif name =="social security" or name == "ssn" or name == "social security number":
                                model.ssn = value
                            elif name == "gender" or name == "sex":
                                if value == "Male":
                                    model.sex = "M"
                                elif value == "Female":
                                    model.sex = "F"
                                else:
                                    model.sex = unicode.upper(value)
                            elif name == "birth date" or name == "birthday" or name == "birth day" or name == "bday":
                                model.bday = self.convert_date(value)
                            elif name == "student street" or name == "street":
                                model.street = value
                            elif name == "student city" or name == "city":
                                model.city = value
                            elif name == "student state" or name == "state":
                                model.state = value
                            elif name == "student zip" or name == "zip":
                                model.zip = value
                            elif name == "notes":
                                model.notes = value
                            elif name == "year" or name == "grade level":
                                #try:
                                    model.year = GradeLevel.objects.get(name=value)
                                #except: pass
                                #model.year = GradeLevel.objects.get(id=value)
                            elif name == "school year" or name == "school_year":
                                model.school_year = SchoolYear.objects.get(name=value)
                            elif name == "e-mail" or name == "email":
                                model.email = value
                            elif name == "home_country" or name == "home country":
                                model.home_country = value
                            elif name == "relationship_to_student" or name == "relationship to student":
                                model.relationship_to_student = value
                            elif name == "ethnicity":
                                model.ethnicity = EthnicityChoice.objects.get_or_create(name=value)[0]
                            elif name == "hs_grad_yr" or name == "high school grad year":
                                model.hs_grad_yr = value
                            elif name == "elem_grad_yr" or name == "elem grad year":
                                model.elem_grad_yr = value
                            elif name == "present_school" or name == "present school":
                                model.present_school = FeederSchool.objects.get_or_create(name=value)[0]
                            elif name == "religion":
                                model.religion = ReligionChoice.objects.get_or_create(name=value)[0]
                            elif name == "heard_about_us" or name == "heard about us":
                                model.heard_about_us = HeardAboutUsOption.objects.get_or_create(name=value)[0]
                            elif name == "first_contact" or name == "first contact":
                                model.first_contact = FirstContactOption.objects.get_or_create(name=value)[0]
                            elif name == "borough":
                                model.borough = BoroughOption.objects.get_or_create(name=value)[0]
                            elif name == "application_decision" or name == "application decision":
                                model.application_decision = ApplicationDecisionOption.objects.get_or_create(name=value)[0]
                            elif name == "withdrawn":
                                model.withdrawn = WithdrawnChoices.objects.get_or_create(name=value)[0]
                            elif name == "withdrawn_note" or name == "withdrawn note":
                                model.withdrawn_note = value
                            elif name == "ready for export":
                                model.ready_for_export = self.determine_truth(value)
                            elif name == "student id":
                                model.sis_student = Student.objects.get(id=value)
                            
                            elif name in ["parent first name", 'parent 1 first name']:
                                p_fname = value
                            elif name in ["parent middle name", 'parent 1 middle name']:
                                p_mname = value
                            elif name in ['parent last name', 'parent 1 last name']:
                                p_lname = value
                            elif name in ['parent relationship to student', 'parent 1 relationship to student']:
                                p_relationship_to_student = value
                            elif name in ['parent street', 'parent 1 street']:
                                p_street = value
                            elif name in ['parent city', 'parent 1 city']:
                                p_city = value
                            elif name in ['parent state', 'parent 1 state']:
                                p_state = value
                            elif name in ['parent zip', 'parent 1 zip']:
                                p_zip = value
                            elif name in ["parent e-mail", "parent email", "parentemail", "parent__email", 'parent 1 email', 'parent 1 e-mail']:
                                p_email = value
                            elif name in ['parent home number', 'parent 1 home number', 'parent home phone', 'parent 1 home phone']:
                                home = value
                            elif name in ['parent cell number', 'parent 1 cell number', 'parent cell phone', 'parent 1 cell phone']:
                                cell = value
                            elif name in ['parent work number', 'parent 1 work number', 'parent work phone', 'parent 1 work phone']:
                                work = value
                            elif name in ['parent number', 'parent 1 number', 'parent other number', 'parent 1 other number', 'parent phone', 'parent 1 phone', 'parent other phone', 'parent 1 other phone']:
                                other = value
                            
                            elif name in ['parent 2 first name']:
                                p2_fname = value
                            elif name in ["parent 2 middle name"]:
                                p2_mname = value
                            elif name in ['parent 2 last name']:
                                p2_lname = value
                            elif name in ['parent 2 relationship to student']:
                                p2_relationship_to_student = value
                            elif name in ['parent 2 street']:
                                p2_street = value
                            elif name in ['parent 2 city']:
                                p2_city = value
                            elif name in ['parent 2 state']:
                                p2_state = value
                            elif name in ['parent 2 zip']:
                                p2_zip = value
                            elif name in ["parent 2 e-mail", "parent 2 email"]:
                                p2_email = value
                            elif name in ['parent 2 home number', 'parent 2 home phone']:
                                home2 = value
                            elif name in ['parent 2 cell number', 'parent 2 cell phone']:
                                cell2 = value
                            elif name in ['parent 2 work number', 'parent 2 work phone']:
                                work2 = value
                            elif name in ['parent 2 number', 'parent 2 other number', 'parent 2 phone', 'parent 2 other phone']:
                                other2 = value
                                
                    model.save()
                    # add emergency contacts (parents)
                    if p_lname and p_fname:
                        ecs = EmergencyContact.objects.filter(fname=p_fname, lname=p_lname, street=p_street)
                        if ecs.count():
                            model.parent_guardians.add(ecs[0])
                        else:
                            ec = EmergencyContact(
                                fname = p_fname,
                                mname = p_mname,
                                lname = p_lname,
                                relationship_to_student = p_relationship_to_student,
                                street = p_street,
                                city = p_city,
                                state = p_state,
                                zip = p_zip,
                                email=  p_email,
                                primary_contact = True,
                            )
                            ec.save()
                            if other:
                                number, extension = self.import_number(other)
                                ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="" , contact=ec)
                                ecNumber.contact = ec
                                ecNumber.save()
                            if home:    
                                number, extension = self.import_number(home)
                                ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="H" , contact=ec)
                                ecNumber.contact = ec
                                ecNumber.save()
                            if cell:    
                                number, extension = self.import_number(cell)
                                ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="C" , contact=ec)
                                ecNumber.contact = ec
                                ecNumber.save()
                            if work:    
                                number, extension = self.import_number(work)
                                ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="W" , contact=ec)
                                ecNumber.contact = ec
                                ecNumber.save()
                            model.parent_guardians.add(ec)
                    if p2_lname and p2_fname:
                        ecs = EmergencyContact.objects.filter(fname=p2_fname, lname=p2_lname, street=p2_street)
                        if ecs.count():
                            model.parent_guardians.add(ecs[0])
                        else:
                            ec2 = EmergencyContact(
                                fname = p2_fname,
                                mname = p2_mname,
                                lname = p2_lname,
                                relationship_to_student = p2_relationship_to_student,
                                street = p2_street,
                                city = p2_city,
                                state = p2_state,
                                zip = p2_zip,
                                email=  p2_email,
                                primary_contact = False,
                                )
                            ec2.save()
                            if other2:
                                number, extension = self.import_number(other2)
                                ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="" , contact=ec)
                                ecNumber.contact = ec2
                                ecNumber.save()
                            if home2:    
                                number, extension = self.import_number(home2)
                                ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="H" , contact=ec)
                                ecNumber.contact = ec2
                                ecNumber.save()
                            if cell2:    
                                number, extension = self.import_number(cell2)
                                ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="C" , contact=ec)
                                ecNumber.contact = ec2
                                ecNumber.save()
                            if work2:
                                number, extension = self.import_number(work2)
                                ecNumber, ecNumberCreated = EmergencyContactNumber.objects.get_or_create(number=number, ext=extension, type="W" , contact=ec)
                                ecNumber.contact = ec2
                                ecNumber.save()
                            model.parent_guardians.add(ec2)
                    model.save()
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "siblings":
                                model.siblings.add(Student.objects.get(value))
                            elif name == "open_house_attended" or name == "open house attended":
                                try:
                                    house = OpenHouse.objects.get_or_create(date=self.convert_date(value))[0]
                                except:
                                    house = OpenHouse.objects.get_or_create(name=value)[0]
                                model.open_house_attended.add(house)
                            elif name == "checklist":
                                check = AdmissionCheck.objects.get(name=value)
                                model.checklist.add(check)
                    
                    inserted, updated = self.log_and_commit(model, inserted, updated, created)
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted, updated
    
    #@transaction\.commit_manually
    def import_admissions_checks(self, sheet):
        from ecwsp.admissions.models import Applicant, AdmissionCheck
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            try:
                name = None
                row = sheet.row(x)
                items = zip(header, row)
                created = True
                applicant = None
                check = None
                
                for (name, value) in items:
                    is_ok, name, value = self.sanitize_item(name, value)
                    if is_ok:
                        if name == "applicant id":
                            applicant = Applicant.objects.get(id=value)
                        elif name == "check name":
                            check = AdmissionCheck.objects.get(name=value)
                applicant.checklist.add(check)
                self.log_and_commit(applicant, addition=False)
                if created:
                    inserted += 1
                else:
                    updated += 1
            except:
                self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted, updated
    
    #@transaction\.commit_manually
    def import_admissions_log(self, sheet):
        from ecwsp.admissions.models import Applicant, ContactLog
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    created = True
                    applicant = None
                    model = ContactLog()
                    
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "applicant id":
                                model.applicant = Applicant.objects.get(id=value)
                            elif name == "date":
                                model.date = self.convert_date(value)
                            elif name == "note":
                                model.note = value
                            elif name == "user":
                                model.user = User.objects.get(username=value)
                    model.save()
                    self.log_and_commit(model, addition=False)
                    if created:
                        inserted += 1
                    else:
                        updated += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted, updated
    
    @transaction.commit_on_success
    def import_grades(self, course, marking_period):
        """ Special import for teachers to upload grades
        Returns Error Message """ 
        from ecwsp.grades.models import Grade,GradeComment
        try:
            sheet = self.get_sheet_by_case_insensitive_name(marking_period.name)
        except:
            return "Could not find a sheet named %s" % (marking_period,)
        x = 0
        if not sheet:
            return "Could not find a sheet named %s" % (marking_period,)
        header = sheet.row(x)
        while x < sheet.nrows:
            try:
                name = None
                row = sheet.row(x)
                items = zip(header, row)
                created = False
                model = None
                grade = None
                comment = ""
                del_comments = False
                for (name, value) in items:
                    is_ok, name, value = self.sanitize_item(name, value)
                    if is_ok:
                        if name == "username":
                            student = Student.objects.get(username=value)
                            model, created = Grade.objects.get_or_create(student=student, course=course, marking_period=marking_period)
                        elif name in ["final grade %",'marking period grade (%)','grade']:
                            grade = value
                        elif name == "comment code" or name == "comment codes" or name == "comment\ncodes":
                            value = unicode.lower(unicode(value))
                            for cc in value.split(','):
                                try:
                                    comment += unicode(GradeComment.objects.get(id=int(float(str(cc)))).comment) + " "
                                except:
                                    comment += unicode(cc) + " IS NOT VALID COMMENT CODE! "
                            value = unicode.lower(value)
                            if value.strip() == "none":
                                del_comments = True
                        elif name == "comment":
                            comment = unicode(value) + " "
                            if value.strip() == "none":
                                del_comments = True
                if model and grade:
                    model.set_grade(grade)
                    model.save()
                    self.log_and_commit(model, addition=False)
                if model and comment:
                    model.comment = comment
                    model.save()
                if model and del_comments:
                    model.comment = ""
                    model.save()
            except:
                print >> sys.stderr, str(sys.exc_info())
            x += 1  

    #@transaction\.commit_manually
    def import_workteams(self, sheet):
        from ecwsp.work_study.models import *
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    model = None
                    created = False
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "id" or name == "workteam id":
                                model = WorkTeam.objects.get(id=value)
                                created = False
                            elif name == "workteam" or name == "work team" or name == "name":
                                model, created = WorkTeam.objects.get_or_create(team_name=value)
                            if name == "company":
                                model.company = Company.objects.get_or_create(name=value)[0]
                            elif name == "login":
                                login = WorkTeamUser.objects.get_or_create(username=value)[0]
                                group = Group.objects.get_or_create(name="Company")[0]
                                login.groups.add(group)
                                model.login.add(login)
                                login.save()
                            elif name == "password":
                                login.set_password(value)
                                login.save()
                            elif name == "paying":
                                if value == "Paying": model.paying = "P"
                                elif value == "Non-Paying": model.paying = "N"
                                elif value == "Funded": model.paying = "F"
                                else: model.paying = value
                            elif name == "funded_by" or name =="funded by":
                                model.funded_by = value
                            elif name == "cra":
                                cra, created = CraContact.objects.get_or_create(name=User.objects.get(username=value))
                                model.cra = cra
                            elif name == "industry_type" or name == "industry type":
                                model.industry_type = value
                            elif name == "train_line" or name == "train line":
                                model.train_line = value
                            elif name == "industry_type" or name == "industry type":
                                model.industry_type = value
                            elif name == "stop_location" or name == "stop location":
                                model.stop_location = value
                            elif name == "dropoff_location" or name == "dropoff location":
                                model.dropoff_location = PickupLocation.objects.get_or_create(location=value)[0]
                            elif name == "pickup_location" or name == "pickup location":
                                model.pickup_location = PickupLocation.objects.get_or_create(location=value)[0]
                            elif name == "address":
                                model.address = value
                            elif name == "city":
                                model.city = value
                            elif name == "state":
                                model.state = value
                            elif name == "zip":
                                model.zip = value
                            elif name == "directions_to" or name == "directions to":
                                model.directions_to = value
                            elif name == "directions_pickup" or name == "directions pickup":
                                model.directions_pickup = value
                            elif name == "use_google_maps" or name == "use google maps":
                                model.use_google_maps = self.determine_truth(value)
                            elif name == "job_description" or name == "job description":
                                model.job_description = value
                    model.save()
                    if created:
                        self.log_and_commit(model, addition=True)
                        inserted += 1
                    else:
                        self.log_and_commit(model, addition=False)
                        updated += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
            x += 1
        return inserted, updated


    #@transaction\.commit_manually
    def import_company_contacts(self, sheet):
        from ecwsp.work_study.models import *
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    model = Contact()
                    created = True
                    fname = None
                    lname = None
                    phone = None
                    phone_cell = None
                    fax = None
                    email = None
                    workteam = None
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "id":
                                model = Contact.objects.get(id=value)
                                created = False
                            elif name == "guid":
                                model.guid = value
                            elif name == "fname" or name == "first name":
                                fname = value
                            elif name == "lname" or name == "last name":
                                lname = value
                            elif name == "phone":
                                number, ext = self.import_number(value)
                                if ext:
                                    phone = number + " " + ext
                                else:
                                    phone = number
                            elif name == "phone_cell" or name == "phone cell":
                                number, ext = self.import_number(value)
                                if ext:
                                    phone_cell = number + " " + ext
                                else:
                                    phone_cell = number
                            elif name == "email":
                                email = value
                            elif name == "fax":
                                fax = value
                            elif name == "work team":
                                workteam = WorkTeam.objects.get(team_name=value)
                    existing_contacts = Contact.objects.filter(fname=fname,lname=lname)
                    if existing_contacts.count()==1:
                        model = Contact.objects.get(id = existing_contacts[0].id)
                        created = False
                    elif existing_contacts.count() >1:
                        exist_filter_by_workteam = existing_contacts.workteam_set.filter(workteam)
                        if exist_filter_by_workteam.count()==1:
                            model = Contact.objects.get(id = exist_filter_by_workteam[0].id)
                            created = False
                        else:
                            model.fname =fname
                            model.lname = lname
                    else:
                        model.fname = fname
                        model.lname = lname
                    if phone: model.phone = phone
                    if phone_cell: model.phone_cell = phone_cell
                    if fax: model.fax = fax
                    if email: model.email = email
                    model.save()
                    if workteam: model.workteam_set.add(workteam)
                        
                    model.save()
                    if created:
                        self.log_and_commit(model, addition=True)
                        inserted += 1
                    else:
                        self.log_and_commit(model, addition=False)
                        updated += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
                x += 1
            
        return inserted, updated


    #@transaction\.commit_manually
    def import_student_workers(self, sheet):
        """ Import students workers """
        from ecwsp.work_study.models import *
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    model = None
                    supid = None
                    created = False
                    try:
                        student = self.get_student(items)
                    except:
                        student = None
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if student:
                                if hasattr(student, 'studentworker'):
                                    model = student.studentworker
                                else:
                                    student.promote_to_worker()
                                    student = StudentWorker.objects.get(id=student.id)
                            else:
                                if name == "student unique id":
                                    model = StudentWorker(unique_id=value)
                                elif name == "student username":
                                    model = StudentWorker(username=value)
                            if name == "day" or name == "work day":
                                value = unicode.lower(value)
                                if value == "monday": model.day = "M"
                                elif value == "tuesday": model.day = "T"
                                elif value == "wednesday": model.day = "W"
                                elif value == "thursday": model.day = "TH"
                                elif value == "friday": model.day = "F"
                                else: model.day = value
                            elif name == "workteam id" or name == 'workteam_id':
                                model.placement = WorkTeam.objects.get(id=value)
                            elif name == "workteam name" or name == "placement":
                                model.placement = WorkTeam.objects.get(team_name=value)
                            elif name == "work permit" or name == "work permit number":
                                model.work_permit_no = value
                            elif name == "primary supervisor id" or name == "supervisor id":
                                supid = value
                                if Contact.objects.get(id=supid):
                                    model.primary_contact = Contact.objects.get(id=supid)
                    model.save()
                    if created:
                        self.log_and_commit(model, addition=True)
                        inserted += 1
                    else:
                        self.log_and_commit(model, addition=False)
                        updated += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
                x += 1
        return inserted, updated


    #@transaction\.commit_manually
    def import_contract_information(self, sheet):
        #does not allow  updates
        from ecwsp.work_study.models import *
        x, header, inserted, updated = self.import_prep(sheet)
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    model = None
                    created = True
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "company":
                                model = CompContract(company = Company.objects.get(name=value))
                            elif name == "official company name" or name == "official name" or name == "company name":
                                model.company_name = value
                            elif name == "name" or name == "contact name":
                                model.name = value
                            elif name == "contact title" or name =="title":
                                model.title = value
                            elif name == "date" or name == "effective date" or name == "start date":
                                model.date = self.convert_date(value)
                            elif name == "school year":
                                model.school_year = SchoolYear.objects.get(name=value)
                            elif name == "number of students" or name == "number students" or name == "students":
                                model.number_students = value
                            elif name == "payment option" or name == "payment":
                                model.payment = PaymentOption.objects.get(name=value)
                            elif name.find("responsibilities") != -1:
                                model.save()
                                try:
                                    model.student_functional_responsibilities.add(StudentFunctionalResponsibility.objects.get(name=value))
                                except:
                                    model.student_functional_responsibilities_other += value
                            elif name.find("skills") != -1:
                                model.save()
                                try:
                                    model.student_desired_skills.add(StudentDesiredSkill.objects.get(name = value))
                                except:
                                    model.student_desired_skills_other += value
                            elif name == "student leave" or name == "leave":
                                model.student_leave = self.determine_truth(value)
                            elif name == "student leave lunch" or name == "leave lunch" or name == "lunch":
                                model.student_leave_lunch = self.determine_truth(value)
                            elif name == "student leave errands" or name == "leave errands" or name == "errands":
                                model.student_leave_errands = self.determine_truth(value)
                            elif name == "student leave other" or name == "leave other":
                                model.student_leave_other = value
                            elif name == "signed":
                                model.signed = self.determine_truth(value)
                            
                            
                    model.save()
                    if created:
                        self.log_and_commit(model, addition=True)
                        inserted += 1
                    else:
                        self.log_and_commit(model, addition=False)
                        updated += 1
                except:
                    self.handle_error(row, name, sys.exc_info(), sheet.name)
                x += 1
        return inserted, updated
