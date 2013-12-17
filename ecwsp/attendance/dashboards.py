from django.core.urlresolvers import reverse
from responsive_dashboard.dashboard import Dashboard, Dashlet, ListDashlet, AdminListDashlet, LinksListDashlet
from ecwsp.sis.dashboards import ReportBuilderDashlet
from .models import StudentAttendance
from report_builder.models import Report

from .models import StudentAttendance, CourseAttendance, AttendanceStatus, AttendanceLog
from ecwsp.schedule.models import Course
from ecwsp.sis.models import Student, UserPreference, Faculty, SchoolYear

import datetime

class AttendanceIndividualDashlet(Dashlet):
    template_name = 'attendance/individual_attendance_report.html'
    
class AttendanceSubmissionPercentageDashlet(Dashlet):
    template_name = 'attendance/teacher_submissions_percentage.html'
    
    # ripped directly from teacher_submissions in attendance/views.py. Create function or class for common use cases in future...
    def submission_percentage(self):
        """ Returns the percentage of teachers who have submitted attendance today. 
            e.g. 2/3 teachers submit attendance, thus 66%. """
        logs = AttendanceLog.objects.filter(date=datetime.date.today())
        homerooms = Course.objects.filter(homeroom=True)
        homerooms = homerooms.filter(marking_period__school_year__active_year=True)
        homerooms = homerooms.filter(coursemeet__day__contains=datetime.date.today().isoweekday()).distinct()
        submissions = []
        homeroom_count = 0
        submission_count = 0
        sub_percent = 0
        for homeroom in homerooms:
            homeroom_count += 1
            log = AttendanceLog.objects.filter(date=datetime.date.today(), course=homeroom)
            if log.count() > 0:
                submission_count += 1
        if submission_count > 0:
            sub_percent = int((submission_count/homeroom_count)*100)
        return sub_percent
		
    def get_context_data(self, **kwargs):
        context = super(AttendanceSubmissionPercentageDashlet, self).get_context_data(**kwargs)
        submission_percentage = self.submission_percentage()
        context = dict(context.items() + {
            'submission_percentage': submission_percentage,
        }.items())
        return context
		
				

class AttendanceDashlet(ListDashlet):
    model = StudentAttendance
    require_permissions = ('attendance.change_studentattendance',)
    fields = ('student', 'date', 'status')
    first_column_is_link = True
    count = 15


class AttendanceLinksListDashlet(LinksListDashlet):
    links = [
        {
            'text': 'Take Homeroom Attendance',
            'link': reverse('ecwsp.attendance.views.teacher_attendance'),
            'perm': ('attendance.take_studentattendance',),
        },
        {
            'text': 'Take Course Attendance',
            'link': reverse('ecwsp.attendance.views.select_course_for_attendance'),
            'perm': ('attendance.take_studentattendance',),
        },
        {
            'text': 'Reports',
            'link': reverse('ecwsp.attendance.views.attendance_report'),
            'perm': ('sis.reports',),
        },
    ]


class AttendanceReportBuilderDashlet(ReportBuilderDashlet):
    show_custom_link = '/admin/report_builder/report/?root_model__app_label=attendance'
    custom_link_text = "Reports"
    def get_context_data(self, **kwargs):
        self.queryset = Report.objects.filter(root_model__app_label='attendance')
        # Show only starred when there are a lot of reports
        if self.queryset.count() > self.count:
            self.queryset = self.queryset.filter(starred=self.request.user)
        return super(ReportBuilderDashlet, self).get_context_data(**kwargs)


class AttendanceAdminListDashlet(AdminListDashlet):
    require_permissions = ('attendance.change_studentattendance',)


class AttendanceDashboard(Dashboard):
    app = 'attendance'
    dashlets = [
        AttendanceSubmissionPercentageDashlet(title="Attendance Report"),
        AttendanceDashlet(title="Recent Attendance"),
        AttendanceLinksListDashlet(title="Links"),
        AttendanceReportBuilderDashlet(title="Reports",),
        AttendanceAdminListDashlet(title="Edit", app_label="attendance"),
    ]


dashboard = AttendanceDashboard()
