#   Copyright 2012 David M Burke
#   Author David M Burke <david@burkesoftware.com>
#   
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#     
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#      
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from ecwsp.sis.models import Student
from suds.client import Client
import json
import csv

@login_required
def login(request):
    """ Log student into Naviance. If successful redirect them.
    """
    username = settings.NAVIANCE_USERNAME
    password = settings.NAVIANCE_PASSWORD
    linked_field = settings.NAVIANCE_SWORD_ID
    url = 'https://services.naviance.com/services/school/index.php?wsdl'
    
    client = Client(url)
    token = client.service.GetSessionToken(username, password)
    
    if request.user.groups.filter(name="students").count():
        try:
            student = Student.objects.get(username=request.user.username)
        except:
            return HttpResponse('Not a valid student')
        
        if linked_field == 'username':
            nav_id = student.username
        elif linked_field == 'id':
            nav_id = student.id
        elif linked_field == 'unique_id':
            nav_id = student.unique_id
        else:
            return HttpResponse('Error: NAVIANCE_SWORD_ID not set correctly')
    else:
        nav_id = request.user.username
        
    result = client.service.LoginStudent(
        token,
        '{"highschoolStudentId":"%s"}' % (nav_id,),
    )
    
    url = json.loads(result).get('loginUrl')
    return HttpResponseRedirect(url)

def create_new_naviance_students():
    """ Naviance has no update or create. So this must be seperate.
    """
    data = [['Student_ID','Class_Year','Last Name','First Name','Middle Name','Gender','Birthdate','GPA']]
    for student in Student.objects.filter(inactive=False):
        row = []
        if settings.NAVIANCE_SWORD_ID == "username":
            row += student.username
        elif settings.NAVIANCE_SWORD_ID == "unique_id":
            row += student.unique_id
        else:
            row += student.id
        if student.class_of_year:
            row += student.class_of_year.year
        else:
            row += ''
        row += [
            student.lname,
            student.fname,
            student.mname,
            student.sex,
            student.bday,
            student.gpa,
        ]
        data += [row]
    myfile = open('foo.csv', 'wb')
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(mylist)
    