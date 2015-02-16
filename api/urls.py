from django.conf.urls import patterns, url
from ecwsp.grades.api_views import SetGradeView, SetFinalGradeView


urlpatterns = patterns('',
    url(r'^set_grade/$', SetGradeView.as_view(), name="api-set-grade"),
    url(r'^set_final_grade/$', SetFinalGradeView.as_view(), name="api-set-final-grade"),
)
