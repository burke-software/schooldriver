from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^applicants_to_students/(?P<year_id>\d+)/$', applicants_to_students),
    (r'^reports/$', reports),
)