from django.conf.urls import *
from views import *

urlpatterns = patterns('',
    (r'^teacher_grade/$', teacher_grade),
    (r'^teacher_grade_submissions/$', teacher_grade_submissions),
    (r'^teacher_grade/download/(?P<id>\d+)/(?P<type>[a-z]+)$', teacher_grade_download),
    (r'^teacher_grade/download/(?P<id>\d+)/$', teacher_grade_download),
    (r'^teacher_grade/upload/(?P<id>\d+)$', teacher_grade_upload),
    (r'^student_gradesheet/(?P<id>\d+)/$', student_gradesheet),
    (r'^student_gradesheet/(?P<id>\d+)/(?P<year_id>\d+)$', student_gradesheet),
    (r'^view_comment_codes/$', view_comment_codes),
    (r'^select_grade_method/$', select_grade_method),
)
