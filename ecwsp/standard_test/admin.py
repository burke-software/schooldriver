from django.contrib import admin
from ecwsp.standard_test.models import StandardCategory, StandardCategoryGrade, StandardTest, StandardTestResult
from daterange_filter.filter import DateRangeFilter

class StandardCategoryInline(admin.TabularInline):
    model = StandardCategory
    extra = 1
    
class StandardTestAdmin(admin.ModelAdmin):
    inlines = (StandardCategoryInline,)
admin.site.register(StandardTest, StandardTestAdmin)

class StandardCategoryGradeInline(admin.TabularInline):
    model = StandardCategoryGrade
    extra = 1
    
class StandardTestResultAdmin(admin.ModelAdmin):
    inlines = (StandardCategoryGradeInline,)
    list_display = ['student', 'test', 'date']
    list_filter = ['test', ('date', DateRangeFilter)]
    search_fields = ['student__first_name', 'student__last_name', 'test__name']
admin.site.register(StandardTestResult, StandardTestResultAdmin)
