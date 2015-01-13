from django.conf.urls import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import views

urlpatterns = patterns('',
    (r'^student_report$', views.student_report),
    (r'^student_report/(?P<student_pk>\d+)$', views.student_report),
    (r'^student_report/(?P<student_pk>\d+)/(?P<marking_period_pk>\d+)$', views.student_report),
    (r'^student_course_section_report/(?P<student_pk>\d+)/(?P<course_section_pk>\d+)$', views.student_report),
    (r'^student_course_section_report/(?P<student_pk>\d+)/(?P<course_section_pk>\d+)/(?P<marking_period_pk>\d+)$', views.student_report),
    (r'^comments/(?P<course_section_id>\d+)/$', views.comments),
    (r'^gradebook/(?P<course_section_id>\d+)/$', views.gradebook),
    (r'^gradebook/ajax_save_grade/$', views.ajax_save_grade),
    (r'^gradebook/ajax_task_poll/$', views.ajax_task_poll),
    (r'^gradebook/ajax_task_poll/(?P<course_section_pk>\d+)$', views.ajax_task_poll),
    (r'^gradebook/(?P<course_section_id>\d+)/ajax_get_item_form/$', views.ajax_get_item_form),
    (r'^gradebook/(?P<course_section_id>\d+)/ajax_get_item_form/(?P<item_id>\d+)/$', views.ajax_get_item_form),
    (r'^gradebook/(?P<course_section_id>\d+)/ajax_get_item_form/(?P<item_id>\d+)/delete/$', views.ajax_delete_item_form),
    (r'^gradebook/(?P<course_section_id>\d+)/ajax_get_demonstration_form/$', views.ajax_get_demonstration_form),
    (r'^gradebook/(?P<course_section_id>\d+)/ajax_get_demonstration_form/(?P<demonstration_id>\d+)/$', views.ajax_get_demonstration_form),
    (r'^gradebook/(?P<course_section_id>\d+)/ajax_get_demonstration_form/(?P<demonstration_id>\d+)/delete/$', views.ajax_delete_demonstration_form),
    (r'^gradebook/(?P<course_section_id>\d+)/ajax_get_student_info/(?P<student_id>\d+)/$', views.ajax_get_student_info),
    (r'^gradebook/(?P<course_section_id>\d+)/ajax_get_fill_all_form/(?P<object_type>item|demonstration)/(?P<object_id>\d+)/$', views.ajax_get_fill_all_form),
    (r'^gradebook/(?P<course_section_id>\d+)/ajax_get_item_tooltip/(?P<item_id>\d+)/$', views.ajax_get_item_tooltip),
    ('student_incomplete_course_sections', 'ecwsp.benchmark_grade.report.student_incomplete_course_sections'),
    ('student_zero_dp_standards', 'ecwsp.benchmark_grade.report.student_zero_dp_standards'),
    (r'^gradebook/export/(?P<course_section_id>\d+)/$', 'ecwsp.benchmark_grade.report.gradebook_export'),
)

urlpatterns += staticfiles_urlpatterns()
