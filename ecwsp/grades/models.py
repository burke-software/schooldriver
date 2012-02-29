from django.db import models
from ecwsp.schedule.models import *

from decimal import Decimal, ROUND_HALF_UP

class GradeComment(models.Model):
    id = models.IntegerField(primary_key=True)
    comment = models.CharField(max_length=500)
    
    def __unicode__(self):
        return unicode(self.id) + ": " + unicode(self.comment)
        
    class Meta:
        ordering = ('id',)
        

class Grade(models.Model):
    student = models.ForeignKey('sis.Student')
    course = models.ForeignKey(Course)
    marking_period = models.ForeignKey(MarkingPeriod, blank=True, null=True)
    date = models.DateField(auto_now=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    final = models.BooleanField(help_text="Yes for final grade. No for mid marking period report. Only final grades are included in the average.")
    override_final = models.BooleanField(help_text="Override final grade for marking period instead of calculating it.")
    comment = models.CharField(max_length=500, blank=True)
    letter_grade_choices = (
            ("I", "Incomplete"),
            ("P", "Pass"),
            ("F", "Fail"),
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
            ("HP", "High Pass"),
            ("LP", "Low Pass"),
        )
    letter_grade = models.CharField(max_length=2, blank=True, null=True, help_text="Will override grade.", choices=letter_grade_choices)
    
    class Meta:
        unique_together = (("student", "course", "marking_period", "final"),)
        permissions = (
            ("change_own_grade", "Change grades for own class"),
        )
        
    def display_grade(self):
        """ Returns full spelled out grade such as Fail, Pass, 60.05, B"""
        return self.get_grade(display=True)
    
    def set_grade(self, grade):
        """ set grade to decimal or letter 
            if grade is less than 1 assume it's a percentage
            returns success (True or False)"""
        try:
            grade = Decimal(str(grade))
            if grade < 1:
                # assume grade is a percentage
                grade = grade * 100
            self.grade = grade
            self.letter_grade = None
            return True
        except:
            grade = unicode.upper(unicode(grade)).strip()
            if grade in dict(self.letter_grade_choices):
                self.letter_grade = grade
                self.grade = None
                return True
            elif grade in ('', None, 'None'):
                self.grade = None
                self.letter_grade = None
                return True
            return False
    
    def get_grade(self, letter=False, display=False, rounding=None):
        """ By default returns simple grade such as 90.03, P, or F"""
        if self.letter_grade:
            if display:
                return self.get_letter_grade_display()
            else:
                return self.letter_grade
        elif self.grade:
            if rounding != None:
                string = '%.' + str(rounding) + 'f'
                return string % float(str(self.grade))
            else:
                return self.grade
        else:
            return ""
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.grade and self.letter_grade != None:
            raise ValidationError('Cannot have both numeric and letter grade')
    
    def save(self, *args, **kwargs):
        super(Grade, self).save(*args, **kwargs)
        
        #cache student's GPA
        if self.grade and self.student:
            self.student.cache_gpa = self.student.calculate_gpa()
            if self.student.cache_gpa != "N/A":
                self.student.save()
    
    def __unicode__(self):
        return unicode(self.get_grade(self))