from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    (r'^upload/(?P<id>\d+)$', views.benchmark_grade_upload),
    (r'^student_grade$', views.student_grade),
    (r'^family_grade$', views.family_grade),
    (r'^gradebook$', views.gradebook),
    (r'^gradebook/ajax_save_grade/$', views.ajax_save_grade),    
)
