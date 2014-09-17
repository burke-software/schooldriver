from constance import config
from ecwsp.sis.models import Student
from ecwsp.sis.helper_functions import strip_unicode_to_ascii, all_tenants

from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django_sis.celery import app

import csv
import requests
import tempfile

@app.task
@all_tenants
def create_new_naviance_students():
    """ Naviance has no update or create. So this must be seperate.
    We just run each one and half will always fail.
    """
    if config.NAVIANCE_IMPORT_KEY:
        data = [['Student_ID','Class_Year','Last Name','First Name','Middle Name','Gender','Birthdate','GPA']]

        for student in Student.objects.filter(is_active=True):
            row = []
            if config.NAVIANCE_SWORD_ID == "username":
                row += [student.username]
            elif config.NAVIANCE_SWORD_ID == "unique_id":
                row += [student.unique_id]
            else:
                row += [student.id]
            if student.class_of_year:
                row += [str(student.class_of_year.year)]
            else:
                row += ['']
            row += [
                strip_unicode_to_ascii(student.last_name),
                strip_unicode_to_ascii(student.first_name),
                strip_unicode_to_ascii(student.mname),
                student.sex,
            ]
            if student.bday:
                row += [student.bday.strftime('%Y%m%d')]
            else:
                row += ['']
            row += [student.gpa]
            data += [row]

        temp = tempfile.TemporaryFile()
        wr = csv.writer(temp,quoting=csv.QUOTE_ALL)
        wr.writerows(data)
        temp.seek(0)

        params = {
            'account':config.NAVIANCE_ACCOUNT,
            'username':config.NAVIANCE_IMPORT_USERNAME,
            'key':config.NAVIANCE_IMPORT_KEY,
            'type':'1',
            'format':'CSV',
            'header':'Yes',
            'email':config.NAVIANCE_EMAILS,
            'description':'django-sis import',
            }
        files = {'datafile': ('import.csv',temp)}
        response = requests.post('https://services.naviance.com/school_import.php',data=params,files=files)
        if response.text != 'Success.\n':
            raise Exception("Error in Naviance Data create import: %s" % (response.text,))

        temp.seek(0)
        files = {'datafile': ('import.csv',temp)}
        params = {
            'account':config.NAVIANCE_ACCOUNT,
            'username':config.NAVIANCE_IMPORT_USERNAME,
            'key':config.NAVIANCE_IMPORT_KEY,
            'type':'11',
            'format':'CSV',
            'header':'Yes',
            'email':config.NAVIANCE_EMAILS,
            'description':'django-sis import',
            }
        response = requests.post('https://services.naviance.com/school_import.php',data=params,files=files)
        if response.text != 'Success.\n':
            raise Exception("Error in Naviance Data update import: %s" % (response.text,))
