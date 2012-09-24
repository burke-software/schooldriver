from django.conf.urls.defaults import *
import views

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    (r'^upload/(?P<id>\d+)$', views.benchmark_grade_upload),
    (r'^student_grade$', views.student_grade),
    (r'^student_grade_course_detail/(?P<course_id>\d+)/(?P<marking_period_id>\d+)$', views.student_grade_course_detail),
    (r'^family_grade$', views.family_grade),
    (r'^family_grade_course_detail/(?P<course_id>\d+)/(?P<marking_period_id>\d+)$', views.family_grade_course_detail),
    (r'^gradebook/(?P<course_id>\d+)/$', views.gradebook),
    (r'^gradebook/ajax_save_grade/$', views.ajax_save_grade),
    (r'^gradebook/(?P<course_id>\d+)/ajax_get_item_form/$', views.ajax_get_item_form),
    (r'^gradebook/(?P<course_id>\d+)/ajax_get_item_form/(?P<item_id>\d+)/$', views.ajax_get_item_form),
    (r'^gradebook/(?P<course_id>\d+)/ajax_get_item_form/(?P<item_id>\d+)/delete/$', views.ajax_delete_item_form),
    (r'^gradebook/(?P<course_id>\d+)/ajax_get_demonstration_form/$', views.ajax_get_demonstration_form),
    (r'^gradebook/(?P<course_id>\d+)/ajax_get_demonstration_form/(?P<demonstration_id>\d+)/$', views.ajax_get_demonstration_form),
    (r'^gradebook/(?P<course_id>\d+)/ajax_get_demonstration_form/(?P<demonstration_id>\d+)/delete/$', views.ajax_delete_demonstration_form),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)

urlpatterns += staticfiles_urlpatterns()
