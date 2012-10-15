#   Copyright 2011 David M Burke
#   Author David M Burke <dburke@cristoreyny.org>
#   Co-Author Callista Goss <calli@burkesoftware.com>
#   
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.utils import simplejson
from django.db import transaction
from django.db.models import Q
from django.forms.models import modelformset_factory
from django.forms.widgets import TextInput
from django.views.generic import ListView
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from ecwsp.administration.models import Template
from ecwsp.omr.createpdf import createpdf,generate_xml
from ecwsp.omr.models import *
from ecwsp.omr.forms import *
from ecwsp.omr.reports import *
from ecwsp.sis.models import Faculty, UserPreference
from ecwsp.sis.helper_functions import *
from ecwsp.schedule.models import Course
from ecwsp.benchmarks.models import Benchmark

from elementtree.SimpleXMLWriter import XMLWriter
import django_filters
import MySQLdb
import logging

class QuestionBankFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super(QuestionBankFilter, self).__init__(*args, **kwargs)
        for name, field in self.filters.iteritems():
            if isinstance(field, django_filters.ChoiceFilter):
                # Add "Any" entry to choice fields.
                field.extra['choices'] = tuple([("", "Any"), ] + list(field.extra['choices']))
    
    class Meta:
        model = QuestionBank
        fields = ['question', 'type', 'benchmarks', 'themes']
    question = django_filters.CharFilter(name='question', lookup_type='icontains', widget=TextInput(attrs={'class':'search',}))

class QuestionBankListView(ListView):
    def get_context_data(self, **kwargs):
        context = super(QuestionBankListView, self).get_context_data(**kwargs)
        
        questions = QuestionBank.objects.all()
        if self.request.session['omr_test_id']:
            test = Test.objects.get(id=self.request.session['omr_test_id'])
            context['test'] = test
            if test.department:
                questions = questions.filter(benchmarks__measurement_topics__department=test.department)
        f = QuestionBankFilter(self.request.GET, queryset=questions)
        
        context['is_popup'] = True
        context['filter'] = f
        context['tip'] = ['Hover over truncated information to view all.', 'Images and formatting are not shown here. They will appear when you select a question.']
        return context
    
    
class BenchmarkFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super(BenchmarkFilter, self).__init__(*args, **kwargs)
        for name, field in self.filters.iteritems():
            if isinstance(field, django_filters.ChoiceFilter):
                # Add "Any" entry to choice fields.
                field.extra['choices'] = tuple([("", "Any"), ] + list(field.extra['choices']))
    
    class Meta:
        model = Benchmark
        fields = ['measurement_topics']
    
    number = django_filters.CharFilter(name='number', lookup_type='icontains', widget=TextInput(attrs={'class':'search',}))
    benchmark = django_filters.CharFilter(name='name', lookup_type='icontains', widget=TextInput(attrs={'class':'search',}))

class BenchmarkListView(ListView):
    def get_context_data(self, **kwargs):
        context = super(BenchmarkListView, self).get_context_data(**kwargs)
        
        benchmarks = Benchmark.objects.all()
        if self.request.session['omr_test_id']:
            test = Test.objects.get(id=self.request.session['omr_test_id'])
            context['test'] = test
            if test.department:
                benchmarks = benchmarks.filter(measurement_topics__department=test.department)
        f = BenchmarkFilter(self.request.GET, queryset=benchmarks)
        
        context['is_popup'] = True
        context['filter'] = f
        context['tip'] = ['Hover over truncated information to view all.']
        return context

@permission_required('omr.teacher_test')
def my_tests(request):
    try:
        teacher = Faculty.objects.get(username=request.user.username)
    except:
        messages.warning(request, "You are not a teacher, redirecting to admin interface.")
        return HttpResponseRedirect(reverse('admin:app_list', args=['omr']))
    tests = Test.objects.filter(teachers=teacher)
    return render_to_response('omr/my_tests.html', {
        'tests': tests
    }, RequestContext(request, {}),)

@permission_required('omr.teacher_test')
def my_tests_show_queue(request):
    id = request.POST['id']
    test = Test.objects.get(id=id)
    html = ""
    for result in test.testinstance_set.filter(results_recieved=False):
        html += '%s <br/>' % (result.student,)
    return HttpResponse(html)

