from django.db.models import FileField
from django.db import models
from django.db.models import Sum
from django.db.models import signals
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.dispatch import dispatcher
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.localflavor.us.models import *

from ecwsp.sis.models import SchoolYear, Student    

from django.core.exceptions import ImproperlyConfigured
from positions.fields import PositionField

if not 'ecwsp.benchmarks' in settings.INSTALLED_APPS:
    raise ImproperlyConfigured('omr depends on benchmarks but it is not in installed apps')
    
    
def get_active_year():
    try:
        return SchoolYear.objects.get(active_year=True)
    except:
        return None
class Test(models.Model):
    name = models.CharField(max_length=255)
    teachers = models.ManyToManyField('sis.Faculty', blank=True, null=True)
    school_year = models.ForeignKey('sis.SchoolYear', default=get_active_year, blank=True, null=True)
    marking_period = models.ForeignKey('schedule.MarkingPeriod', blank=True, null=True)
    department = models.ForeignKey('benchmarks.Department', blank=True, null=True)
    courses = models.ManyToManyField('schedule.Course', blank=True, null=True, help_text="Enroll an entire course, students will not show until saving.")
    students = models.ManyToManyField('sis.Student', blank=True, null=True, through='TestInstance')
    finalized = models.BooleanField(help_text="This test is finished and should no longer be edited!")
    answer_sheet_pdf = FileField(upload_to="student_tests", blank=True)
    queXF_pdf = FileField(upload_to="student_tests", blank=True)
    banding = FileField(upload_to="student_tests", blank=True)
    
    class Meta:
        permissions = (
            ('teacher_test', 'Teacher can make and edit tests'),
        )
    
    def __unicode__(self):
        return self.name
    
    def __enroll_student(self, student):
        instance, created = TestInstance.objects.get_or_create(
                student=student,
                test=self,
            )
        instance.save()
        instance.teachers = self.teachers.all()
        instance.save()
    
    def link_copy(self):
        from ecwsp.omr.views import test_copy
        return '<a href="%s">Copy</a>' % (reverse(test_copy, args=[self.id]),)
    link_copy.allow_tags = True
    
    @property
    def students_test_results(self):
        return self.testinstance_set.filter(results_received=True).count()
    
    @property
    def students_in_queue(self):
        return self.testinstance_set.filter(results_received=False).count()
    
    @property
    def points_possible(self):
        data = self.question_set.aggregate(points_possible=Sum('point_value'))
        return data['points_possible']
        
    @property
    def points_average(self):
        try:
            total_points = self.question_set.aggregate(total_points=Sum('answerinstance__points_earned'))['total_points']
            return float(total_points) / (float(self.points_possible) * float(self.students_test_results))
        except:
            return "N/A"
    
    def enroll_students(self, students):
        """ Enroll these students, delete those not in this list!! """
        if students:
            for student in students:
                self.__enroll_student(student)
            kill_instances = TestInstance.objects.filter(test=self).exclude(student__in=students.all())
            for kill_instance in kill_instances:
                kill_instance.delete()
            self.enroll_course()
    
    def enroll_course(self):
        for course in self.courses.all():
            students = Student.objects.filter(course=course)
            for student in students:
                self.__enroll_student(student)
def enroll_course_signal(sender, instance, signal, *args, **kwargs):
    instance.enroll_course()
signals.m2m_changed.connect(enroll_course_signal, sender=Test.courses.through)
    

class QuestionAbstract(models.Model):
    question = RichTextField(blank=True)
    benchmarks = models.ManyToManyField('benchmarks.Benchmark', blank=True, null=True)
    theme = models.CharField(max_length=255, blank=True)
    type_choices = (
        ('Multiple Choice','Multiple Choice'), # Simple
        ('True/False','True/False'),        # Multiple Choice with only True or False options
        ('Essay','Essay'),                  # Teacher grades and fills in bubble
    )
    type = models.CharField(max_length=25, choices=type_choices, default='Multiple Choice')
    point_value = models.IntegerField(default=1)
    is_true = models.BooleanField(verbose_name="True or False")
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return strip_tags(self.question)


class QuestionBank(QuestionAbstract):
    network_question = models.ForeignKey('NetworkQuestionBank', editable=False, unique=True, blank=True, null=True)


