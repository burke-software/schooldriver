import autocomplete_light
from .models import Student

autocomplete_light.register(Student,
    search_fields=['^first_name', 'last_name'],
    attrs={
        'placeholder': 'Look up student',
        'data-autocomplete-minimum-characters': 2,
    },
    widget_attrs={
        'data-widget-maximum-values': 10,
        'class': 'modern-style',
    },
)

class LookupStudentAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    search_fields = ['^first_name', 'last_name']
    autocomplete_template = 'sis/lookup_student.html'
autocomplete_light.register(Student, LookupStudentAutocomplete)