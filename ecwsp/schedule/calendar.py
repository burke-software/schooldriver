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

#import vobject
from datetime import datetime

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
        mps = MarkingPeriod.objects.filter(start_date__lt=date, end_date__gt=date)
        periods = Period.objects.filter(start_time__lt=date, end_time__gt=date)
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
        
        if include_asp:
            asp_periods = Period.objects.filter(course__courseenrollment__user=student, course__asp=True).order_by('start_time').distinct()
            periods = periods | asp_periods
            asp_course_meets = CourseMeet.objects.filter(course__courseenrollment__user=student, course__asp=True).distinct()
            course_meets = course_meets | asp_course_meets
        
        days = []
        arr_days = []
        for day in CourseMeet.day_choice:
            if course_meets.filter(day=day[0]).count():
                days.append(day[1])
                arr_days.append(day)
                
        for period in periods:
            period.days = []
            for day in arr_days:
                course = course_meets.filter(day=day[0], period=period)
                if course.count():
                    period.days.append(course[0])
                else:
                    period.days.append(None)
            CourseMeet.objects.filter(course__courseenrollment__user=student, course__marking_period=marking_period, ).distinct()
        return days, periods
