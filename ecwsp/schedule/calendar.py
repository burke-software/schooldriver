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
    
    
    def build_schedule(self, student, marking_period, include_asp=False, schedule_days=None):
        """
        Returns days ['Monday', 'Tuesday'...] and periods
        """
        periods = Period.objects.filter(coursesection__courseenrollment__user=student, coursesection__marking_period=marking_period).order_by('start_time').distinct()
        course_meets = CourseMeet.objects.filter(section__courseenrollment__user=student, section__marking_period=marking_period).distinct()
        
        if schedule_days is None:
            day_list = CourseMeet.day_choice
        else:
            # super ugly
            day_choices = dict(CourseMeet.day_choice)
            day_list = []
            for schedule_day in schedule_days:
                day_list.append((schedule_day, day_choices[schedule_day]))
        days = []
        arr_days = []
        for day in day_list:
            if course_meets.filter(day=day[0]).count():
                days.append(day[1])
                arr_days.append(day)
                
        only_active = Configuration.get_or_default("Only Active Classes in Schedule", "False").value in \
            ['T', 'True', '1', 't', 'true']
        hide_meetingless = Configuration.get_or_default('Hide Empty Periods in Schedule').value in \
            ['T', 'True', '1', 't', 'true']
        
        useful_periods = []
        for period in periods:
            has_meeting = False
            period.days = []
            for day in arr_days:
                if  only_active:
                    course = course_meets.filter(day=day[0], period=period, course__active=True)
                else:
                    course = course_meets.filter(day=day[0], period=period)
                if course.count():
                    period.days.append(course[0])
                    has_meeting = True
                else:
                    period.days.append(None)
            if has_meeting or not hide_meetingless:
                useful_periods.append(period)
        return days, useful_periods
