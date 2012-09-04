from django.conf.urls.defaults import *
from ecwsp.canvas_sync import views

urlpatterns = patterns('',
    (r'^setup/$', views.setup),
)