from responsive_dashboard.dashboard import Dashboard, Dashlet, ListDashlet, AdminListDashlet
from ecwsp.admissions.models import Applicant
from ecwsp.admissions.forms import ReportForm, TemplateReportForm
from ecwsp.sis.models import SchoolYear
from report_builder.models import Report

import datetime

class ApplicantDashlet(ListDashlet):
    model = Applicant
    require_permissions = ('admissions.change_applicant',)
    fields = ('__str__', 'date_added', 'level', 'from_online_inquiry')
    order_by = ('-date_added',)
    columns = 2
    first_column_is_link = True


class ReportBuilderDashlet(ListDashlet):
    """ django-report-builder starred reports """
    model = Report
    count = 10
    show_custom_link = '/admin/report_builder/report/?root_model__app_label=admissions'
    custom_link_text = "Admissions Reports"
    show_change = False
    fields = ('edit', 'name', 'download_xlsx')
    require_apps = ('report_builder',)
    require_permissions = ('report_builder.change_report')
    def _render(self, **kwargs):
        self.queryset = Report.objects.filter(root_model__app_label='admissions')
        # Show only starred when there are a lot of reports
        if self.queryset.count() > self.count:
            self.queryset = self.queryset.filter(starred=self.request.user)
        return super(ReportBuilderDashlet, self)._render(**kwargs)


class AdmissionsReportsDashlet(Dashlet):
    template = "/admissions/reports_dashlet.html"
    columns = 1
    require_permissions = ('admissions.change_applicant',)
    
    def _render(self, **kwargs):   
        report_form = ReportForm()
        template_form = TemplateReportForm()
        self.template_dict = dict(self.template_dict.items() + {
            'report_form': report_form,
            'template_form': template_form,
        }.items())
        return super(AdmissionsReportsDashlet, self)._render(**kwargs)


class AdmissionsDashboard(Dashboard):
    app = 'admissions'
    dashlets = [
        ApplicantDashlet(title="Newest Applicants"),
        ReportBuilderDashlet(title="Reports",),
        AdminListDashlet(title="Edit", app_label="admissions"),
        AdmissionsReportsDashlet(title="Admissions Reports"),
    ]


dashboard = AdmissionsDashboard()
