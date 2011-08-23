from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.modules import DashboardModule

from ecwsp.sis.forms import *

class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for ecwsp.
    """
    def __init__(self, **kwargs):
        Dashboard.__init__(self, **kwargs)
        
        self.children.append(modules.Group(
            column=1,
            title='CWSP',
            children=[
                modules.ModelList(
                    models=(
                        'ecwsp.work_study.models.StudentWorker',
                        'ecwsp.work_study.models.StudentInteraction',
                        'ecwsp.work_study.models.Attendance',
                        'ecwsp.work_study.models.PickupLocation',
                        'ecwsp.work_study.models.CraContact',
                        'ecwsp.work_study.models.Personality',
                        'ecwsp.work_study.models.Handout33',
                        'ecwsp.work_study.models.PresetComment',
                        'ecwsp.work_study.models.AttendanceFee',
                        'ecwsp.work_study.models.AttendanceReason',
                    ),
                ),
                modules.ModelList(
                    title="Company Data",
                    models=(
                        'ecwsp.work_study.models.Company',
                        'ecwsp.work_study.models.WorkTeam',
                        'ecwsp.work_study.models.TimeSheet',
                        'ecwsp.work_study.models.Contact',
                        'ecwsp.work_study.models.CompanyContract',
                        'ecwsp.work_study.models.CompanyHistory',
                        'ecwsp.work_study.models.ClientVisit',
                        'ecwsp.work_study.models.PaymentOption',
                        'ecwsp.work_study.models.StudentDesiredSkill',
                        'ecwsp.work_study.models.StudentFunctionalResponsibility',
                        'ecwsp.work_study.models.CompContract',
                    ),
                ),
            ]
        ))
        
        self.children.append(modules.ModelList(
            title=_('School Information'),
            column=1,
            models=(
                'ecwsp.sis.models.SchoolYear',
                'ecwsp.sis.models.Student',
                'ecwsp.sis.models.EmergencyContact',
                'ecwsp.sis.models.Cohort',
                'ecwsp.sis.models.ReasonLeft',
                'ecwsp.sis.models.Faculty',
            ),
        ))

        self.children.append(modules.ModelList(
            title=('Volunteer Tracking'),
            column=1,
            models=('ecwsp.volunteer_track.models.Site',
                'ecwsp.volunteer_track.models.SiteSupervisor',
                'ecwsp.volunteer_track.models.Hours',
                'ecwsp.volunteer_track.models.Volunteer',
            ),
        ))

        self.children.append(modules.ModelList(
            title=_('Attendance'),
            column=1,
            models=('ecwsp.sis.models.StudentAttendance',
                    'ecwsp.sis.models.AttendanceStatus',
                    'ecwsp.sis.models.ASPAttendance',
                ),
        ))
        
        self.children.append(modules.ModelList(
            title = 'Discipline',
            column=1,
            models=(
                'ecwsp.sis.models.StudentDiscipline',
                'ecwsp.sis.models.DisciplineAction',
                'ecwsp.sis.models.PresetComment',
            ),
        ))
    
        self.children.append(modules.ModelList(
            title='Courses and Grades',
            column=1,
            models=('ecwsp.schedule.*',),
        ))
        
        self.children.append(modules.ModelList(
            title='Admissions',
            column=1,
            models=('ecwsp.admissions.*',),
        ))
        
        self.children.append(modules.ModelList(
            title='Alumni',
            column=1,
            models=('ecwsp.alumni.*',),
        ))
        
        self.children.append(modules.ModelList(
            title='OpenMetricRecognition',
            column=1,
            models=('ecwsp.omr.*',),
        ))
        
        self.children.append(modules.AppList(
            title='Administration',
            column=2,
            models=(
                'django.contrib.*',
                'ecwsp.sis.models.ReportField',
                'ecwsp.administration.*',
                'ecwsp.engrade_sync.*',
                'ldap_groups.*',
            )
        ))
        
        # append a recent actions module
        self.children.append(modules.RecentActions(
            title='Recent Actions',
            column=2,
            limit=5
        ))
        
        self.children.append(modules.Feed(
            title='Latest SWORD News',
            column=2,
            feed_url='https://sites.google.com/a/cristoreyny.org/sword-wiki/news/posts.xml',
            limit=2
        ))
        
        self.children.append(modules.LinkList(
            column=2,
            children=(
                {
                    'title': 'SWORD Wiki and Manual',
                    'url': 'https://sites.google.com/a/cristoreyny.org/sword-wiki/',
                    'external': True,
                },
                {
                    'title': 'Student Worker Relation Database Community',
                    'url': 'http://code.google.com/p/student-worker-relational-database/',
                    'external': True,
                },
                {
                    'title': 'Burke Software',
                    'url': 'http://burkesoftware.com',
                    'external': True,
                },
            )
        ))
