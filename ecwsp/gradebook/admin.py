from django.contrib import admin
from .models import CalculationRulePerCourseCategory


@admin.register(CalculationRulePerCourseCategory)
class CalculationRulePerCourseCategoryAdmin(admin.ModelAdmin):
    pass
