from django.db import models
from django.db.models import Sum
from django.db.models import signals
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.dispatch import dispatcher
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from ckeditor.fields import RichTextField

from ecwsp.sis.models import SchoolYear, Student

class MeasurementTopic(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __unicode__(self):
        return self.name
    
    
class Benchmark(models.Model):
    name = models.CharField(max_length=255, unique=True)
    measurement_topics = models.ManyToManyField(MeasurementTopic)
    number = models.CharField(max_length=10, blank=True, null=True)
    def __unicode__(self):
        return '%s %s' % (self.number, self.name)
        
        
class Theme(models.Model):
    """ Used by teachers, not an official benchmark """
    name = models.CharField(max_length=255, unique=True)
    def __unicode__(self):
        return self.name
    
    
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
    courses = models.ManyToManyField('schedule.Course', blank=True, null=True, help_text="Enroll an entire course, students will not show until saving.")
    students = models.ManyToManyField('sis.Student', blank=True, null=True, through='TestInstance')
    
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
        return self.testinstance_set.filter(results_recieved=True).count()
    
    @property
    def students_in_queue(self):
        return self.testinstance_set.filter(results_recieved=False).count()
        
    def reindex_question_order(self):
        """Test questions should always be 1, 2, 3, etc
        This will set it straight with respect to current order """
        questions = self.question_set.order_by('order')
        i = 1
        for question in questions:
            if question.order != i:
                question.order = i
                question.save()
            i += 1
        
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

class TestVersion(models.Model):
    """Used to mix up order or questions within groups"""
    test = models.ForeignKey(Test)
    
    
class QuestionGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __unicode__(self):
        return self.name
    

class QuestionAbstract(models.Model):
    question = RichTextField()
    group = models.ForeignKey(
        QuestionGroup,
        help_text="Group questions together on the test. Test variants are made by mixing up questions within the group. "+
            " The name can be anything you want and you may reuse names on different tests.",
        blank=True,
        null=True,
    )
    benchmarks = models.ManyToManyField(Benchmark, blank=True, null=True)
    themes = models.ManyToManyField(Theme, blank=True, null=True)
    type_choices = (
        ('Multiple Choice','Multiple Choice'), # Simple
        ('True/False','True/False'),        # Multiple Choice with only True or False options
        ('Essay','Essay'),                  # Teacher grades and fills in bubble
        ('Matching','Matching'),            # Same answers for a number of "questions" Question only printed once.
    )
    type = models.CharField(max_length=25, choices=type_choices, default='Multiple Choice')
    point_value = models.IntegerField(default=1)
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return strip_tags(self.question)


class QuestionBank(QuestionAbstract):
    pass
    
    
class Question(QuestionAbstract):
    test = models.ForeignKey(Test)
    order = models.IntegerField(blank=True,null=True)
    
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
                qb.answerbank_set.add(ab)
                
    def save(self, *args, **kwargs):
        if not self.order:
            self.order = self.test.question_set.filter(order__isnull=False).count() + 1 
        super(Question, self).save(*args, **kwargs)
    
    
class ErrorType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __unicode__(self):
        return self.name


class AnswerAbstract(models.Model):
    answer = RichTextField()
    error_type = models.ForeignKey(ErrorType, blank=True, null=True)
    point_value = models.IntegerField(default=0)
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return strip_tags(self.answer)
    
class AnswerBank(AnswerAbstract):
    question = models.ForeignKey(QuestionBank)
    
class Answer(AnswerAbstract):
    question = models.ForeignKey(Question)
    
    
class TestInstance(models.Model):
    student = models.ForeignKey('sis.Student')
    school_year = models.ForeignKey('sis.SchoolYear', blank=True, null=True)
    marking_period = models.ForeignKey('schedule.MarkingPeriod', blank=True, null=True)
    test = models.ForeignKey(Test)
    date = models.DateTimeField(auto_now_add=True)
    teachers = models.ManyToManyField('sis.Faculty', blank=True, null=True)
    results_recieved = models.BooleanField()
    def __unicode__(self):
        return '%s %s' % (self.student, self.test)
    
    @property
    def points_possible(self):
        data = self.test.question_set.aggregate(points_possible=Sum('point_value'))
        return data['points_possible']
    @property
    def points_earned(self):
        data = self.answerinstance_set.aggregate(points_earned=Sum('points_earned'))
        return data['points_earned']
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
    
    def clean(self):
        if not self.test_instance.test.question_set.filter(question=self.question).count():
            raise ValidationError('Test instance contains answers that are not part of the test!.')