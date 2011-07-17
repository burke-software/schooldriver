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
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from ecwsp.omr.models import *
from ecwsp.omr.forms import *
from ecwsp.sis.models import Faculty
from ecwsp.sis.helper_functions import *
from ecwsp.schedule.models import Course

from elementtree.SimpleXMLWriter import XMLWriter

@permission_required('omr.change_test')
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

def my_tests_show_queue(request):
    id = request.POST['id']
    test = Test.objects.get(id=id)
    html = ""
    for result in test.testinstance_set.filter(results_recieved=False):
        html += '%s <br/>' % (result.student,)
    return HttpResponse(html)

@permission_required('omr.change_test')
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

@login_required
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
    
@login_required
def edit_test_questions(request, id):
    test = get_object_or_404(Test, id=id)
    questions = test.question_set.all()
    
    # for media
    question_form = TestQuestionForm(prefix="not_real")
    
    return render_to_response('omr/edit_test_questions.html', {
        'test': test,
        'questions': questions,
        'question_form': question_form,
    }, RequestContext(request, {}),)

@login_required
def ajax_new_question_form(request, test_id):
    test = Test.objects.get(id=test_id)
    
    if request.POST:
        question_answer_form = AnswerFormSet(request.POST, prefix="questionanswers_new")
        question_form = TestQuestionForm(request.POST, prefix="question_new")
        if question_answer_form.is_valid() and question_form.is_valid():
            q_instance = question_form.save()
            for qa_form in question_answer_form.forms:
                qa_instance = qa_form.save(commit=False)
                qa_instance.question = q_instance
                qa_instance.save()
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

@login_required
def ajax_read_only_question(request, test_id, question_id):
    question = Question.objects.get(id=question_id)
    return render_to_response('omr/edit_test_questions_read_only.html', {
        'question': question,
    }, RequestContext(request, {}),)

@login_required
def ajax_delete_question(request, test_id, question_id):
    question = Question.objects.get(id=question_id)
    question.delete()
    return HttpResponse('SUCCESS');

@login_required
def ajax_question_form(request, test_id, question_id):
    question = Question.objects.get(id=question_id)
    if request.POST:
        question_answer_form = AnswerFormSet(request.POST, instance=question, prefix="questionanswers_" + str(question_id))
        question_form = TestQuestionForm(request.POST, instance=question, prefix="question_" + str(question_id))
        if question_answer_form.is_valid() and question_form.is_valid():
            question_answer_form.save()
            question_form.save()
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
def generate_quexml(request):
    from elementtree.SimpleXMLWriter import XMLWriter
    global priorType
    priorType = None
    def generate_response():
        answers = []
        if priorType == "Multiple Choice":
            ct=0
            alphabet=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
            while ct < priorCt:
                answers.append((alphabet[ct],ct+1))
                ct=ct+1
        elif priorType == "True/False":
            answers = (("True",1), ("False",2))
        w.start("response")
        w.start("fixed")
        for label, value in answers:
            w.start("category")
            w.element("label", label)
            w.element("value", str(value))
            w.end("category")  
        w.end("fixed")
        w.end("response")
        w.end("question")
        global priorType
        priorType = question.type
        global answerCt
        answerCt=-1        
      
    
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s' % 'test.xml'
                
    test = TestInstance.objects.get(id=id)
    essays = None
    w = XMLWriter(response)
    questionnaire = w.start("questionnaire", {
        'xmlns:xsi':"http://www.w3.org/2001/XMLSchema-instance",
        'xsi:noNamespaceSchemaLocation':"quexml.xsd",
        'id':str(test.id),
    })
    w.start("questionnaireInfo")
    w.element("position","before")
    w.element("text",test.test.name) #name of test design
    w.element("administration","self")
    w.end("questionnaireInfo")
    w.start("section")
    w.start("sectionInfo")
    w.element("position","title")
    w.element("text",str(test.student)) #student assigned to test instance
    w.element("administration","self")
    w.end("sectionInfo")
    questions = test.test.question_set.order_by('group')
    groups = []
    for q in questions:
        if q.group not in groups:
            groups.append(q.group)
    
    for group in groups:
        w.start("question")
        w.element("text",str(group))
        groupedQuestions = questions.filter(group=group)
        i = 1 # Question number for human use only
        priorType = None
        essays = []
        answerCt = -1
        for question in groupedQuestions:
            if priorType:
                if priorType != question.type and priorType != "Essay":
                    priorCt = answerCt
                    generate_response()
                    w.start("question")
                elif priorType=="Multiple Choice":
                    priorCt=answerCt
                    answerCt = Answer.objects.filter(question=question).count()
                    if priorCt > -1 and answerCt != priorCt:
                        generate_response()
                        w.start("question")
            if question.type != "Essay":
                w.start("subQuestion", varName=str(question.id))
                w.element("text", str(i))
                w.end("subQuestion")
            else:
                essays.append((question,i))
            priorType = question.type
            i += 1
        priorCt = Answer.objects.filter(question=question).count()
        generate_response()
        
    w.end("section")
    w.start("section")
    w.start("sectionInfo")
    w.element("position", "title")
    w.element("text","For teacher use only!")
    w.element("administration","self")
    w.end("sectionInfo")
    w.start("question")
    value = -1
    for essay in essays:
        question, i = essay
        priorVal = value
        value = question.point_value
        print value
        if priorVal > -1 and value != priorValue:
            w.start("response")
            w.start("fixed")
            ct=0
            while ct<=value:
                w.start("category")
                w.element("label",str(ct))
                w.element("value",str(ct+1))
                w.end("category")
                ct += 1
            w.end("fixed")
            w.end("response")
            w.end("question")
            w.start("question")
        w.start("subQuestion")
        w.element("text",str(i))
        w.end("subQuestion")
    w.start("response")
    w.start("fixed")
    value = question.point_value
    ct=0
    while ct<=value:
        w.start("category")
        w.element("label",str(ct))
        w.element("value",str(ct+1))
        w.end("category")
        ct += 1
    w.end("fixed")
    w.end("response")    
    w.end("question")
    w.end("section")
    
    
    w.close(questionnaire)
    return response