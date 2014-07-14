import autocomplete_light
from .models import CourseSection

class CourseSectionAutocomplete(autocomplete_light.AutocompleteModelBase):
    split_words = True
    search_fields = ['name', 'course__fullname', 'course__shortname']

autocomplete_light.register(CourseSection, CourseSectionAutocomplete)
