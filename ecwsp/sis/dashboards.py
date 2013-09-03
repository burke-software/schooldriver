from responsive_dashboard.dashboard import Dashboard, Dashlet, ListDashlet, RssFeedDashlet
from ecwsp.discipline.dashboards import DisciplineDashlet
from ecwsp.schedule.models import Course, MarkingPeriod
from report_builder.models import Report
import datetime



class ViewStudentDashlet(Dashlet):
    template = 'sis/view_student_dashlet.html'
    

class SisDisciplineDashlet(DisciplineDashlet):
    fields = ('show_students', 'infraction')
    columns = 1
    count = 5

class CourseDashlet(ListDashlet):
    model = Course
    fields = ('__str__', 'number_of_students',)
    order_by = ('-marking_period__start_date',)
    require_apps = ('ecwsp.schedule',)

class GradesDashlet(Dashlet):
    template = 'sis/grade_dashlet.html'
    require_apps = ('ecwsp.grades',)

    def _check_perm(self):
        user = self.request.user
        if user.has_perm('grades.check_own_grade') or user.has_perm('grades.change_grade'):
            return True
        return False

    def _render(self, **kwargs):
       today = datetime.date.today()
       marking_periods = MarkingPeriod.objects.filter(end_date__gte=today).order_by('start_date')
       if marking_periods:
           marking_period = marking_periods[0]
           due_in = (marking_period.end_date - today).days
       else:
           due_in = None
       self.template_dict['due_in'] = due_in
       return super(GradesDashlet, self)._render(**kwargs)


class ReportBuilderDashlet(ListDashlet):
    """ django-report-builder starred reports """
    model = Report
    fields = ('edit', 'name', 'download_xlsx')
    require_apps = ('report_builder',)
    require_permissions = ('report_builder.change_report')
    def _render(self, **kwargs):
        self.queryset = Report.objects.filter(starred=self.request.user)
        return super(ReportBuilderDashlet, self)._render(**kwargs)

class AnnouncementsDashlet(RssFeedDashlet):
    feed_url = 'http://feeds.feedburner.com/FeedForBurkeSoftwareAndConsultingLlc'
    more_link = 'https://plus.google.com/u/0/112784955559393766110'

class SisDashboard(Dashboard):
    app = 'sis'
    dashlets = [
        CourseDashlet(title="Courses For"),
        SisDisciplineDashlet(title="Latest Discipline Reports",),
        ViewStudentDashlet(title="Student"),
        GradesDashlet(title="Grades"),
        ReportBuilderDashlet(title="Starred Reports", model=Report),
        AnnouncementsDashlet(title="Announcements"),
    ]


dashboard = SisDashboard()
