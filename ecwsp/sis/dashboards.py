from responsive_dashboard.dashboard import Dashboard, Dashlet, ListDashlet, RssFeedDashlet
from ecwsp.discipline.dashboards import DisciplineDashlet
from ecwsp.schedule.models import Course, MarkingPeriod, CourseSection
from .models import SchoolYear
from ecwsp.attendance.models import StudentAttendance, CourseSectionAttendance, AttendanceStatus, AttendanceLog
from report_builder.models import Report
import datetime

from django.core.urlresolvers import reverse
from responsive_dashboard.dashboard import AdminListDashlet, LinksListDashlet, dashboards
from ecwsp.sis.models import Student, UserPreference, Faculty


class ViewStudentDashlet(Dashlet):
    template_name = 'sis/view_student_dashlet.html'


class EventsDashlet(Dashlet):
    template_name = 'sis/events_dashlet.html'

    def get_context_data(self, **kwargs):
        context = super(EventsDashlet, self).get_context_data(**kwargs)
        today = datetime.date.today()
        news_alerts = []

        try:
            school_year = SchoolYear.objects.filter(active_year=True)[0]
        except IndexError:
            school_year = None

        marking_periods = MarkingPeriod.objects.filter(end_date__gte=today).order_by('start_date')
        if marking_periods:
            marking_period = marking_periods[0]
        else:
            marking_period = None

        future_marking_periods = marking_periods.filter(start_date__gte=today)
        if future_marking_periods:
            next_marking_period = future_marking_periods[0]
        else:
            next_marking_period = None

        new_year = None
        if school_year:
            date_delta = school_year.start_date - today
            date_delta = date_delta.days
            if date_delta <= 0 and date_delta > -30:
                news_alerts += ["A new school year has started on {}.".format(school_year.start_date)]
            elif date_delta < 60:
                news_alerts += ['A new school year will start on {}.'.format(school_year.start_date)]


        context = dict(context.items() + {
            'marking_period': marking_period,
            'next_marking_period': next_marking_period,
            'school_year': school_year,
            'news_alerts': news_alerts,
        }.items())
        return context




class ReportBuilderDashlet(ListDashlet):
    """ django-report-builder starred reports """
    model = Report
    fields = ('edit', 'name', 'download_xlsx')
    require_apps = ('report_builder',)
    require_permissions = ('report_builder.change_report',)

    def get_context_data(self, **kwargs):
        context = super(ReportBuilderDashlet, self).get_context_data(**kwargs)
        self.queryset = Report.objects.filter(starred=self.request.user)
        return context

#class AnnouncementsDashlet(RssFeedDashlet):
#    feed_url = 'http://feeds.feedburner.com/FeedForBurkeSoftwareAndConsultingLlc'
#    more_link = 'https://plus.google.com/u/0/112784955559393766110'


class AttendanceIndividualDashlet(Dashlet):
    template_name = 'attendance/individual_attendance_report.html'

class AttendanceSubmissionPercentageDashlet(Dashlet):
    template_name = 'attendance/teacher_submissions_percentage.html'

    # Create function or class for common use cases in future...
    def submission_percentage(self):
        """ Returns the percentage of teachers who have submitted attendance today.
            e.g. 2/3 teachers submit attendance, thus 66%. """
        logs = AttendanceLog.objects.filter(date=datetime.date.today())
        homerooms = CourseSection.objects.filter(course__homeroom=True)
        homerooms = homerooms.filter(marking_period__school_year__active_year=True)
        homerooms = homerooms.filter(coursemeet__day__contains=datetime.date.today().isoweekday()).distinct()
        submissions = []
        homeroom_count = 0
        submission_count = 0
        sub_percent = 0
        for homeroom in homerooms:
            homeroom_count += 1
            log = AttendanceLog.objects.filter(date=datetime.date.today(), course_section=homeroom)
            if log.count() > 0:
                submission_count += 1
        if submission_count > 0:
            sub_percent = int((submission_count/homeroom_count)*100)
        return sub_percent

    def get_context_data(self, **kwargs):
        context = super(AttendanceSubmissionPercentageDashlet, self).get_context_data(**kwargs)
        submission_percentage = self.submission_percentage()
        context = dict(context.items() + {
            'submission_percentage': submission_percentage,
        }.items())
        return context



class AttendanceDashlet(ListDashlet):
    model = StudentAttendance
    require_permissions = ('attendance.change_studentattendance',)
    fields = ('student', 'date', 'status')
    first_column_is_link = True
    count = 15


class AttendanceLinksListDashlet(LinksListDashlet):
    links = [
        {
            'text': 'Take homeroom attendance',
            'link': reverse('ecwsp.attendance.views.teacher_attendance'),
            'perm': ('attendance.take_studentattendance',),
        },
        {
            'text': 'Take course section attendance',
            'link': reverse('ecwsp.attendance.views.select_course_section_for_attendance'),
            'perm': ('attendance.take_studentattendance',),
        },
        {
            'text': 'Reports',
            'link': reverse('ecwsp.attendance.views.attendance_report'),
            'perm': ('sis.reports',),
        },
    ]


class AttendanceReportBuilderDashlet(ReportBuilderDashlet):
    show_custom_link = '/admin/report_builder/report/?root_model__app_label=attendance'
    custom_link_text = "Reports"
    def get_context_data(self, **kwargs):
        self.queryset = Report.objects.filter(root_model__app_label='attendance')
        # Show only starred when there are a lot of reports
        if self.queryset.count() > self.count:
            self.queryset = self.queryset.filter(starred=self.request.user)
        return super(ReportBuilderDashlet, self).get_context_data(**kwargs)


class AttendanceAdminListDashlet(AdminListDashlet):
    require_permissions = ('attendance.change_studentattendance',)

class SisDashboard(Dashboard):
    app = 'sis'
    dashlets = [
        EventsDashlet(title="School Events"),
        ViewStudentDashlet(title="Student"),
        ReportBuilderDashlet(title="Starred Reports", model=Report),
        #AnnouncementsDashlet(title="Announcements"),
        AttendanceSubmissionPercentageDashlet(title="Attendance Report"),
        AttendanceDashlet(title="Recent Attendance"),
        AttendanceLinksListDashlet(title="Links"),
        AttendanceReportBuilderDashlet(title="Attendance Reports",),
        AttendanceAdminListDashlet(title="Attendance", app_label="attendance"),
        AdminListDashlet(title="School Information", app_label="sis"),
    ]


dashboards.register('sis', SisDashboard)
