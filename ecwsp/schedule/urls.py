from django.conf.urls import *
from responsive_dashboard import views, dashboard

urlpatterns = patterns('',
    (r'^$', views.generate_dashboard, {'app_name': 'schedule'}),
)
