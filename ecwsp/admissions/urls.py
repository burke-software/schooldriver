from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^applicants_to_students/(?P<year_id>\d+)/$', applicants_to_students),
    (r'^ajax_check_duplicate_applicant/(?P<fname>[A-z]+)/(?P<lname>[A-z]+)/$', ajax_check_duplicate_applicant),
    (r'^reports/$', reports),
)