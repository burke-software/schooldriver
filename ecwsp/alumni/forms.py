from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from ecwsp.alumni.models import *

import decimal

class AlumniNoteForm(forms.ModelForm):
    class Meta:
        model = AlumniNote
        fields = ('alumni','category','note')
        widgets = {'alumni': forms.HiddenInput()}

class AlumniForm(forms.ModelForm):
    class Meta:
        model = Alumni
    
    def clean(self):
        data = self.cleaned_data
        semesters = data.get("semesters")
        if semesters and semesters != "ALL":
            try: Decimal(semesters)
            except InvalidOperation:
                raise forms.ValidationError("Semesters must be a number or ALL")
        return data
    
    alumniaction_set = forms.ModelMultipleChoiceField(
        queryset=AlumniAction.objects.all(), 
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=('Actions'),
            is_stacked=False
        ),
        help_text='<a href="/admin/alumni/alumniaction/add/" target="_blank"> Add Action </a>'
    )
        
    def __init__(self, *args, **kwargs):
        super(AlumniForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['alumniaction_set'].initial = self.instance.alumniaction_set.all()

    def save(self, commit=True):
        alumni = super(AlumniForm, self).save(commit=False)
        if commit:
            alumni.save()
        if alumni.pk:
            alumni.alumniaction_set = self.cleaned_data['alumniaction_set']
        self.save_m2m()
        return alumni