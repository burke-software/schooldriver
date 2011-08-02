#   Copyright 2011 David M Burke
#   Author David M Burke <dburke@cristoreyny.org>
#   
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#     
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#      
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.utils import simplejson
from django.db import transaction
from django.forms.models import modelformset_factory
from django.forms.widgets import TextInput
from django.views.generic import ListView
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from ecwsp.omr.models import *
from ecwsp.omr.forms import *
from ecwsp.sis.models import Faculty
from ecwsp.sis.helper_functions import *
from ecwsp.schedule.models import Course

from elementtree.SimpleXMLWriter import XMLWriter
import django_filters

class QuestionBankFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super(QuestionBankFilter, self).__init__(*args, **kwargs)
        for name, field in self.filters.iteritems():
            if isinstance(field, django_filters.ChoiceFilter):
                # Add "Any" entry to choice fields.
                field.extra['choices'] = tuple([("", "Any"), ] + list(field.extra['choices']))
    
    class Meta:
        model = QuestionBank
        fields = ['question', 'type', 'benchmarks', 'themes',]
    question = django_filters.CharFilter(name='question', lookup_type='icontains', widget=TextInput(attrs={'class':'search',}))

class QuestionBankListView(ListView):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(QuestionBankListView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        f = QuestionBankFilter(self.request.GET, queryset=QuestionBank.objects.all())
        context['is_popup'] = True
        context['filter'] = f
        context['tip'] = ['Hover over truncated information to view all.', 'Images and formatting are not shown here. They will appear when you select a question.']
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
    new_test.teachers = old_test.teachers.all()
    new_test.save()
    for old_question in old_test.question_set.all():
        new_question = copy_model_instance(old_question)
        new_question.save()
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
    teacher_courses = Course.objects.filter(teacher=teacher)
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
            return render_to_response('omr/edit_test_questions_read_only.html', {
                'question': q_instance,
            }, RequestContext(request, {}),)
    else:
        question_answer_form = NewAnswerFormSet(prefix="questionanswers_new")
        question_form = TestQuestionForm(prefix="question_new", initial={'test': test})
    
    return render_to_response('omr/ajax_question_form.html', {
        'new': 'new',
        'question_form.prefix': 'new',
        'question_form': question_form,
        'answers_formset': question_answer_form,
    }, RequestContext(request, {}),)

@permission_required('omr.teacher_test')
def ajax_question_form(request, test_id, question_id):
    question = Question.objects.get(id=question_id)
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
    return render_to_response('omr/ajax_question_form.html', {
        'question': question,
        'question_form': question_form,
        'answers_formset': question_answer_form,
    }, RequestContext(request, {}),)

@login_required
def generate_xml(request):
    from xml.dom import minidom
    
    test = TestInstance.objects.get(id=id)
    teacher_section_required = False
    
    doc = minidom.Document()
    testtag = doc.createElement("test")
    doc.appendChild(testtag)
    id = doc.createElement("id")
    testtag.appendChild(id)
    idtext = doc.createTextNode(str(test.id))
    id.appendChild(idtext)
    titletag = doc.createElement("title")
    testtag.appendChild(titletag)
    titletext = doc.createTextNode(test.test.name)
    titletag.appendChild(titletext)
    studentsection = doc.createElement("section")
    testtag.appendChild(studentsection)
    studentnametag = doc.createElement("name")
    studentsection.appendChild(studentnametag)
    studentname = doc.createTextNode(str(test.student.fname + " " + test.student.lname))
    studentnametag.appendChild(studentname)

    questions = test.test.question_set.order_by('group')
    groups = []
    essays = []
    for q in questions:
        if q.group not in groups:
            groups.append(q.group)
    
    for group in groups:
        grouptag = doc.createElement("group")
        studentsection.appendChild(grouptag)
        groupname = doc.createElement("text")
        grouptag.appendChild(groupname)
        groupnametext = doc.createTextNode(str(group.name))
        groupname.appendChild(groupnametext)
        
        groupedQuestions = questions.filter(group=group)
        i = 1 # Question number for human use only
        priorType = None
        
        for q in groupedQuestions:
            questiontag = doc.createElement("question")
            questiontag.setAttribute("varName",str(q.id))
            grouptag.appendChild(questiontag)
            question_number = doc.createElement("text")
            questiontag.appendChild(question_number)
            if q.type == "Essay":
                essays.append([q,i])
                teacher_section_required = True
                text = str(i) + ".  Essay Question"
            else:
                text = str(i) + ". "
                answers = []
                if q.type == "Multiple Choice":
                    ct=0
                    alphabet=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
                    while ct < q.answer_set.count():
                        answers.append(alphabet[ct])
                        ct=ct+1
                elif q.type == "True/False":
                    answers = ("True","False")
                for choice in answers:
                    choicetag = doc.createElement("choice")
                    questiontag.appendChild(choicetag)
                    choicetagtext = doc.createTextNode(str(choice))
                    choicetag.appendChild(choicetagtext) 
                
            question_numbertext = doc.createTextNode(text)
            question_number.appendChild(question_numbertext)
            i=i+1
    
    if teacher_section_required:
        teachersection = doc.createElement("section")
        testtag.appendChild(teachersection)
        teachertexttag = doc.createElement("name")
        teachersection.appendChild(teachertexttag)
        teachertext = doc.createTextNode("For Teacher Use Only")
        teachertexttag.appendChild(teachertext)
        priorGroup = None
        for q,number in essays:
            if priorGroup!= q.group or priorGroup == None:
                teacher_grouptag = doc.createElement("group")
                teachersection.appendChild(teacher_grouptag)
                teacher_groupname = doc.createElement("text")
                teacher_grouptag.appendChild(teacher_groupname)
                teacher_groupnametext = doc.createTextNode(str(group.name))
                teacher_groupname.appendChild(teacher_groupnametext)
                priorGroup = q.group
                
            teacher_question = doc.createElement("question")
            teacher_question.setAttribute("varName",str(q.id))
            teacher_grouptag.appendChild(teacher_question)
            teacher_question_number = doc.createElement("text")
            teacher_question.appendChild(teacher_question_number)
            teacher_question_numbertext = doc.createTextNode(str(number) + ". ")
            teacher_question_number.appendChild(teacher_question_numbertext)
            options = Answer.objects.filter(question=q)
            for choice in options:
                choicetag = doc.createElement("choice")
                teacher_question.appendChild(choicetag)
                choicetagtext = doc.createTextNode(str(choice.point_value))
                choicetag.appendChild(choicetagtext)
                
    #need to create a zip file of banding files and pdf files - currently sets up pdf to download and creates xml.            
    response = HttpResponse(mimetype="application/pdf")
    #xmlresponse = HttpResponse(mimetype="text/xml")    
    pdf = createpdf(doc.toxml(),response)
    response['Content-Disposition'] = "attachment; filename=" + pdf
    return response