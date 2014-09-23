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
    (r'^application', views.studentApplication),
)
