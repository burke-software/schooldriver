from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^volunteer/$', student_dash),
    (r'^volunteer/site$', student_site_approval),
    (r'^volunteer/hours$', student_hours),
    (r'^volunteer/change_supervisor$', change_supervisor),
)
