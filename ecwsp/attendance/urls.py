from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^teacher_submissions/$', teacher_submissions),
    (r'^studentattendance/report/$', attendance_report),
    (r'^studentattendance/student/(?P<id>\d+)/$', attendance_student),
    (r'^teacher_attendance/$', teacher_attendance),
    (r'^teacher_attendance/$', teacher_attendance),
    (r'^teacher_attendance/(?P<course>\d+)/$', teacher_attendance),
)