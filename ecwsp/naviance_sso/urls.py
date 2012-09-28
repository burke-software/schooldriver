from django.conf.urls.defaults import *
from ecwsp.naviance_sso import views

urlpatterns = patterns('',
    (r'^login/$', views.login),
)