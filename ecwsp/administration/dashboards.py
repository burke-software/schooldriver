from responsive_dashboard.dashboard import Dashboard, Dashlet, ListDashlet, AdminListDashlet, LinksListDashlet, dashboards
from django.contrib.admin.models import LogEntry
from django.core.urlresolvers import reverse
from report_builder.models import Report
from ecwsp.sis.dashboards import ReportBuilderDashlet


import datetime

class LogEntryDashlet(ListDashlet):
    model = LogEntry
    fields = ('user', 'action_time', 'content_type',  'object_repr', 'action_flag', 'change_message')
    columns = 2
    count = 8
    require_permissions_or = ('admin.change_log', 'admin.view_log')
    order_by = ('-action_time',)

class EngradeSyncListDashlet(AdminListDashlet):
    required_apps = ('engrade_sync',)
    require_permissions = ('engrade_sync.course_sync',)
    

# Yes I suck and deserve killed for this
# Don't freak the fuck out when reverse fails
try:
    annoying_link = reverse('ecwsp.engrade_sync.views.setup')
except:
    annoying_link = ""
class AdministrationLinksListDashlet(LinksListDashlet):
    links = [
        {
            'text': 'School Import',
            'link': reverse('simple_import.views.start_import'),
            'desc': '',
            'perm': ('simple_import.change_importlog',),
        },
                {
            'text': 'Configuration',
            'link': reverse('admin:administration_configuration_changelist'),
            'desc': '',
            'perm': ('administration.change_configuration',),
        },
        {
            'text': 'Custom Fields',
            'link': reverse('admin:custom_field_customfield_changelist'),
            'desc': '',
            'perm': ('custom_field.change_custom_field',),
        },
        {
            'text': 'Canvas Sync',
            'link': '/canvas_sync/setup',
            'desc': '',
            'perm': ('sis.reports',),
        },
        {
            'text': 'Engrade Sync',
            'link': annoying_link,
            'perm': ('sis.reports',),
            'required_apps': ('ecwsp.engrade_sync',),
        },
        {
            'text': 'Change School Year',
            'link': reverse('ecwsp.sis.views.increment_year'),
            'desc': '',
            'perm': ('sis.change_student', 'sis.change_schoolyear'),
        },
    ]


class AdminDashboard(Dashboard):
    app = 'administration'
    dashlets = [
        LogEntryDashlet(title="Latest Actions"),
        AdminListDashlet(title="User Management", app_label="auth"),
        AdminListDashlet(title="SIS Management", app_label="administration"),
        EngradeSyncListDashlet(title="Engrade Sync", app_label="engrade_sync"),
        AdministrationLinksListDashlet(title="Links"),
        ReportBuilderDashlet(title="Report Builder"),
    ]


dashboards.register('administration', AdminDashboard)
