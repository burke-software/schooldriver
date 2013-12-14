from django.conf.urls import *
from ecwsp.naviance_sso import views

urlpatterns = patterns('',
    (r'^login/$', views.login),
)
