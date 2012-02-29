from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^enroll/(?P<id>\d+)$', schedule_enroll),
    (r'^grade_analytics/$', grade_analytics),
)