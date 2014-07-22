import floppyforms as forms
from django.db.models import Q
from django.conf import settings

from ecwsp.schedule.models import MarkingPeriod
from ecwsp.benchmark_grade.models import Item, AssignmentType, Category, Demonstration, Mark
from ecwsp.sis.models import Cohort
from ecwsp.benchmarks.models import Benchmark

class ItemForm(forms.ModelForm):
    def get_user_excludes(self):
        # get user-configured exclusions at runtime
        allowed_exclude = set(['marking_period', 'assignment_type', 'benchmark', 'date', 'description'])
        from ecwsp.administration.models import Configuration
        exclude = [x.strip() for x in Configuration.get_or_default('Gradebook hide fields').value.lower().split(',')] 
        exclude = set(exclude).intersection(allowed_exclude)
        return list(exclude)

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        for field_name in self.get_user_excludes():
            try:
                self.fields.pop(field_name)
            except KeyError:
                pass

    class Meta:
        model = Item
        widgets = {
            'date': forms.DateInput,
            'name': forms.TextInput,
            'description': forms.TextInput,
            'marking_period': forms.Select,
            'category': forms.Select,
            'points_possible': forms.NumberInput,
            'assignment_type': forms.Select,
            'course_section': forms.Select, #HiddenInput,
        }
        exclude = ('multiplier',) # also exclude user-configured fields; see __init__ above

class DemonstrationForm(forms.ModelForm):
    class Meta:
        model = Demonstration
        widgets = {
            'name': forms.TextInput,
            'item': forms.Select,
        }

class FillAllForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FillAllForm, self).__init__(*args, **kwargs)
        self.fields['mark'].label = 'Mark entire column'
    class Meta:
        model = Mark
        widgets = {
            'item': forms.HiddenInput,
            'demonstration': forms.HiddenInput,
            'student': forms.HiddenInput,
        }
        exclude = ('normalized_mark', 'description')
       
class GradebookFilterForm(forms.Form):
    cohort = forms.ModelChoiceField(queryset=None, widget=forms.Select(attrs={'onchange':'submit_filter_form(this.form)'}), required=False)
    marking_period = forms.ModelChoiceField(queryset=None, widget=forms.Select(attrs={'onchange':'submit_filter_form(this.form)'}), required=False)
    benchmark = forms.ModelMultipleChoiceField(queryset=None, required=False, widget=forms.SelectMultiple(attrs={'class': 'simple_multiselect'}))
    category = forms.ModelChoiceField(queryset=None, widget=forms.Select(attrs={'onchange':'submit_filter_form(this.form)'}), required=False)
    assignment_type = forms.ModelChoiceField(queryset=None, widget=forms.Select(attrs={'onchange':'submit_filter_form(this.form)'}), required=False)
    name = forms.CharField(required=False)
    date_begin = forms.DateField(required=False, widget=forms.DateInput(attrs={'placeholder':'Later than'}), validators=settings.DATE_VALIDATORS)
    date_end = forms.DateField(required=False, widget=forms.DateInput(attrs={'placeholder':'Earlier than'}), validators=settings.DATE_VALIDATORS)
    
    def update_querysets(self, course_section):
        self.fields['cohort'].queryset = Cohort.objects.filter(Q(percoursesectioncohort=None, student__coursesection=course_section) | Q(percoursesectioncohort__coursesection=course_section)).distinct().order_by('name')
        self.fields['marking_period'].queryset = MarkingPeriod.objects.filter(coursesection=course_section).distinct()
        self.fields['benchmark'].queryset = Benchmark.objects.filter(item__course_section=course_section).distinct()
        self.fields['assignment_type'].queryset = AssignmentType.objects.filter(item__course_section=course_section).distinct()
        self.fields['category'].queryset = Category.objects.filter(item__course_section=course_section).distinct()
