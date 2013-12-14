from django.core.urlresolvers import reverse
from responsive_dashboard.dashboard import Dashboard, Dashlet, ListDashlet, LinksListDashlet, AdminListDashlet
from ecwsp.discipline.models import StudentDiscipline
from report_builder.models import Report

import datetime

class DisciplineLinksDashlet(LinksListDashlet):
    links = [
        {
            'text': 'NOT Discipline actions',
            'link': reverse('ecwsp.attendance.views.teacher_attendance'),
            'perm': ('attendance.take_studentattendance',),
        },
        {
            'text': 'NOT Infractions',
            'link': reverse('ecwsp.attendance.views.select_course_for_attendance'),
            'perm': ('attendance.take_studentattendance',),
        },
        {
            'text': 'NOT Student Discipline',
            'link': reverse('ecwsp.attendance.views.attendance_report'),
            'perm': ('sis.reports',),
        },
        {
            'text': 'NOT Counseling',
            'link': reverse('ecwsp.attendance.views.attendance_report'),
            'perm': ('sis.reports',),
        },
    ]
    
    
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
    def _render(self, **kwargs):
        self.queryset = Report.objects.filter(root_model__app_label='discipline')
        # Show only starred when there are a lot of reports
        if self.queryset.count() > self.count:
            self.queryset = self.queryset.filter(starred=self.request.user)
        return super(ReportBuilderDashlet, self)._render(**kwargs)


# this is not a dashlet shown on default
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


class DisciplineDashboard(Dashboard):
    app = 'discipline'
    dashlets = [
        DisciplineLinksDashlet(title="Links"),
        DisciplineDashlet(title="Latest Discipline"),
        ReportBuilderDashlet(title="Reports",),
        AdminListDashlet(title="Edit", app_label="discipline"),
    ]


dashboard = DisciplineDashboard()
