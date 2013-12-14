from django.conf.urls import *
from ecwsp.integrations.canvas_sync import views

urlpatterns = patterns('',
    (r'^setup/$', views.setup),
)
