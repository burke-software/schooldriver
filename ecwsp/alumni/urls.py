from django.conf.urls import *
from views import *

urlpatterns = patterns('',
    (r'^ajax_quick_add_note/(?P<student_id>\d+)/$', ajax_quick_add_note),
    (r'^import_clearinghouse/$', import_clearinghouse),
    
)
