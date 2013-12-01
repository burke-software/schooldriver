from django.core.urlresolvers import reverse
from responsive_dashboard.dashboard import Dashboard, Dashlet, ListDashlet, AdminListDashlet, LinksListDashlet
from ecwsp.sis.dashboards import ReportBuilderDashlet
from .models import StudentAttendance
from report_builder.models import Report

import datetime

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
    def _render(self, **kwargs):
        self.queryset = Report.objects.filter(root_model__app_label='attendance')
        # Show only starred when there are a lot of reports
        if self.queryset.count() > self.count:
            self.queryset = self.queryset.filter(starred=self.request.user)
        return super(ReportBuilderDashlet, self)._render(**kwargs)


class AttendanceAdminListDashlet(AdminListDashlet):
    require_permissions = ('attendance.change_studentattendance',)


class AttendanceDashboard(Dashboard):
    app = 'attendance'
    dashlets = [
        AttendanceDashlet(title="Recent Attendance"),
        AttendanceLinksListDashlet(title="Links"),
        AttendanceReportBuilderDashlet(title="Reports",),
        AttendanceAdminListDashlet(title="Edit", app_label="attendance"),
    ]


dashboard = AttendanceDashboard()