@user_passes_test(lambda u: u.has_perm("omr.teacher_test") or u.has_perm("omr.change_test"))
def test_copy(request, test_id):
    """ Copy test with a copy of all questions and answers. """
    old_test = Test.objects.get(id=test_id)
    new_test = copy_model_instance(old_test)
    new_test.name = old_test.name + " (copy)"
    new_test.save()
    try:
        new_test.teachers.add(Faculty.objects.get(username=request.user.username))
    except:
        new_test.teachers = old_test.teachers
    new_test.finalized = False
    new_test.save()
    for old_question in old_test.question_set.all():
        new_question = copy_model_instance(old_question)
        new_question.save()
        for benchmark in old_question.benchmarks.all():
            new_question.benchmarks.add(benchmark)
        new_test.question_set.add(new_question)
        for old_answer in old_question.answer_set.all():
            new_answer = copy_model_instance(old_answer)
            new_answer.save()
            new_question.answer_set.add(new_answer)
    messages.success(request, "Test copied!")
    # Redirect to either admin or teacher edit page
    if Faculty.objects.filter(username=request.user.username).count():
        return HttpResponseRedirect(reverse(edit_test, args=[new_test.id]))
    else:
        return HttpResponseRedirect(reverse('admin:test_change_form', args=[new_test.id]))

@user_passes_test(lambda u: u.has_perm("omr.teacher_test") or u.has_perm("omr.view_test") or u.has_perm("omr.change_test"))
def download_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    test.reindex_question_order()
    return render_to_response('omr/test.html', {
        'test': test,
    }, RequestContext(request, {}),)

@permission_required('omr.teacher_test')
def edit_test(request, id=None):
    teacher = Faculty.objects.get(username=request.user.username)
    teacher_courses = Course.objects.filter(Q(teacher=teacher) | Q(secondary_teachers=teacher))
    if id:
        add = False
        test = Test.objects.get(id=id)
        test_form = TestForm(instance=test)
        test_form.fields['students'].initial = test.students.all()
    else:
        add = True
        test_form = TestForm()
        test_form.fields['teachers'].initial = [teacher.id]
    
    if request.method == 'POST':
        if '_delete' in request.POST and id:
            test.delete()
            return HttpResponseRedirect(reverse(my_tests))
        if add:
            test_form = TestForm(request.POST)
        else:
            test_form = TestForm(request.POST, instance=test)
        if test_form.is_valid():
            instance = test_form.save()
            messages.success(request, 'Test %s saved!' % (instance,))
            if '_continue' in request.POST:
                return HttpResponseRedirect(reverse(my_tests) + str(instance.id))
            elif '_save' in request.POST:
                return HttpResponseRedirect(reverse(my_tests))
            elif '_next' in request.POST:
                return HttpResponseRedirect(reverse(edit_test_questions, args=[instance.id]))
                
    test_form.fields['courses'].queryset = teacher_courses
    return render_to_response('omr/edit_test.html', {
        'test_form': test_form,
        'add': add,
    }, RequestContext(request, {}),)
    
@permission_required('omr.teacher_test')
def edit_test_questions(request, id):
    test = get_object_or_404(Test, id=id)
    test.reindex_question_order()
    questions = test.question_set.all()
    
    # Ugly way to see which test is on, currently only used for filtering benchmarks
    request.session['omr_test_id'] = str(id)
    
    # for media
    question_form = TestQuestionForm(prefix="not_real")
    
    return render_to_response('omr/edit_test_questions.html', {
        'test': test,
        'questions': questions,
        'question_form': question_form,
    }, RequestContext(request, {}),)

@permission_required('omr.teacher_test')
@transaction.commit_on_success
def ajax_reorder_question(request, test_id):
    question_up_id = request.POST['question_up_id'][9:]
    question_down_id = request.POST['question_down_id'][9:]
    question_up = Question.objects.get(id=question_up_id)
    question_down =  Question.objects.get(id=question_down_id)
    
    if question_up.order and question_up.order > 1:
        question_up.order -= 1
        question_up.save()
    if question_down.order:
        question_down.order += 1
        question_down.save()
    
    data = {
        question_up_id: question_up.order,
        question_down_id: question_down.order,
    }
    data = simplejson.dumps(data)
    return HttpResponse(data,'application/javascript')

