from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^get_filters/(?P<app>[a-z_]+)/(?P<module>[a-z_]+)$', get_filters),
    (r'^get_filter_field$', get_filter_field),
)
