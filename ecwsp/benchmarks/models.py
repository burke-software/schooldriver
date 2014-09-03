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

class Benchmark(models.Model):
    measurement_topics = models.ManyToManyField('MeasurementTopic')
    number = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=700)
    year = models.ForeignKey('sis.GradeLevel', blank=True, null=True)

    def display_measurement_topics(self):
        txt = ""
        for topic in self.measurement_topics.all():
            txt += unicode(topic) + ", "
        if txt:
            return txt[:-2]

    def __unicode__(self):
        return unicode('%s %s' % (self.number, self.name))

    class Meta:
        ordering = ('number', 'name',)


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __unicode__(self):
        return self.name


class MeasurementTopic(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, blank=True, null=True)
    def __unicode__(self):
        if self.department:
            return unicode(self.department) + " - " + unicode(self.name)
        else:
            return unicode(self.name)
    class Meta:
        unique_together = ('name', 'department')
        ordering  = ('department','name')

