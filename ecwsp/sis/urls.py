from django.conf.urls import patterns, url
from .views import transcript_nonofficial, photo_flash_card, thumbnail, paper_attendance
from .views import user_preferences, view_student, ajax_include_deleted, import_naviance, increment_year, increment_year_confirm, StudentViewDashletView
from responsive_dashboard.views import generate_dashboard

urlpatterns = patterns('',
    (r'^$', generate_dashboard, {'app_name': 'sis'}),
    (r'^reports/transcript_nonofficial/(?P<student_id>\d+)/$', transcript_nonofficial),
    (r'^flashcard/$', photo_flash_card),
    (r'^flashcard/(?P<year>\d+)/$', photo_flash_card),
    (r'^preferences/$', user_preferences),
    (r'^view_student/$', view_student),
    url(r'^view_student/(?P<id>\d+)/$', view_student, name="view-student"),
    (r'^ajax_view_student_dashlet/(?P<pk>\d+)/$', StudentViewDashletView.as_view()),
    (r'^ajax_include_deleted/$', ajax_include_deleted),
    (r'^student/naviance/$', import_naviance),
    (r'^increment_year/$', increment_year),
    (r'^increment_year_confirm/(?P<year_id>\d+)/$', increment_year_confirm),
    (r'^thumbnail/(?P<year>\d+)/$', thumbnail),
    (r'^paper_attendance/(?P<day>\d+)/$', paper_attendance),
)
