from django.conf.urls import *
from ecwsp.omr import views
from ecwsp.omr.models import QuestionBank
from ecwsp.benchmarks.models import Benchmark

urlpatterns = patterns('',
    (r'^test/$', views.my_tests),
    (r'^test/show_queue/$', views.my_tests_show_queue),
    (r'^test/add/$', views.edit_test),
    (r'^test/(?P<id>\d+)/$', views.edit_test),
    (r'^test_questions/(?P<id>\d+)/$', views.edit_test_questions),
    (r'^test_questions/(?P<question_id>\d+)/save_question/$', views.save_question),
    (r'^test_questions/(?P<answer_id>\d+)/save_answer/$', views.save_answer),
    (r'^test_questions/(?P<test_id>\d+)/download_test/$', views.download_test),
    (r'^test_questions/(?P<test_id>\d+)/ajax_question_form/(?P<question_id>\d+)/$', views.ajax_question_form),
    (r'^test_questions/(?P<test_id>\d+)/ajax_delete_question/(?P<question_id>\d+)/$', views.ajax_delete_question),
    (r'^test_questions/(?P<test_id>\d+)/ajax_delete_answer/(?P<answer_id>\d+)/$', views.ajax_delete_answer),
    (r'^test_questions/(?P<test_id>\d+)/ajax_question_form/new/$', views.ajax_new_question_form),
    (r'^test_questions/(?P<test_id>\d+)/ajax_benchmarks_form/(?P<question_id>\d+)/$', views.ajax_benchmarks_form),
    (r'^test_questions/(?P<test_id>\d+)/add_answer/(?P<question_id>\d+)/new/$', views.add_answer),
    (r'^test_questions/(?P<test_id>\d+)/ajax_question_bank_to_question/(?P<question_bank_id>\d+)/$', views.ajax_question_bank_to_question),
    (r'^test_questions/(?P<test_id>\d+)/ajax_finalize_test/$', views.ajax_finalize_test),
    
    (r'^test_questions/(?P<test_id>\d+)/ajax_mark_as_answer/(?P<answer_id>\d+)/$', views.ajax_mark_as_answer),
    
    (r'^test/(?P<test_id>\d+)/copy/$', views.test_copy),
    (r'^test_result/(?P<test_id>\d+)/$', views.test_result),
    (r'^test_result/(?P<test_id>\d+)/download_xls/$', views.download_test_results),
    (r'^test_result/(?P<test_id>\d+)/download_student_results/$', views.download_student_results),
    (r'^test_result/(?P<test_id>\d+)/download_teacher_results/$', views.download_teacher_results),
    (r'^test_result/(?P<test_id>\d+)/download_answer_sheets/$', views.download_answer_sheets),
    (r'^generatexml/(?P<test_id>\d+)', views.queXF_answer_sheets),
    (r'^question_bank/$', views.QuestionBankListView.as_view(
        model=QuestionBank,
    )),
    (r'^benchmark/$', views.BenchmarkListView.as_view(
        model=Benchmark,
    )),
    (r'^manual_edit/(?P<test_id>\d+)/$', views.manual_edit),
)
