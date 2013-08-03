from responsive_dashboard.dashboard import Dashboard, Dashlet, ListDashlet, AdminListDashlet
from ecwsp.work_study.models import TimeSheet
from report_builder.models import Report

import datetime

class TimeSheetDashlet(ListDashlet):
    model = TimeSheet
    require_permissions = ('work_study.change_timesheet',)
    fields = ('student', 'date', 'performance', 'approved', 'supervisor_Comment_Brief', 'student_Accomplishment_Brief')
    order_by = ('-date',)
    columns = 3
    first_column_is_link = True


class ReportBuilderDashlet(ListDashlet):
    """ django-report-builder starred reports """
    model = Report
    count = 10
    show_custom_link = '/admin/report_builder/report/?root_model__app_label=work_study'
    custom_link_text = "Work Study Reports"
    show_change = False
    fields = ('edit', 'name', 'download_xlsx')
    require_apps = ('report_builder',)
    require_permissions = ('report_builder.change_report')
    extra_links = {
        'Premade Reports': ''
    }
    def _render(self, **kwargs):
        self.queryset = Report.objects.filter(root_model__app_label='work_study')
        # Show only starred when there are a lot of reports
        if self.queryset.count() > self.count:
            self.queryset = self.queryset.filter(starred=self.request.user)
        return super(ReportBuilderDashlet, self)._render(**kwargs)


class WorkStudyAttendanceDashlet(Dashlet):
    template = "/work_study/cwsp_attendance_dashlet.html"
    require_permissions = ('work_study.change_attandance',)



class WorkStudyDashboard(Dashboard):
    app = 'work_study'
    dashlets = [
        ReportBuilderDashlet(title="Reports",),
        TimeSheetDashlet(title="Time Sheets",),
        WorkStudyAttendanceDashlet(title="Work Study Attendance"),
        AdminListDashlet(title="Edit Work Study", app_label="work_study")
    ]


dashboard = WorkStudyDashboard()