class NetworkQuestionBank(QuestionAbstract):
    """ Stores questions for multiple SWORD instances """
    school = models.TextField(max_length=1000, blank=True, help_text="School that submitted this question")
    group = None
    themes = None
    
    def copy_local(self):
        """ Copy to the school wide question bank, if exists, update """
        if QuestionBank.objects.filter(network_question=self).count():
            local = QuestionBank.objects.get(network_question=self)
        else:
            local = QuestionBank(network_question=self)
        local.question = self.question
        local.group = self.group
        local.type = self.type
        local.point_value = self.point_value
        local.save()
        local.benchmarks = self.benchmarks.all()
        local.save()
        local.answerbank_set.clear()
        for answer in self.answer_set.all():
            local_answer = AnswerBank.get_or_create(
                question = local,
                answer = answer.answer,
                error_type = answer.error_type,
                point_value = answer.point_value,
            )[0]
            local.answerbank_set.add(local_answer)
    
    
class Question(QuestionAbstract):
    test = models.ForeignKey(Test)
    order = PositionField(collection='test', blank=True)
    
    class Meta:
        ordering = ['order']
    
    def copy_to_bank(self):
        """ Copy question and answer to bank unless a question with the exact same wording already exists."""
        if not QuestionBank.objects.filter(question=self.question).count():
            qb = QuestionBank(
                question = self.question,
                group = self.group,
                type = self.type,
                point_value = self.point_value,
            )
            qb.save()
            qb.benchmarks = self.benchmarks.all()
            qb.themes = self.themes.all()
            qb.save()
            for answer in self.answer_set.all():
                ab = AnswerBank(
                    question = qb,
                    answer = answer.answer,
                    error_type = answer.error_type,
                    point_value = answer.point_value,
                )
                ab.save()
                self.save()
                qb.answerbank_set.add(ab)
                self.save()
    
    def check_type(self):
        """ Check question type, force answers to make sense. True/False should have
        A True and False answer. """
        if self.type == "True/False":
            answers = self.answer_set.all()
            if answers.count() == 2:
                answer = Answer.objects.get(id=answers[0].id)
                answer.answer = "True"
                if self.is_true:
                    answer.point_value = self.point_value
                else:
                    answer.point_value = 0
                answer.save()
                answer = Answer.objects.get(id=answers[1].id)
                answer.answer = "False"
                if self.is_true:
                    answer.point_value = 0
                else:
                    answer.point_value = self.point_value
                answer.save()
            else:
                for answer in answers:
                    answer.delete()
                answer = Answer(
                    answer="True",
                    question=self
                )
                if self.is_true:
                    answer.point_value = self.point_value
                else:
                    answer.point_value = 0
                answer.save()
                self.save()
                answer = Answer(
                    answer="False",
                    question=self
                )
                if self.is_true:
                    answer.point_value = 0
                else:
                    answer.point_value = self.point_value
                answer.save()


class AnswerAbstract(models.Model):
    answer = RichTextField(blank=True)
    error_type = models.CharField(max_length=255, blank=True)
    point_value = models.IntegerField(default=0)
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return strip_tags(self.answer)
    
class AnswerBank(AnswerAbstract):
    question = models.ForeignKey(QuestionBank)
    
class Answer(AnswerAbstract):
    question = models.ForeignKey(Question)
    order = PositionField(collection="question")
    
    class Meta:
        ordering = ('order',)

    @property
    def letter(self):
        if self.question.type == "True/False":
            return self.answer[0]
        else:
            return chr(self.order + 65)
    
class TestInstance(models.Model):
    student = models.ForeignKey('sis.Student')
    school_year = models.ForeignKey('sis.SchoolYear', blank=True, null=True)
    marking_period = models.ForeignKey('schedule.MarkingPeriod', blank=True, null=True)
    test = models.ForeignKey(Test)
    date = models.DateTimeField(auto_now_add=True, validators=settings.DATE_VALIDATORS)
    teachers = models.ManyToManyField('sis.Faculty', blank=True, null=True)
    results_received = models.BooleanField()
    def __unicode__(self):
        return '%s %s' % (self.student, self.test)
    
    @property
    def points_possible(self):
        data = self.test.question_set.aggregate(points_possible=Sum('point_value'))
        return data['points_possible']
    @property
    def points_earned(self):
        data = self.answerinstance_set.aggregate(points_earned=Sum('points_earned'))
        if data['points_earned']: 
            return data['points_earned']
        else:
            return 0
    @property
    def grade(self):
        try:
            possible = self.points_possible
            earned = self.points_earned
            grade = float(earned) / float(possible)
            return '%.2f' % (grade * 100)
        except:
            return None
        
    
class AnswerInstance(models.Model):
    test_instance = models.ForeignKey(TestInstance)
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(Answer)
    points_earned = models.IntegerField()
    points_possible = models.IntegerField()
    def __unicode__(self):
        return '%s %s' % (self.test_instance, self.answer)
    class Meta:
        unique_together = (("test_instance", "question"),)
