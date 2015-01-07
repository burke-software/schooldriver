from django.core.validators import MaxLengthValidator
from django.db import models
from constance import config


class GradeComment(models.Model):
    """ Optional pre defined comment
    Used when free thought on report cards is discouraged
    """
    # Allow users to set the id, instead of auto inc
    id = models.IntegerField(primary_key=True)
    comment = models.CharField(max_length=500)

    def __unicode__(self):
        return unicode(self.id) + ": " + unicode(self.comment)

    class Meta:
        ordering = ('id',)


def grade_comment_length_validator(value):
    max_length = config.GRADE_COMMEND_LENGTH_LIMIT
    validator = MaxLengthValidator(max_length)
    return validator(value)


class LetterGradeChoices(models.Model):
    """ Valid letter grade options """
    letter = models.CharField(max_length=50)

    def __unicode__(self):
        return self.letter


class Grade(models.Model):
    enrollment = models.ForeignKey('schedule.CourseEnrollment')
    marking_period = models.ForeignKey(
        'schedule.MarkingPeriod', blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)
    grade = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    comment = models.CharField(
        max_length=500, blank=True, validators=[grade_comment_length_validator])
    letter_grade = models.ForeignKey(LetterGradeChoices, blank=True, null=True)

    class Meta:
        unique_together = (("enrollment", "marking_period"),)
        permissions = (
            ("change_own_grade", "Change grades for own class"),
            ('change_own_final_grade', 'Change final YTD grades for own class'),
        )

    def __unicode__(self):
        return self.grade
