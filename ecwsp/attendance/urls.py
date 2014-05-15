from django.conf.urls import *
from ecwsp.attendance import views

urlpatterns = patterns('',
    (r'^teacher_submissions/$', views.teacher_submissions),
    (r'^studentattendance/report/$', views.attendance_report),
    (r'^studentattendance/student/(?P<id>\d+)/$', views.attendance_student),
    (r'^studentattendance/add_multiple/$', views.add_multiple),
    (r'^teacher_attendance/$', views.teacher_attendance),
    (r'^teacher_attendance/$', views.teacher_attendance),
    (r'^teacher_attendance/(?P<course>\d+)/$', views.teacher_attendance),
    (r'^course_attendance/$', views.select_course_for_attendance),
    (r'^course_attendance/(?P<course_id>\d+)/$', views.course_attendance),
    (r'^daily_attendance_report/$', views.daily_attendance_report_wrapper),
)
