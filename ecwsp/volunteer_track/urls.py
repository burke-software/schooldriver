from django.conf.urls import *
from ecwsp.volunteer_track.views import *

urlpatterns = patterns('',
    (r'^volunteer/$', student_dash),
    (r'^volunteer/site$', student_site_approval),
    (r'^volunteer/hours/(?P<id>\d+)/$', student_hours),
    (r'^volunteer/change_supervisor/(?P<id>\d+)/$', change_supervisor),
    (r'^approve$', approve),
)
