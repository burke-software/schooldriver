from django.conf.urls import patterns
from views import student_page_redirect, school_report_builder_view, transcript_nonofficial, photo_flash_card, grade_report
from views import import_everything, user_preferences, view_student, ajax_include_deleted, import_naviance, increment_year_or_graduate

urlpatterns = patterns('',
    (r'^get_student/(?P<student_id>\d+)/$', student_page_redirect),
    (r'^reports/$', school_report_builder_view),
    (r'^reports/transcript_nonofficial/(?P<student_id>\d+)/$', transcript_nonofficial),
    (r'^flashcard/$', photo_flash_card),
    (r'^flashcard/(?P<year>\d+)/$', photo_flash_card),
    (r'^grade_report/$', grade_report),
    (r'^import/$', import_everything),
    (r'^preferences/$', user_preferences),
    (r'^view_student/$', view_student),
    (r'^view_student/(?P<id>\d+)/$', view_student),
    (r'^ajax_include_deleted/$', ajax_include_deleted),
    (r'^student/naviance/$', import_naviance),
    (r'^increment_year_or_graduate/$', increment_year_or_graduate),
)
