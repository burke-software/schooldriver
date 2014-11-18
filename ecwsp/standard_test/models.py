from django.db import models
from django.conf import settings

import datetime

class StandardTest(models.Model):
    """ A test such as SAT or ACT """
    name = models.CharField(max_length=255, unique=True)
    calculate_total = models.BooleanField(default=False,
        help_text = "Automatically calculate the total score by adding others together.",
    )
    cherry_pick_categories = models.BooleanField(default=False,
        help_text="Cherry pick results to generate total. Goes through each category and picks best scores, then calculates the total.",
    )
    cherry_pick_final = models.BooleanField(default=False, help_text="Cherry pick results to get total. Only use final scores.")
    show_on_reports = models.BooleanField(default=True)

    def __unicode__(self):
        return unicode(self.name)

    def get_cherry_pick_total(self, student):
        """ Returns cherry
        Why show real grades when fake ones look better?
        """
        cherry = 0
        if self.cherry_pick_final:
            for result in self.standardtestresult_set.filter(student=student,show_on_reports=True):
                cat_total = result.standardcategorygrade_set.filter(category__is_total=True).first()
                if cat_total is not None and cat_total.grade > cherry: cherry = cat_total.grade
        elif self.cherry_pick_categories:
            cats = self.standardcategory_set.filter(standardcategorygrade__result__show_on_reports=True,standardcategorygrade__result__student=student).annotate(highest=models.Max('standardcategorygrade__grade'))
            for cat in cats:
                cherry += cat.highest
        return cherry


class StandardCategory(models.Model):
    """ Category for a test """
    name = models.CharField(max_length=255)
    test = models.ForeignKey(StandardTest)
    is_total = models.BooleanField(default=False,
        help_text="This is the actual total. Use this for tests that do not use simple addition to calculate final scores.",
    )
    def __unicode__(self):
        return unicode(self.test) + ": " + unicode(self.name)

class StandardTestResult(models.Model):
    """ Standardized test instance. These are the results of a student taking a test. """
    date = models.DateField(default=datetime.date.today(), validators=settings.DATE_VALIDATORS)
    student = models.ForeignKey('sis.Student')
    test = models.ForeignKey(StandardTest)
    show_on_reports = models.BooleanField(default=True, help_text="If true, show this test result on a report such as a transcript. " + \
        "Note entire test types can be marked as shown on report or not. This is useful if you have a test that is usually shown, but have a few instances where you don't want it to show.")


    class Meta:
        unique_together = ('date', 'student', 'test')

    def __unicode__(self):
        try:
            return '%s %s %s' % (unicode(self.student), unicode(self.test), self.date)
        except:
            return "Standard Test Result"

    @property
    def total(self):
        """Returns total for the test instance
        This may be calculated or marked as "is_total" on the category
        """
        if self.test.calculate_total:
            total = 0
            for cat in self.standardcategorygrade_set.all():
                total += cat.grade
            return str(total).rstrip('0').rstrip('.')
        elif self.standardcategorygrade_set.filter(category__is_total=True):
            totals = self.standardcategorygrade_set.filter(category__is_total=True)
            if totals:
                return str(totals[0].grade).rstrip('0').rstrip('.')
        else:
            return 'N/A'

class StandardCategoryGrade(models.Model):
    """ Grade for a category and result """
    category = models.ForeignKey(StandardCategory)
    result = models.ForeignKey(StandardTestResult)
    grade = models.DecimalField(max_digits=6,decimal_places=2)
