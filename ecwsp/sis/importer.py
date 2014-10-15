from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.db import transaction
from django.conf import settings

from ecwsp.admissions.models import *
from ecwsp.sis.models import *
from ecwsp.schedule.models import *
from ecwsp.sis.xl_report import XlReport
from ecwsp.sis.uno_report import *
from ecwsp.attendance.models import *
from ecwsp.standard_test.models import StandardCategory, StandardCategoryGrade, StandardTest, StandardTestResult

import xlrd
import re
from heapq import merge
from datetime import time
import datetime
import sys
from decimal import *
import subprocess
import os.path

class Importer:
    def __init__(self, file=None, user=None):
        """Opens file. If not xls, convert to xls using uno
        supports any file Openoffice.org supports"""
        if file:
            self.file = file
            filename = os.path.basename(file.name)
            if filename[-3:] == "xls":
                self.book = xlrd.open_workbook(file_contents=file.read())
            else: # convert to xls
                destination = open('/tmp/' + filename, 'wb+')
                destination.write(file.read())
                destination.close()
                document = uno_open('/tmp/' + str(filename))
                tmp, filename, content = uno_save(document, filename, "xls")
                self.book = xlrd.open_workbook(tmp.name)
            self.error_data = {}
            self.error_titles = {}
            self.errors = 0
            self.user = user
    
        
    def make_log_entry(self, user_note=""):
        self.log = ImportLog(user=self.user, user_note=user_note, import_file=self.file)
        file_name = datetime.datetime.now().strftime("%Y%m%d%H%M") + ".sql"
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
        """Generate a unique username for a ***User*** (not MdlUser) based on first and last name
        Try first the first letter of the first name plus the last name
        if fail, try adding more letters of the first name
        if fail, add an incrementing number to the end.
        This function should always find a name and never fail except in
        absurd scenarios with many users and limited varchar space
        """
        # We want usernames to be a-z only!
        from django.utils.encoding import smart_unicode
        import unicodedata
        # Try to deal with unicode nicely
        # http://www.peterbe.com/plog/unicode-to-ascii
        fname = unicodedata.normalize('NFKD', smart_unicode(fname)).encode('ascii', 'ignore')
        lname = unicodedata.normalize('NFKD', smart_unicode(lname)).encode('ascii', 'ignore')
        fname = fname.lower()
        lname = lname.lower()
        # Kill any character outside a-z
        fname = re.sub('[^a-z]', '', fname)
        lname = re.sub('[^a-z]', '', lname)

        try:
            i = 1
            username = fname[:i] + lname
            while User.objects.filter(username=username).count() > 0:
                if i < len(fname):
                    i += 1
                else:
                    raise UsernameError
                username = fname[:i] + lname
                if username == "": raise UsernameError
        except:
            number = 1
            username = fname[:i] + lname + str(number)
            while User.objects.filter(username=username).count() > 0:
                number += 1
                username = fname[:i] + lname + str(number)
        return username
    
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
        is raised if the student isn't found. default False"""
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
                        try:
                            return Student.objects.get(id=value)
                        except:
                            return Student.objects.get(username=value)
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
        
        sheet = self.get_sheet_by_case_insensitive_name("standard test")
        if sheet:
            inserted = self.import_standard_test(sheet)
            msg += "%s standard tests inserted <br/>" % (inserted)
        sheet = self.get_sheet_by_case_insensitive_name("alumni note")
        if sheet:
            inserted, updated = self.import_alumni_note(sheet)
            msg += "%s alumni note entries inserted,<br/>" % (inserted,)
            
        sheet = self.get_sheet_by_case_insensitive_name("alumni email")
        if sheet:
            inserted, updated = self.import_alumni_email(sheet)
            msg += "%s alumni email inserted,<br/>" % (inserted,)
        sheet = self.get_sheet_by_case_insensitive_name("alumni number")
        if sheet:
            inserted, updated = self.import_alumni_number(sheet)
            msg += "%s alumni numbers inserted,<br/>" % (inserted,)
            
        sheet = self.get_sheet_by_case_insensitive_name("college enrollment")
        if sheet:
            inserted, updated = self.import_college_enrollment(sheet)
            msg += "%s college enrollments inserted, %s college enrollments updated. <br/>" % (inserted, updated)
        
        if msg == "":
            msg = "No files found. Check if sheets are named correctly. "
        
        msg += unicode(self.errors) + " error(s). "
        
        filename = 'import_error.xlsx'
        if len(self.error_data):
            self.log.errors = True
            self.log.save()
            report = XlReport()
            save = False
            for key, error_page in self.error_data.items():
                if len(error_page):
                    save = True
                    report.add_sheet(error_page, header_row=self.error_titles[key][0], title=key)
            if save:
                report.save(filename)
            else:
                filename = None
        return msg, filename
    
    def import_just_alumni_data(self):
        inserted = 0
        msg = ""
        #try:
        sheet = self.book.sheet_by_index(0) # Just get the first one
        inserted, updated = self.import_college_enrollment(sheet)
        msg += "%s records inserted <br/>" % (inserted)
        msg += "%s records updated<br/>" % (updated)
        #except: pass
        
        if msg == "":
            msg = "No files found. Check if sheets are named correctly. "
        
        msg += unicode(self.errors) + " error(s). "
        
        filename = 'import_error.xls'
        if len(self.error_data):
            report = XlReport()
            save = False
            for key, error_page in self.error_data.items():
                if len(error_page):
                    save = True
                    report.add_sheet(error_page, header_row=self.error_titles[key][0], title=key)
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
            report = XlReport()
            save = False
            for key, error_page in self.error_data.items():
                if len(error_page):
                    save = True
                    report.add_sheet(error_page, header_row=self.error_titles[key][0], title=key)
            if save:
                report.save(filename)
            else:
                filename = None
        return msg, filename
    
    
    def import_standard_test(self, sheet, known_test=None):
        """Import Standardized tests. Does not allow updates.
        test: if the test name is already known. """
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
                                    test = StandardTest.objects.get_or_create(name="PLAN")[0]
                                    model.test = test
                            elif name[:9] == "category ":
                                model.save()
                                category, created = StandardCategory.objects.get_or_create(name=name[9:], test=test)
                                grade, created = StandardCategoryGrade.objects.get_or_create(category=category, result=model, grade=value)
                            elif name in ["verbal", "math", "writing", "english", "reading", "science", "writing_sub", "comb_eng_write", "composite"]: # Naviance
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
    
    def import_alumni_email(self, sheet):
        from ecwsp.alumni.models import Alumni, AlumniEmail
        x, header, inserted, updated = self.import_prep(sheet)
        name = None
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    student = self.get_student(items,try_secondary=True)
                    email = email_type = None
                    if hasattr(student, 'alumni'):
                        alumni = student.alumni
                    else:
                        alumni = Alumni(student=student)
                        alumni.save()
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name == "email":
                                email = value
                            elif name == "type":
                                email_type = value
                    note, created = AlumniEmail.objects.get_or_create(
                        alumni=alumni,
                        email=email,
                        type=email_type,
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
    
    
    def import_alumni_number(self, sheet):
        from ecwsp.alumni.models import Alumni, AlumniPhoneNumber
        x, header, inserted, updated = self.import_prep(sheet)
        name = None
        while x < sheet.nrows:
            with transaction.commit_manually():
                try:
                    name = None
                    row = sheet.row(x)
                    items = zip(header, row)
                    student = self.get_student(items,try_secondary=True)
                    phone_number = phone_number_type = None
                    if hasattr(student, 'alumni'):
                        alumni = student.alumni
                    else:
                        alumni = Alumni(student=student)
                        alumni.save()
                    for (name, value) in items:
                        is_ok, name, value = self.sanitize_item(name, value)
                        if is_ok:
                            if name in ["phone number", 'number']:
                                phone_number = AlumniEmail.objects.get_or_create(email=value)[0]
                            elif name == "type":
                                phone_number_type = value
                    note, created = AlumniPhoneNumber.objects.get_or_create(
                        alumni=alumni,
                        phone_number=phone_number,
                        type=phone_number_type,
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
                    course_section = None
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
                            elif name == "course section":
                                course_section = CourseSection.objects.get(fullname=value)
                            elif name == "marking period":
                                marking_period = MarkingPeriod.objects.get(name=value)
                            elif name == "override final":
                                override_final = self.determine_truth(value)
                    if student and course_section and grade:
                        model, created = Grade.objects.get_or_create(student=student, course_section=course_section, marking_period=marking_period, override_final=override_final)
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
                        raise Exception('Requires student, course section, and grade')
                except:
                    self.handle_error(row, header, sys.exc_info(), sheet.name)
            x += 1
        return inserted, updated
    
    
    @transaction.commit_on_success
    def import_grades(self, course_section, marking_period):
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
                            model, created = Grade.objects.get_or_create(student=student, course_section=course_section, marking_period=marking_period)
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

