from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^enroll/(?P<id>\d+)$', schedule_enroll),
    (r'^teacher_grade/$', teacher_grade),
    (r'^teacher_grade/download/(?P<id>\d+)/(?P<type>[a-z]+)$', teacher_grade_download),
    (r'^teacher_grade/download/(?P<id>\d+)/$', teacher_grade_download),
    (r'^teacher_grade/upload/(?P<id>\d+)$', teacher_grade_upload),
    (r'^student_gradesheet/(?P<id>\d+)/$', student_gradesheet),
    (r'^student_gradesheet/(?P<id>\d+)/(?P<year_id>\d+)$', student_gradesheet),
    (r'^grade_analytics/$', grade_analytics),
    (r'^view_comment_codes/$', view_comment_codes),
    (r'^teacher_grade_submissions/$', teacher_grade_submissions),
)
