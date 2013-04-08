#       calendar.py
#       
#       Copyright 2010 Cristo Rey New York High School
#        Author David M Burke <david@burkesoftware.com>
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

# Handles all calendar operations to create ical files and sync
# with Google calendar

from ecwsp.schedule.models import *
from ecwsp.sis.models import SchoolYear
from ecwsp.administration.models import Configuration

#import vobject
from datetime import datetime

def get_active_class_config():
    if Configuration.get_or_default("Only Active Classes in Schedule", None).value == "True" \
    or Configuration.get_or_default("Only Active Classes in Schedule", None).value == "true" \
    or Configuration.get_or_default("Only Active Classes in Schedule", None).value == "T":
        return "True"
    else:
        return "False"
class Calendar:
    """ Handles calendar functionality. Download ical, sync with Google Apps, or
    directly find where a student it."""
    def generate_ical(user):
        year = SchoolYear.objects.get(active_year=True)
        #cal = vobject.iCalendar()
        
    def find_student(self, student, date=None):
        """ Find a student's current location.
        date: defaults to right now. """
        if not date:
            date = datetime.now()
        mps = MarkingPeriod.objects.filter(start_date__lte=date, end_date__gte=date)
        periods = Period.objects.filter(start_time__lte=date, end_time__gte=date)
        day = date.isoweekday()
        courses = Course.objects.filter(marking_period__in=mps, periods__in=periods, enrollments__student=student)
        course_meet = CourseMeet.objects.filter(course__in=courses, day=day, period__in=periods)
        return course_meet[0].location
    
    
    def build_schedule(self, student, marking_period, include_asp=False):
        """
        Returns days ['Monday', 'Tuesday'...] and periods
        """
        periods = Period.objects.filter(course__courseenrollment__user=student, course__marking_period=marking_period).order_by('start_time').distinct()
        course_meets = CourseMeet.objects.filter(course__courseenrollment__user=student, course__marking_period=marking_period).distinct()
        
        days = []
        arr_days = []
        for day in CourseMeet.day_choice:
            if course_meets.filter(day=day[0]).count():
                days.append(day[1])
                arr_days.append(day)
                
        only_active = Configuration.get_or_default("Only Active Classes in Schedule", "False").value
    
        
        for period in periods:
            period.days = []
            for day in arr_days:
                if  only_active in ['T', 'True', '1', 't', 'true']:
                    course = course_meets.filter(day=day[0], period=period, course__active=True)
                else:
                    course = course_meets.filter(day=day[0], period=period)
                if course.count():
                    period.days.append(course[0])
                else:
                    period.days.append(None)
            CourseMeet.objects.filter(course__courseenrollment__user=student, course__marking_period=marking_period, ).distinct()
        return days, periods
