import autocomplete_light
from .models import Student, EmergencyContact, Faculty

class UserAutocomplete(autocomplete_light.AutocompleteModelBase):
    split_words = True
    search_fields = ['first_name', 'last_name']
    attrs = {
        'placeholder': 'Lookup Student(s)',
    }

class ActiveUserAutocomplete(UserAutocomplete):
    choices=Student.objects.filter(is_active=True)

class LookupStudentAutocomplete(UserAutocomplete, autocomplete_light.AutocompleteModelTemplate):
    autocomplete_template = 'sis/lookup_student.html'

class ContactAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    split_words = True
    search_fields = ['fname', 'lname']
    attrs = {
        'placeholder': 'Lookup Contact(s)',
    }
    choice_template = 'sis/autocomplete_contact.html'

autocomplete_light.register(EmergencyContact, ContactAutocomplete)
autocomplete_light.register(Student, UserAutocomplete)
autocomplete_light.register(Student, ActiveUserAutocomplete)
autocomplete_light.register(Faculty, ActiveUserAutocomplete)
autocomplete_light.register(Student, LookupStudentAutocomplete)
