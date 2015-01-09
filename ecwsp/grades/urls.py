from django.conf.urls import patterns, url
from ecwsp.sis.views import SpaView
from . import views


urlpatterns = patterns('',
    url(r'^course_section/(?P<pk>\d+)/grades/$', views.CourseSectionGrades.as_view(), name="course-section-grades"),
    url(r'^view_comment_codes/$', views.view_comment_codes),
    url(r'^teacher_grade/download/(?P<id>\d+)/(?P<type>[a-z]+)$', views.teacher_grade_download),
    url(r'^teacher_grade/download/(?P<id>\d+)/$', views.teacher_grade_download),
)
