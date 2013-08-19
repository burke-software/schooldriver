from django.contrib import messages
from responsive_dashboard.dashboard import Dashboard, Dashlet, ListDashlet, AdminListDashlet
from ecwsp.sis.models import SchoolYear
from ecwsp.work_study.models import TimeSheet
from ecwsp.work_study.forms import ReportBuilderForm, ReportTemplateForm
from report_builder.models import Report

import datetime

class TimeSheetDashlet(ListDashlet):
    model = TimeSheet
    require_permissions = ('work_study.change_timesheet',)
    fields = ('student', 'date', 'performance', 'approved', 'supervisor_Comment_Brief', 'student_Accomplishment_Brief')
    order_by = ('-date',)
    columns = 2
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
    def _render(self, **kwargs):
        self.queryset = Report.objects.filter(root_model__app_label='work_study')
        # Show only starred when there are a lot of reports
        if self.queryset.count() > self.count:
            self.queryset = self.queryset.filter(starred=self.request.user)
        return super(ReportBuilderDashlet, self)._render(**kwargs)


class WorkStudyAttendanceDashlet(Dashlet):
    template = "/work_study/cwsp_attendance_dashlet.html"
    require_permissions = ('work_study.change_attendance',)


class WorkStudyReportsDashlet(Dashlet):
    template = "/work_study/reports_dashlet.html"
    columns = 2
    require_permissions = ('work_study.change_studentworker',)
    
    def _render(self, **kwargs):
        try:
            active_year = SchoolYear.objects.get(active_year=True)
        except SchoolYear.DoesNotExist:
            messages.warning(self.request, 'No Active Year Set, please create an active year!')
            return HttpResponseRedirect('/')
    
        form = ReportBuilderForm(initial={'custom_billing_begin':active_year.start_date,'custom_billing_end':active_year.end_date})
        template_form = ReportTemplateForm()
        self.template_dict = dict(self.template_dict.items() + {
            'form': form,
            'template_form': template_form,
        }.items())
        return super(WorkStudyReportsDashlet, self)._render(**kwargs)


class WorkStudyDashboard(Dashboard):
    app = 'work_study'
    dashlets = [
        ReportBuilderDashlet(title="Reports",),
        WorkStudyReportsDashlet(title="Work Study Reports"),
        TimeSheetDashlet(title="Time Sheets",),
        WorkStudyAttendanceDashlet(title="Work Study Attendance"),
        AdminListDashlet(title="Edit Work Study", app_label="work_study"),
    ]


dashboard = WorkStudyDashboard()
