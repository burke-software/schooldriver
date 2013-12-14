from django.core.urlresolvers import reverse
from responsive_dashboard.dashboard import Dashboard, Dashlet, ListDashlet, AdminListDashlet, LinksListDashlet
from ecwsp.sis.dashboards import ReportBuilderDashlet
from ecwsp.counseling.models import StudentMeeting, ReferralForm
from report_builder.models import Report

import datetime

class CounselingLinksListDashlet(LinksListDashlet):
    links = [
        {
            'text': 'Submit Referral Form',
            'link': reverse('admin:counseling_referralform_add'),
            'perm': ('counseling.add_referralform',),
        },
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
    
    
class StudentMeetingDashlet(ListDashlet):
    model = StudentMeeting
    require_permissions = ('counseling.change_studentmeeting',)
    fields = ('display_students', 'date', 'category', 'reported_by')
    first_column_is_link = True
    count = 8
    columns = 2


class ReferralFormDashlet(ListDashlet):
    model = ReferralForm
    require_permissions = ('counseling.change_referralform',)
    fields = ('classroom_teacher', 'date', 'student',)
    first_column_is_link = True
    count = 8



class CounselingAdminListDashlet(AdminListDashlet):
    require_permissions = ('counseling.change_studentmeeting',)


class CounselingDashboard(Dashboard):
    app = 'counseling'
    dashlets = [
        CounselingLinksListDashlet(title="Links"),
        StudentMeetingDashlet(title="Student Meetings"),
        ReferralFormDashlet(title="Referrals"),
        CounselingAdminListDashlet(title="Edit", app_label="counseling"),
    ]


dashboard = CounselingDashboard()
