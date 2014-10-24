from django.conf.urls import *
from ecwsp.admissions import views
from responsive_dashboard.views import generate_dashboard

urlpatterns = patterns('',
    (r'^$', generate_dashboard, {'app_name': 'admissions'}),
    (r'^applicants_to_students/(?P<year_id>\d+)/$', views.applicants_to_students),
    (r'^ajax_check_duplicate_applicant/(?P<fname>[A-z]+)/(?P<lname>[A-z]+)/$', views.ajax_check_duplicate_applicant),
    (r'^reports/$', views.reports),
    (r'^reports/funnel/$', views.funnel),
    (r'^inquiry_form/$', views.inquiry_form),
    url(r'^application', views.student_application, name="student-application"),
    url(r'^custom-field-editor', views.application_custom_field_editor, name="application-custom-fields"),
    url(r'^custom-application-editor', views.custom_application_editor, name="custom-application-editor"),
)
