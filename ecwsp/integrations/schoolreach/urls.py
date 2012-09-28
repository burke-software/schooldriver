from django.conf.urls.defaults import *
from ecwsp.integrations.schoolreach import views

urlpatterns = patterns('',
    (r'^setup/$', views.setup),
)