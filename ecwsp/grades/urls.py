from django.conf.urls import *
from django.views.generic import TemplateView
from ecwsp.grades import views


urlpatterns = patterns('',
    (r'^teacher_grade/$', views.teacher_grade),
    (r'^teacher_grade_submissions/$', views.teacher_grade_submissions),
    (r'^teacher_grade/download/(?P<id>\d+)/(?P<type>[a-z]+)$', views.teacher_grade_download),
    (r'^teacher_grade/download/(?P<id>\d+)/$', views.teacher_grade_download),
    url(r'^student_grades/(?P<pk>\d+)/$', views.StudentGradesheet.as_view(), name="student-grades"),
    url(r'^student_grades/(?P<pk>\d+)/(?P<year_id>\d+)/$', views.StudentGradesheet.as_view()),
    (r'^view_comment_codes/$', views.view_comment_codes),
    (r'^select_grade_method/$', views.select_grade_method),
    url(r'^course_section_grades/(?P<pk>\d+)/$', views.CourseSectionGrades.as_view(), name="course-section-grades"),
)
