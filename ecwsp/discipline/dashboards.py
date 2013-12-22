from django.core.urlresolvers import reverse
from responsive_dashboard.dashboard import Dashboard, Dashlet, ListDashlet, LinksListDashlet, AdminListDashlet
from ecwsp.discipline.models import StudentDiscipline
from responsive_dashboard.dashboard import Dashboard, Dashlet, ListDashlet, AdminListDashlet
from .models import StudentDiscipline
from report_builder.models import Report

import datetime
    
    
class DisciplineDashlet(ListDashlet):
    model = StudentDiscipline
    first_column_is_link = True
    fields = ('show_students', 'infraction', 'comment_brief',  'date')
    columns = 2
    count = 10 
    order_by = ('-date',)
    require_apps = ('ecwsp.discipline',)


class ReportBuilderDashlet(ListDashlet):
    """ django-report-builder starred reports """
    model = Report
    count = 10
    show_custom_link = '/admin/report_builder/report/?root_model__app_label=discipline'
    custom_link_text = "Discipline Reports"
    show_change = False
    fields = ('edit', 'name', 'download_xlsx')
    require_apps = ('report_builder',)
    require_permissions = ('report_builder.change_report')

    def get_context_data(self, **kwargs):
        self.queryset = Report.objects.filter(root_model__app_label='discipline')
        # Show only starred when there are a lot of reports
        if self.queryset.count() > self.count:
            self.queryset = self.queryset.filter(starred=self.request.user)
        return super(ReportBuilderDashlet, self).get_context_data(**kwargs)


# this is not a dashlet shown on default
class AdmissionsReportsDashlet(Dashlet):
    template_name = "/admissions/reports_dashlet.html"
    columns = 1
    require_permissions = ('admissions.change_applicant',)
    
    def get_context_data(self, **kwargs):   
        context = super(AdmissionsReportsDashlet, self).get_context_data(**kwargs)
        report_form = ReportForm()
        template_form = TemplateReportForm()
        context = dict(context.items() + {
            'report_form': report_form,
            'template_form': template_form,
        }.items())
        return context


class DisciplineDashboard(Dashboard):
    app = 'discipline'
    dashlets = [
        DisciplineDashlet(title="Latest Discipline"),
        ReportBuilderDashlet(title="Reports",),
        AdminListDashlet(title="Edit", app_label="discipline"),
    ]


dashboard = DisciplineDashboard()
