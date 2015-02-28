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
                        'ecwsp.work_study.models.WorkTeamUser',
                        'ecwsp.work_study.models.TimeSheet',
                        'ecwsp.work_study.models.TimeSheetPerformanceChoice',
                        'ecwsp.work_study.models.Contact',
                        'ecwsp.work_study.models.CompanyContract',
                        'ecwsp.work_study.models.CompanyHistory',
                        'ecwsp.work_study.models.ClientVisit',
                        'ecwsp.work_study.models.PaymentOption',
                        'ecwsp.work_study.models.StudentDesiredSkill',
                        'ecwsp.work_study.models.StudentFunctionalResponsibility',
                        'ecwsp.work_study.models.CompContract',
                        'ecwsp.work_study.models.MessageToSupervisor',
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
                'ecwsp.sis.models.PerCourseSectionCohort',
                'ecwsp.sis.models.ReasonLeft',
                'ecwsp.sis.models.Faculty',
                'ecwsp.sis.models.MessageToStudent',
                'ecwsp.sis.models.FamilyAccessUser',
                'ecwsp.sis.models.GradeScale',
            ),
        ))

        self.children.append(modules.ModelList(
            title=('Volunteer Tracking'),
            column=1,
            models=(
                'ecwsp.volunteer_track.*',
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
                'ecwsp.discipline.models.StudentDiscipline',
                'ecwsp.discipline.models.DisciplineAction',
                'ecwsp.discipline.models.PresetComment',
            ),
        ))

        self.children.append(modules.ModelList(
            title = 'Attendance',
            column=1,
            models=(
                'ecwsp.attendance.*',
            ),
        ))

        self.children.append(modules.ModelList(
            title='Courses and Grades',
            column=1,
            models=('ecwsp.schedule.*', 'ecwsp.benchmark_grade.*', 'ecwsp.benchmarks.*'),
        ))

        self.children.append(modules.ModelList(
            title='Standard Tests',
            column=1,
            models=('ecwsp.standard_test.*',),
        ))

        self.children.append(modules.ModelList(
            title='Admissions',
            column=1,
            models=('ecwsp.admissions.*',),
        ))

        self.children.append(modules.ModelList(
            title='Counseling',
            column=1,
            models=('ecwsp.counseling.*',),
        ))

        self.children.append(modules.ModelList(
            title='Alumni',
            column=1,
            models=('ecwsp.alumni.*',),
        ))

        self.children.append(modules.AppList(
            title='Administration',
            column=2,
            models=(
                'django.contrib.*',
                'ecwsp.administration.*',
                'constance.*',
                'ecwsp.engrade_sync.*',
                'ldap_groups.*',
                'google_auth.*',
            )
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            title='Recent Actions',
            column=2,
            limit=5
        ))

        self.children.append(modules.LinkList(
            column=2,
            children=(
                {
                    'title': 'Schooldriver Manual',
                    'url': 'http://docs.schooldriver.org',
                    'external': True,
                },
                {
                    'title': 'Schooldriver Community',
                    'url': 'http://github.com/burke-software/django-sis',
                    'external': True,
                },
                {
                    'title': 'Burke Software',
                    'url': 'http://burkesoftware.com',
                    'external': True,
                },
            )
        ))
