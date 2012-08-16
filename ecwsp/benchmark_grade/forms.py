#       Copyright 2012 Burke Software and Consulting LLC
#       Author John Milner <john@tmoj.net>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from django import forms
from ajax_select.fields import AutoCompleteSelectMultipleField
from django.contrib.admin import widgets as adminwidgets

from ecwsp.schedule.models import MarkingPeriod
from ecwsp.benchmark_grade.models import Item

class BenchmarkGradeVerifyForm(forms.Form):
    # whoever instantiates must assign queryset for marking_periods 
    all_students = forms.BooleanField(required=False)
    students = AutoCompleteSelectMultipleField('refering_course_student', required=False, label=u'Specific students', help_text=u'')
    marking_periods = forms.ModelMultipleChoiceField(queryset=MarkingPeriod.objects.none()) 
    all_demonstrations = forms.BooleanField(required=False)
    def clean(self):
        cleaned_data = super(BenchmarkGradeVerifyForm, self).clean()
        if cleaned_data['all_students']:
            # if the user requested all students and individual students,
            # honor all_students and remove individual students to prevent confusion
            self.data = self.data.copy() # often passed an immutable QueryDict
            del self.data['students']
            del cleaned_data['students']
        return cleaned_data

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        widgets = {
            'course': forms.HiddenInput,
            'date': adminwidgets.AdminDateWidget(),
        }
        
class GradebookFilterForm(forms.Form):
    cohort = forms.ModelChoiceField(queryset=None)
    marking_period = forms.ModelChoiceField(queryset=None)
    benchmark = forms.ModelChoiceField(queryset=None)
    assignment = forms.ModelChoiceField(queryset=None)
    assignment_type = forms.ModelChoiceField(queryset=None)