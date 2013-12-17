from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django import forms

from ecwsp.alumni.models import *
from ecwsp.alumni.forms import *

class CollegeEnrollmentAdmin(admin.ModelAdmin):
    search_fields = ['college__name', 'alumni__student__first_name', 'alumni__student__last_name']
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

class AlumniPhoneNumberInline(admin.TabularInline):
    model = AlumniPhoneNumber
    extra = 0
    
class AlumniEmailInline(admin.TabularInline):
    model = AlumniEmail
    extra = 0

class AlumniNoteInline(admin.TabularInline):
    model = AlumniNote
    readonly_fields = ('user', 'date',)
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'style':'width:450px;',})},
    }
    
class EnrollmentInline(admin.StackedInline):
    model = CollegeEnrollment
    classes = ('grp-collapse grp-closed',)
    inline_classes = ('grp-collapse grp-open',)
    extra = 0

admin.site.register(AlumniNoteCategory)
    

class AlumniActionAdmin(admin.ModelAdmin):
    filter_horizontal = ['alumni']
admin.site.register(AlumniAction, AlumniActionAdmin)

class AlumniAdmin(admin.ModelAdmin):
    form = AlumniForm
    search_fields = ['student__first_name', 'student__last_name', 'college__name']
    list_filter = ['graduated', 'program_years', 'college', 'college_override', 'student__class_of_year']
    list_display = ['student', 'graduated', 'college']
    inlines = [AlumniEmailInline,AlumniPhoneNumberInline,WithdrawlInline, AlumniNoteInline,EnrollmentInline]
    
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
    
    def get_readonly_fields(self, request, obj=None):
        if obj: # Editing
            return self.readonly_fields + ('student',)
        return ()
    
    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup in ('student__id__exact',):
            return True
        return super(AlumniAdmin, self).lookup_allowed(lookup, *args, **kwargs)
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        # save(commit=False) will soon stop deleting, so we have to do it manually
        # https://code.djangoproject.com/ticket/10284
        # see also (scroll down): https://docs.djangoproject.com/en/dev/topics/forms/formsets/#django.forms.formsets.BaseFormSet.can_delete
        for obj in formset.deleted_objects:
            if obj.pk is not None: # don't try to double delete
                obj.delete()
        for instance in instances:
            if isinstance(instance, AlumniNote): #Check if it is the correct type of inline
                if(not instance.user):
                    instance.user = request.user        
            instance.save()
    
admin.site.register(Alumni, AlumniAdmin)

admin.site.register(AlumniStatus)
admin.site.register(AlumniNote)
