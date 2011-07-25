from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^test/$', my_tests),
    (r'^test/show_queue/$', my_tests_show_queue),
    (r'^test/add/$', edit_test),
    (r'^test/(?P<id>\d+)/$', edit_test),
    (r'^test_questions/(?P<id>\d+)/$', edit_test_questions),
    (r'^test_questions/(?P<test_id>\d+)/ajax_reorder_question/$', ajax_reorder_question),
    (r'^test_questions/(?P<test_id>\d+)/ajax_question_form/(?P<question_id>\d+)/$', ajax_question_form),
    (r'^test_questions/(?P<test_id>\d+)/ajax_delete_question/(?P<question_id>\d+)/$',ajax_delete_question),
    (r'^test_questions/(?P<test_id>\d+)/ajax_read_only_question/(?P<question_id>\d+)/$',ajax_read_only_question),
    (r'^test_questions/(?P<test_id>\d+)/ajax_question_form/new/$', ajax_new_question_form),
    (r'^test/(?P<test_id>\d+)/copy/$', test_copy),
    (r'^generatexml', generate_quexml),
)