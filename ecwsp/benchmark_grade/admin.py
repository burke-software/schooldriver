from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE

from ecwsp.benchmark_grade.models import Category, Item, Demonstration, Mark, Aggregate
from ecwsp.benchmark_grade.models import CalculationRulePerCourseCategory, CalculationRuleCategoryAsCourse, CalculationRule, AssignmentType 

admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Demonstration)
admin.site.register(Mark)
admin.site.register(Aggregate)
admin.site.register(AssignmentType)

class CalculationRulePerCourseCategoryInline(admin.TabularInline):
    model = CalculationRulePerCourseCategory
    verbose_name = 'Category included in each course average'
    verbose_name_plural = 'Categories included in each course average'
    extra = 0 

class CalculationRuleCategoryAsCourseInline(admin.TabularInline):
    model = CalculationRuleCategoryAsCourse
    verbose_name = 'Category treated as course in each marking period average'
    verbose_name_plural = 'Categories treated as courses in each marking period average'
    extra = 0
'''
class CalculationRuleSubstitutionInline(admin.TabularInline):
    model = CalculationRuleSubstitution
    extra = 0
'''
class CalculationRuleAdmin(admin.ModelAdmin):
    inlines = [CalculationRulePerCourseCategoryInline, CalculationRuleCategoryAsCourseInline]

admin.site.register(CalculationRule, CalculationRuleAdmin)
