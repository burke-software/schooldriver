from django.conf import settings

from celery.task.schedules import crontab
from celery.decorators import periodic_task

import csv
import requests
import tempfile

if "ecwsp.naviance_sso" in settings.INSTALLED_APPS and settings.NAVIANCE_IMPORT_KEY:
    @periodic_task(run_every=crontab(hour=22, minute=26))
    def create_new_naviance_students():
        """ Naviance has no update or create. So this must be seperate.
        We just run each one and half will always fail.
        """
        data = [['Student_ID','Class_Year','Last Name','First Name','Middle Name','Gender','Birthdate','GPA']]
    
        for student in Student.objects.filter(inactive=False):
            row = []
            if settings.NAVIANCE_SWORD_ID == "username":
                row += [student.username]
            elif settings.NAVIANCE_SWORD_ID == "unique_id":
                row += [student.unique_id]
            else:
                row += [student.id]
            if student.class_of_year:
                row += [str(student.class_of_year.year)]
            else:
                row += ['']
            row += [
                student.lname,
                student.fname,
                student.mname,
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
            'account':settings.NAVIANCE_ACCOUNT,
            'username':settings.NAVIANCE_IMPORT_USERNAME,
            'key':settings.NAVIANCE_IMPORT_KEY,
            'type':'1',
            'format':'CSV',
            'header':'Yes',
            'email':settings.NAVIANCE_EMAILS,
            'description':'django-sis import',
            }
        files = {'datafile': ('import.csv',temp)}
        response = requests.post('https://services.naviance.com/school_import.php',data=params,files=files)
        if response.text != 'Success.\n':
            raise Exception("Error in Naviance Data create import: %s" % (response.text,))
        
        params = {
            'account':settings.NAVIANCE_ACCOUNT,
            'username':settings.NAVIANCE_IMPORT_USERNAME,
            'key':settings.NAVIANCE_IMPORT_KEY,
            'type':'11',
            'format':'CSV',
            'header':'Yes',
            'email':settings.NAVIANCE_EMAILS,
            'description':'django-sis import',
            }
        response = requests.post('https://services.naviance.com/school_import.php',data=params,files=files)
        if response.text != 'Success.\n':
            raise Exception("Error in Naviance Data update import: %s" % (response.text,))