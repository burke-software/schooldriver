from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^reports/$', report_builder_view),
    (r'^import/$', import_student),
    (r'^import/survey/$', import_survey),
    
    (r'^student_timesheet/$', student_timesheet),
    (r'^supervisor/create_timesheet/(?P<studentId>\d+)/$', create_time_card),
    (r'^supervisor/change_supervisor/(?P<studentId>\d+)/$', change_supervisor),
    (r'^supervisor/$', supervisor_dash),
    (r'^supervisor/view/$', supervisor_view),
    (r'^supervisor/view/xls/$', supervisor_xls),
    (r'^student/view/$', student_view),
    (r'^student/edit/(?P<tsid>\d+)/$', student_edit),
    (r'^approve/$', approve),
    (r'^supervisor/delete/$', timesheet_delete),
    (r'^dol/$', dol_form),
    (r'^dol/(?P<id>\d+)$', dol_form),
    (r'^student_meeting/$', student_meeting),
    (r'^company_contract/(?P<id>\d+)/$', company_contract1),
    (r'^company_contract2/(?P<id>\d+)/$', company_contract2),
    (r'^company_contract3/(?P<id>\d+)/$', company_contract3),
    (r'^company_contract_complete/(?P<id>\d+)/$', company_contract_complete),
    (r'^company_contract_pdf/(?P<id>\d+)/$', company_contract_pdf),
    (r'^studentworker/bulk_change/$', studentworker_bulk_change),
)


