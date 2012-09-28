from django.conf.urls.defaults import *
from ecwsp.integrations.canvas_sync import views

urlpatterns = patterns('',
    (r'^setup/$', views.setup),
)