@permission_required('omr.teacher_test')
def ajax_question_bank_to_question(request, test_id, question_bank_id):
    test = get_object_or_404(Test, id=test_id)
    bank = get_object_or_404(QuestionBank, id=question_bank_id)
    new_question = Question(
        question=bank.question,
        group=bank.group,
        type=bank.type,
        point_value=bank.point_value,
        test=test,
    )
    new_question.save()
    new_question.benchmarks = bank.benchmarks.all()
    new_question.themes = bank.themes.all()
    new_question.save()
    for bank_answer in bank.answerbank_set.all():
        new_answer = Answer(
            question=new_question,
            answer=bank_answer.answer,
            error_type=bank_answer.error_type,
            point_value=bank_answer.point_value,
        )
        new_answer.save()
        new_question.answer_set.add(new_answer)
    return ajax_read_only_question(request, test_id, new_question.id)

@permission_required('omr.teacher_test')
def ajax_read_only_question(request, test_id, question_id):
    question = Question.objects.get(id=question_id)
    return render_to_response('omr/edit_test_questions_read_only.html', {
        'question': question,
    }, RequestContext(request, {}),)

@permission_required('omr.teacher_test')
def ajax_delete_question(request, test_id, question_id):
    question = Question.objects.get(id=question_id)
    question.delete()
    return HttpResponse('SUCCESS');

@permission_required('omr.teacher_test')
def ajax_new_question_form(request, test_id):
    test = Test.objects.get(id=test_id)
    
    if request.POST:
        question_answer_form = AnswerFormSet(request.POST, prefix="questionanswers_new")
        question_form = TestQuestionForm(request.POST, prefix="question_new")
        if question_form.is_valid():
            q_instance = question_form.save()
            for qa_form in question_answer_form.forms:
                if qa_form.is_valid():
                    qa_instance = qa_form.save(commit=False)
                    if str(qa_instance.answer).replace("<br />\n", ''): # Firefox hack
                        qa_instance.question = q_instance
                        qa_instance.save()
            q_instance.check_type()
            if question_form.cleaned_data['save_to_bank']:
                q_instance.copy_to_bank()
            return render_to_response('omr/edit_test_questions_read_only.html', {
                'question': q_instance,
            }, RequestContext(request, {}),)
    else:
        try:
            extra_answers = UserPreference.objects.get(user=request.user).omr_default_number_answers
        except:
            extra_answers = 2
        if not extra_answers:
            extra_answers = 2
        NewAnswerFormSet = inlineformset_factory(Question, Answer, extra=extra_answers, form=AnswerForm)
        question_answer_form = NewAnswerFormSet(prefix="questionanswers_new")
        try:
            points = UserPreference.objects.get(user=request.user).omr_default_point_value
        except:
            points = 1
        if not points:
            points = 1
        save_to_bank = UserPreference.objects.get(user=request.user).omr_default_save_question_to_bank
        question_form = TestQuestionForm(prefix="question_new", initial={'test': test, 'point_value': points, 'save_to_bank': save_to_bank})
    
    return render_to_response('omr/ajax_question_form.html', {
        'new': 'new',
        'question_form.prefix': 'new',
        'question_form': question_form,
        'answers_formset': question_answer_form,
    }, RequestContext(request, {}),)

