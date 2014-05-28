from django.conf.urls import patterns, url
from responsive_dashboard.views import generate_dashboard
from .views import CourseView

urlpatterns = patterns('',
    (r'^$', generate_dashboard, {'app_name': 'schedule'}),
    url(r'^course/(.*)$', CourseView.as_view(), name="course")
)
