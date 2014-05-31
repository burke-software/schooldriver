import autocomplete_light
from .models import Student, EmergencyContact, Faculty

class UserAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^first_name', 'last_name']
    
class ActiveUserAutocomplete(UserAutocomplete):
    choices=Student.objects.filter(is_active=True)

class LookupStudentAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    search_fields = ['^first_name', 'last_name']
    autocomplete_template = 'sis/lookup_student.html'

class ContactAutocomplete(autocomplete_light.AutocompleteModelTemplate):
    search_fields = ['^fname', 'lname']
    autocomplete_template = 'sis/autocomplete_contact.html'
    choice_template = 'sis/autocomplete_contact.html'

autocomplete_light.register(EmergencyContact, ContactAutocomplete)
autocomplete_light.register(Student, UserAutocomplete)
autocomplete_light.register(Student, ActiveUserAutocomplete)
autocomplete_light.register(Faculty, ActiveUserAutocomplete)
autocomplete_light.register(Student, LookupStudentAutocomplete)
