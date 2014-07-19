from django.conf.urls import *
from views import ajax_quick_add_note, import_clearinghouse
from responsive_dashboard.views import generate_dashboard

urlpatterns = patterns('',
    (r'^$', generate_dashboard, {'app_name': 'alumni'}),
    (r'^ajax_quick_add_note/(?P<student_id>\d+)/$', ajax_quick_add_note),
    (r'^import_clearinghouse/$', import_clearinghouse),
    
)
