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

import floppyforms as forms
import ecwsp.gumby_forms as forms
from ajax_select.fields import AutoCompleteSelectMultipleField
from django.contrib.admin import widgets as adminwidgets
from django.db.models import Q
from django.conf import settings

from ecwsp.schedule.models import MarkingPeriod
from ecwsp.benchmark_grade.models import Item, AssignmentType, Category, Demonstration, Mark
from ecwsp.sis.models import Cohort
from ecwsp.benchmarks.models import Benchmark

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        widgets = {
            'course': forms.HiddenInput,
            'date': adminwidgets.AdminDateWidget(),
        }
        exclude = ('scale','multiplier',)

class DemonstrationForm(forms.ModelForm):
    class Meta:
        model = Demonstration

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
    benchmark = forms.ModelMultipleChoiceField(queryset=None, required=False)
    category = forms.ModelChoiceField(queryset=None, widget=forms.Select(attrs={'onchange':'submit_filter_form(this.form)'}), required=False)
    assignment_type = forms.ModelChoiceField(queryset=None, widget=forms.Select(attrs={'onchange':'submit_filter_form(this.form)'}), required=False)
    name = forms.CharField(required=False)
    date_begin = forms.DateField(required=False, widget=adminwidgets.AdminDateWidget(attrs={'placeholder':'Later than'}), validators=settings.DATE_VALIDATORS)
    date_end = forms.DateField(required=False, widget=adminwidgets.AdminDateWidget(attrs={'placeholder':'Earlier than'}), validators=settings.DATE_VALIDATORS)
    
    def update_querysets(self, course):
        self.fields['cohort'].queryset = Cohort.objects.filter(Q(percoursecohort=None, student__course=course) | Q(percoursecohort__course=course)).distinct().order_by('name')
        self.fields['marking_period'].queryset = MarkingPeriod.objects.filter(course=course).distinct()
        self.fields['benchmark'].queryset = Benchmark.objects.filter(item__course=course).distinct()
        self.fields['assignment_type'].queryset = AssignmentType.objects.filter(item__course=course).distinct()
        self.fields['category'].queryset = Category.objects.filter(item__course=course).distinct()
