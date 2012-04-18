from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^show_filters/(?P<app>[a-z]+)/(?P<module>[a-z]+)$', show_filters),
)
