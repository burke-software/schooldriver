from responsive_dashboard.dashboard import Dashboard, Dashlet, ListDashlet, AdminListDashlet, LinksListDashlet
from django.contrib.admin.models import LogEntry
from django.contrib import messages
from django.core.urlresolvers import reverse
from report_builder.models import Report
from ecwsp.sis.dashboards import ReportBuilderDashlet
from ecwsp.sis.models import Faculty
from .models import Test

import datetime

class OmrReportBuilderDashlet(ReportBuilderDashlet):
    """ django-report-builder starred reports """
    show_custom_link = '/admin/report_builder/report/?root_model__app_label=omr'
    custom_link_text = "OMR Reports"
    def get_context_data(self, **kwargs):
        self.queryset = Report.objects.filter(root_model__app_label='omr')
        # Show only starred when there are a lot of reports
        if self.queryset.count() > self.count:
            self.queryset = self.queryset.filter(starred=self.request.user)
        return super(ReportBuilderDashlet, self).get_context_data(**kwargs)


class OmrMyTestsDashlet(Dashlet):
    """ Show's a teachers OMR tests """
    template_name = "/omr/my_tests_dashlet.html"
    columns = 3
    responsive = False
    required_perms = ('omr.teacher_test',)
    
    def get_context_data(self, **kwargs):
        context = super(OmrMyTestsDashlet, self).get_context_data(**kwargs)
        try:
            teacher = Faculty.objects.get(username=self.request.user.username)
            tests = Test.objects.filter(teachers=teacher)
            context = dict(context.items() + {
                'tests': tests,
            }.items())
        except:
            messages.warning(self.request, "You are not a teacher!")
        return context
    

class OmrDashboard(Dashboard):
    app = 'omr'
    dashlets = [
        OmrMyTestsDashlet(title="My Tests"),
        AdminListDashlet(title="OMR Admin", app_label="omr"),
        OmrReportBuilderDashlet(title="Report Builder"),
    ]


dashboard = OmrDashboard()
