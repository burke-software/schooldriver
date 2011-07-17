from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
     (r'^student/volunteer/$', student_site_approval),
)