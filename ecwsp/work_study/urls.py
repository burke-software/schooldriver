from django.conf.urls import *
from ecwsp.work_study import views
from responsive_dashboard.views import generate_dashboard

urlpatterns = patterns('',
    (r'^$', generate_dashboard, {'app_name': 'work_study'}),
    (r'^reports/$', views.report_builder_view),
    (r'^student_timesheet/$', views.student_timesheet),
    (r'^supervisor/create_timesheet/(?P<studentId>\d+)/$', views.create_time_card),
    (r'^supervisor/change_supervisor/(?P<studentId>\d+)/$', views.change_supervisor),
    (r'^supervisor/$', views.supervisor_dash),
    (r'^supervisor/view/$', views.supervisor_view),
    (r'^supervisor/view/xls/$', views.supervisor_xls),
    (r'^student/view/$', views.student_view),
    (r'^student/edit/(?P<tsid>\d+)/$', views.student_edit),
    (r'^approve/$', views.approve),
    (r'^supervisor/delete/$', views.timesheet_delete),
    (r'^dol/$',views.dol_form),
    (r'^dol/(?P<id>\d+)$', views.dol_form),
    (r'^student_meeting/$', views.student_meeting),
    (r'^company_contract/(?P<id>\d+)/$', views.company_contract1),
    (r'^company_contract2/(?P<id>\d+)/$', views.company_contract2),
    (r'^company_contract3/(?P<id>\d+)/$', views.company_contract3),
    (r'^company_contract_complete/(?P<id>\d+)/$', views.company_contract_complete),
    (r'^company_contract_pdf/(?P<id>\d+)/$', views.company_contract_pdf),
    (r'^fte_chart/$', views.fte_chart),
    (r'^routes/$', views.routes),
    (r'^take_attendance/$', views.take_attendance),
    (r'^take_attendance/(?P<work_day>\d+)/$', views.take_attendance),
)


