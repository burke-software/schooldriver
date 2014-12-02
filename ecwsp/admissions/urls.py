from django.conf.urls import *
from ecwsp.admissions import views
from ecwsp.sis.views import SpaView
from responsive_dashboard.views import generate_dashboard
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    (r'^$', generate_dashboard, {'app_name': 'admissions'}),
    (r'^applicants_to_students/(?P<year_id>\d+)/$', views.applicants_to_students),
    (r'^ajax_check_duplicate_applicant/(?P<fname>[A-z]+)/(?P<lname>[A-z]+)/$', views.ajax_check_duplicate_applicant),
    (r'^reports/$', views.reports),
    (r'^reports/funnel/$', views.funnel),
    (r'^inquiry_form/$', views.inquiry_form),
    url(r'^custom-application-editor/', 
        TemplateView.as_view(template_name='admissions/custom_application_editor.html'), 
        name="custom-application-editor"
        ),
    (r'^application/(?P<pk>\d+)/$', SpaView.as_view()),
    (r'^application/$', SpaView.as_view()),
)
