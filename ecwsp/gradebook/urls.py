from django.conf.urls import patterns, url
from ecwsp.sis.views import SpaView


urlpatterns = patterns('',
    url(r'^', SpaView.as_view()),
)
