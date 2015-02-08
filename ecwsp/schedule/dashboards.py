from responsive_dashboard.dashboard import Dashboard, Dashlet, ListDashlet, RssFeedDashlet, AdminListDashlet, dashboards
from .models import Course, CourseSection, MarkingPeriod
from ecwsp.attendance.models import CourseSectionAttendance
import datetime

class CourseSectionDashlet(ListDashlet):
    model = CourseSection
    fields = ('__str__', 'number_of_students',)
    require_apps = ('ecwsp.schedule',)


class GradesDashlet(Dashlet):
    template_name = 'schedule/grade_dashlet.html'
    require_apps = ('ecwsp.grades',)
    require_permissions_or = ('grades.check_own_grade', 'grades.change_grade',)

    def get_context_data(self, **kwargs):
        context = super(GradesDashlet, self).get_context_data(**kwargs)
        today = datetime.date.today()
        marking_periods = MarkingPeriod.objects.filter(end_date__gte=today).order_by('start_date')
        if marking_periods:
            marking_period = marking_periods[0]
            due_in = (marking_period.end_date - today).days
        else:
            due_in = None
        context['due_in'] = due_in
        return context


class AttendanceDashlet(Dashlet):
    template_name = 'attendance/course_attendance_dashlet.html'
    model = CourseSectionAttendance
    require_apps = ('ecwsp.attendance',)


class CourseDetailDashlet(Dashlet):
    template_name = 'schedule/course_detail_dashlet.html'
    require_permissions_or = ('grades.check_own_grade', 'schedule.change_course',)

    def get_context_data(self, **kwargs):
        context = super(CourseDetailDashlet, self).get_context_data(**kwargs)
        courses = Course.objects.filter(
            sections__marking_period__school_year__active_year=True)
        if self.request.user.has_perm('schedule.change_course'):
            context['change_course'] = True
        else:
            context['change_course'] = False
            courses = courses.filter(sections__teachers=self.request.user)
        context['courses'] = courses

        return context



class CourseDashboard(Dashboard):
    app = 'schedule'
    dashlets = [
        CourseSectionDashlet(title="Course Sections"),
        #CourseDetailDashlet(title="Courses"),
        GradesDashlet(title="Grades"),
        AdminListDashlet(title="Schedule", app_label="schedule"),
        AdminListDashlet(title="GradesList", verbose_name="Grades", app_label="grades"),
        AttendanceDashlet(title="Attendance Reports")
    ]

dashboards.register('schedule', CourseDashboard)
