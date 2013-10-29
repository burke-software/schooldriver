from django.conf.urls import *
from ecwsp.integrations.schoolreach import views

urlpatterns = patterns('',
    (r'^setup/$', views.setup),
)
