from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django import forms

from ecwsp.alumni.models import *
from ecwsp.alumni.forms import *

class CollegeEnrollmentAdmin(admin.ModelAdmin):
    search_fields = ['college__name', 'alumni__student__fname', 'alumni__student__lname']
    list_display = ['college', 'alumni', 'graduated', 'begin', 'end']
    list_filter = ['program_years', 'status', 'graduated']
admin.site.register(CollegeEnrollment, CollegeEnrollmentAdmin)

class CollegeAdmin(admin.ModelAdmin):
    search_fields = ['code', 'name', 'state']
    list_filter = ['type']
    list_display = ['code', 'name', 'state']
admin.site.register(College, CollegeAdmin)

class WithdrawlInline(admin.TabularInline):
    model = Withdrawl
    extra = 0

class AlumniNoteInline(admin.TabularInline):
    model = AlumniNote
    readonly_fields = ('user', 'date',)
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'style':'width:450px;',})},
    }

admin.site.register(AlumniNoteCategory)
    

class AlumniActionAdmin(admin.ModelAdmin):
    filter_horizontal = ['alumni']
admin.site.register(AlumniAction, AlumniActionAdmin)

class AlumniAdmin(admin.ModelAdmin):
    form = AlumniForm
    search_fields = ['student__fname', 'student__lname']
    list_filter = ['graduated', 'program_years']
    list_display = ['student', 'graduated', 'college']
    inlines = [WithdrawlInline, AlumniNoteInline]
    
    fieldsets = [
        (None, {
            'fields': ('student',)
        }),
        ('College', {
            'fields': ('college_override', 'college', 'on_track', 'graduated', 'graduation_date',
                       'status', 'program_years', 'semesters',)
        }),
        ('Actions', {
            'fields': ('alumniaction_set',)
        }),
    ]
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, AlumniNote): #Check if it is the correct type of inline
                if(not instance.user):
                    instance.user = request.user        
            instance.save()
    
admin.site.register(Alumni, AlumniAdmin)

admin.site.register(AlumniStatus)