@permission_required('omr.teacher_test')
def ajax_question_form(request, test_id, question_id):
    question = Question.objects.get(id=question_id)
    test = Test.objects.get(id=test_id)
    
    if request.POST:
        question_answer_form = AnswerFormSet(request.POST, instance=question, prefix="questionanswers_" + str(question_id))
        question_form = TestQuestionForm(request.POST, instance=question, prefix="question_" + str(question_id))
        
        if question_form.is_valid() and question_answer_form.is_valid():
            question_form.save()
            question_answer_form.save()
            question.check_type()
            return render_to_response('omr/edit_test_questions_read_only.html', {
                'question': question,
            }, RequestContext(request, {}),)
    else:
        question_answer_form = AnswerFormSet(instance=question, prefix="questionanswers_" + str(question_id))
        question_form = TestQuestionForm(instance=question, prefix="question_" + str(question_id))
    if test.finalized:
        question_form.fields['type'].widget.attrs['readonly'] = True
        question_form.fields['order'].widget.attrs['readonly'] = True
        question_form.fields['point_value'].widget.attrs['readonly'] = True
        for a_form in question_answer_form:
            a_form.fields['point_value'].widget.attrs['readonly'] = True
    return render_to_response('omr/ajax_question_form.html', {
        'question': question,
        'question_form': question_form,
        'answers_formset': question_answer_form,
        'new': False,
        'finalized': test.finalized,
    }, RequestContext(request, {}),)

@permission_required('omr.teacher_test')
def ajax_finalize_test(request, test_id):
    try:
        # Send to QueXF
        generate_xml(test_id)
        return HttpResponse('SUCCESS');
    except:
        try: # try again? One time it failed and then worked on second try..no clue why
            generate_xml(test_id)
            return HttpResponse('SUCCESS');
        except:
            logging.error('Couldn\'t finalize omr test.', exc_info=True, extra={
                'request': request,
            })
            return HttpResponse('Unexpected Error');

@permission_required('omr.teacher_test')
def test_result(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    
    return render_to_response('omr/test_result.html', {
        'test': test,
    }, RequestContext(request, {}),)

@user_passes_test(lambda u: u.has_perm("omr.teacher_test") or u.has_perm("omr.view_test") or u.has_perm("omr.change_test"))
def download_test_results(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    return report.download_results(test)
    
@user_passes_test(lambda u: u.has_perm("omr.teacher_test") or u.has_perm("omr.view_test") or u.has_perm("omr.change_test"))
def download_student_results(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    format = UserPreference.objects.get_or_create(user=request.user)[0].get_format(type="document")
    template = Template.objects.get_or_create(name="OMR Student Test Result")[0].get_template(request)
    if not template:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    return report.download_student_results(test, format, template)
    
    
@user_passes_test(lambda u: u.has_perm("omr.teacher_test") or u.has_perm("omr.view_test") or u.has_perm("omr.change_test"))
def download_answer_sheets(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    
    response = HttpResponse(test.answer_sheet_pdf, mimetype="application/pdf")
    filename = "Answer_Sheets.pdf"
    response['Content-Disposition'] = "filename=" + str(filename)
    return response

@login_required
def queXF_answer_sheets(request,test_id):
    pdf = generate_xml(test_id)
    response = HttpResponse(pdf, mimetype="application/pdf")
    filename = "Test_" + test_id + ".pdf"
    response['Content-Disposition'] = "filename=" + str(filename)
    return response


@permission_required('omr.teacher_test')
def manual_edit(request, test_id):
    #open the blob.
    test = get_object_or_404(TestInstance, id=test_id)
    letter = {}
    ascii_letter = None
    tf_response  = None
    student_answer = None
    for question in test.test.question_set.all(): #each question
        for answer in question.answerinstance_set.all(): #student's answer to question
            student_answer = answer.answer
        count = 0
        ascii_letter = 45
        tf_response = "none"
        if question.type == "True/False":
            ascii_letter = False
            tf_response = student_answer.answer
        else:
            for possible in question.answer_set.all():
                if student_answer == possible:
                    ascii_letter = 65+count #'A', 'B', 'C', etc. in ASCII
                else:
                    count += 1
        if ascii_letter:
            letter[question]=chr(ascii_letter)
        else:
            letter[question] = tf_response
        #http://stackoverflow.com/questions/1294385/how-to-insert-retrieve-a-file-stored-as-a-blob-in-a-mysql-db-using-python
        #render a blob image. probably going to have to play with this for a while.
    return render_to_response('omr/manually_edit.html', {
        'test': test, 'letter':letter, 'q':question
    }, RequestContext(request, {}),)
    
@permission_required('omr.teacher_test')
def student_unknown(request, test_id):
    #open files from quexf
    test = get_object_or_404(TestInstance, id = test_id)
    
    return render_to_response('omr/student_unknown', {
        
    }, RequestContext(request, {}),)
