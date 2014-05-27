import autocomplete_light
from .models import Student, EmergencyContact

class StudentAutocomplete(autocomplete_light.AutocompleteModelBase):
    choices=Student.objects.filter(is_active=True)
    search_fields = ['^first_name', 'last_name']
autocomplete_light.register(Student, StudentAutocomplete)

class LookupStudentAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    search_fields = ['^first_name', 'last_name']
    autocomplete_template = 'sis/lookup_student.html'
autocomplete_light.register(Student, LookupStudentAutocomplete)

class ContactAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    search_fields = ['^fname', 'lname']
    autocomplete_template = 'sis/autocomplete_contact.html'
    choice_template = 'sis/autocomplete_contact.html'
autocomplete_light.register(EmergencyContact, ContactAutocomplete)