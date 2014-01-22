from django.conf.urls import patterns
from .views import transcript_nonofficial, photo_flash_card
from .views import user_preferences, view_student, ajax_include_deleted, import_naviance, increment_year, increment_year_confirm, StudentViewDashletView

urlpatterns = patterns('',
    (r'^reports/transcript_nonofficial/(?P<student_id>\d+)/$', transcript_nonofficial),
    (r'^flashcard/$', photo_flash_card),
    (r'^flashcard/(?P<year>\d+)/$', photo_flash_card),
    (r'^preferences/$', user_preferences),
    (r'^view_student/$', view_student),
    (r'^view_student/(?P<id>\d+)/$', view_student),
    (r'^ajax_view_student_dashlet/(?P<pk>\d+)/$', StudentViewDashletView.as_view()),
    (r'^ajax_include_deleted/$', ajax_include_deleted),
    (r'^student/naviance/$', import_naviance),
    (r'^increment_year/$', increment_year),
    (r'^increment_year_confirm/(?P<year_id>\d+)/$', increment_year_confirm),
)
