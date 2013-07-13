from django.conf.urls.defaults import *
#from django.views.generic import ListView
from ecwsp.omr.views import *
from ecwsp.omr.models import QuestionBank
from ecwsp.benchmarks.models import Benchmark

urlpatterns = patterns('',
    (r'^test/$', my_tests),
    (r'^test/show_queue/$', my_tests_show_queue),
    (r'^test/add/$', edit_test),
    (r'^test/(?P<id>\d+)/$', edit_test),
    (r'^test_questions/(?P<id>\d+)/$', edit_test_questions),
    (r'^test_questions/(?P<question_id>\d+)/save_question/$', save_question),
    (r'^test_questions/(?P<answer_id>\d+)/save_answer/$', save_answer),
    (r'^test_questions/(?P<test_id>\d+)/download_test/$', download_test),
    (r'^test_questions/(?P<test_id>\d+)/ajax_reorder_question/$', ajax_reorder_question),
    (r'^test_questions/(?P<test_id>\d+)/ajax_question_form/(?P<question_id>\d+)/$', ajax_question_form),
    (r'^test_questions/(?P<test_id>\d+)/ajax_delete_question/(?P<question_id>\d+)/$',ajax_delete_question),
    (r'^test_questions/(?P<test_id>\d+)/ajax_delete_answer/(?P<answer_id>\d+)/$',ajax_delete_answer),
    (r'^test_questions/(?P<test_id>\d+)/ajax_question_form/new/$', ajax_new_question_form),
    (r'^test_questions/(?P<test_id>\d+)/ajax_benchmarks_form/(?P<question_id>\d+)/$', ajax_benchmarks_form),
    (r'^test_questions/(?P<test_id>\d+)/add_answer/(?P<question_id>\d+)/new/$', add_answer),
    (r'^test_questions/(?P<test_id>\d+)/ajax_question_bank_to_question/(?P<question_bank_id>\d+)/$',ajax_question_bank_to_question),
    (r'^test_questions/(?P<test_id>\d+)/ajax_finalize_test/$', ajax_finalize_test),
    
    (r'^test_questions/(?P<test_id>\d+)/ajax_mark_as_answer/(?P<answer_id>\d+)/$', ajax_mark_as_answer),
    
    (r'^test/(?P<test_id>\d+)/copy/$', test_copy),
    (r'^test_result/(?P<test_id>\d+)/$', test_result),
    (r'^test_result/(?P<test_id>\d+)/download_xls/$', download_test_results),
    (r'^test_result/(?P<test_id>\d+)/download_student_results/$', download_student_results),
    (r'^test_result/(?P<test_id>\d+)/download_answer_sheets/$', download_answer_sheets),
    (r'^generatexml/(?P<test_id>\d+)', queXF_answer_sheets),
    (r'^question_bank/$', QuestionBankListView.as_view(
        model=QuestionBank,
    )),
    (r'^benchmark/$', BenchmarkListView.as_view(
        model=Benchmark,
    )),
    (r'^manual_edit/(?P<test_id>\d+)/$', manual_edit),
)
