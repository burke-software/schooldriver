from django.contrib import admin

from daterange_filter.filter import DateRangeFilter
import autocomplete_light

from .models import DisciplineActionInstance, Infraction, StudentDiscipline, DisciplineAction

class DisciplineActionInstanceInline(admin.TabularInline):
    model = DisciplineActionInstance
    extra = 1
    
class StudentDisciplineAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(StudentDiscipline)
    list_per_page = 50
    fields = ['date', 'students', 'teacher', 'infraction', 'comments', 'private_note']
    list_display = ('show_students', 'date', 'comment_brief', 'infraction')
    list_filter = [('date',DateRangeFilter), 'infraction', 'action',]
    search_fields = ['comments', 'students__first_name', 'students__last_name']
    inlines = [DisciplineActionInstanceInline]
    
    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup in ('students', 'students__id__exact',):
            return True
        return super(StudentDisciplineAdmin, self).lookup_allowed(lookup, *args, **kwargs)

admin.site.register(StudentDiscipline, StudentDisciplineAdmin)
admin.site.register(DisciplineAction)
admin.site.register(Infraction)
