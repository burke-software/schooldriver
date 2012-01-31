from django.conf.urls.defaults import *
from views import *
from report import *

urlpatterns = patterns('',
    (r'^get_student/(?P<id>\d+)/$', student_page_redirect),
    (r'^reports/$', school_report_builder_view),
    (r'^reports/transcript_nonofficial/(?P<id>\d+)/$', transcript_nonofficial),
    (r'^flashcard/$', photo_flash_card),
    (r'^flashcard/(?P<year>\d+)/$', photo_flash_card),
    (r'^grade_report/$', grade_report),
    (r'^import/$', import_everything),
    (r'^preferences/$', user_preferences),
    (r'^view_student/$', view_student),
    (r'^view_student/(?P<id>\d+)/$', view_student),
    (r'^student/naviance/$', import_naviance),
)
