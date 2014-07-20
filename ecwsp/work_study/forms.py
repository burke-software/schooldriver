from ecwsp.work_study.models import (StudentWorker, TimeSheet, Contact,
        TimeSheetPerformanceChoice, ClientVisit, WorkTeam, CompContract,
        Attendance)
from ecwsp.sis.forms import StudentReportWriterForm

from django import forms
from django.contrib.admin import widgets as adminwidgets
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape

from django.conf import settings

import autocomplete_light
from decimal import Decimal
from datetime import datetime, date
from itertools import chain


class CustomCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    items_per_row = 2 # Number of items per row
    
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = ['<table  style="width:99%;"><tr>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = ' for="%s"' % final_attrs['id']
            else:
                label_for = ''
    
            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            if i != 0 and i % self.items_per_row == 0:
                output.append('</tr><tr>')
            output.append('<td nowrap><label%s>%s %s</label></td>' % (label_for, rendered_cb, option_label))
        output.append('</tr></table>')
        return mark_safe('\n'.join(output))



class HorizRadioRenderer(forms.RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
        """Outputs radios"""
        return mark_safe(u'\n'.join([u' %s&nbsp;&nbsp; \n ' % w for w in self]))


class TdRadioRenderer(forms.RadioSelect.renderer):
    """ 
    this overrides widget method to put radio buttons in td's
    """
    def render(self):
        """Outputs radios"""
        #return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))
        return mark_safe(u'\n'.join([u'<td class="border " style="padding"> %s </td>\n' % w for w in self]))

class TdNoTextRadioRenderer(forms.RadioSelect.renderer):
    """ 
    this overrides widget method to put radio buttons in td's
    """
    def render(self):
        """Outputs radios"""
        #return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))
        return mark_safe(u'\n'.join([u'<td class="none nofont" style="font-size: 0px !important; padding-left:10px; padding-right:10px;"> <span style="font-size: 0px;">%s</span> </td>\n' % w for w in self]))


class TimeSheetForm(forms.ModelForm):
    class Meta:
        model = TimeSheet

    my_supervisor = forms.ModelChoiceField(queryset=Contact.objects.all(), required=False)
    date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS, validators=settings.DATE_VALIDATORS) 
    time_in = forms.TimeField(widget=forms.TextInput(attrs={'class': 'timecard-datefield'}))
    time_lunch = forms.TimeField(widget=forms.TextInput(attrs={'class': 'timecard-datefield'}))
    time_lunch_return = forms.TimeField(widget=forms.TextInput(attrs={'class': 'timecard-datefield'}))
    time_out = forms.TimeField(widget=forms.TextInput(attrs={'class': 'timecard-datefield'}))
    performance = forms.ModelChoiceField(queryset=TimeSheetPerformanceChoice.objects.all(),required=False,widget=forms.Select(attrs={'class':'timecard-performance'}))
    edit = forms.BooleanField(required=False)

    def set_supers(self, qs):
        self.fields["my_supervisor"].queryset = qs
        
    def clean(self):
        cleaned_data = self.cleaned_data
        time_in = cleaned_data.get("time_in")
        time_lunch = cleaned_data.get("time_lunch")
        time_lunch_return = cleaned_data.get("time_lunch_return")
        time_out = cleaned_data.get("time_out")
        
        # validate max hours
        try:
            hours = time_lunch.hour - time_in.hour
            mins = time_lunch.minute - time_in.minute
            hours += time_out.hour - time_lunch_return.hour
            mins += time_out.minute - time_lunch_return.minute
            hours += mins/Decimal(60)
        except:
            raise forms.ValidationError("You must fill out time in and time out.")
        if hours > settings.MAX_HOURS_DAY:
            raise forms.ValidationError("Only " + unicode(settings.MAX_HOURS_DAY) + " hours are allowed in one day.")
        elif hours <= 0:
            raise forms.ValidationError("You cannot have negative hours!")
            
        
        # validate time in and out
        if time_lunch_return < time_lunch:
            raise forms.ValidationError("Cannot return from lunch before leaving for lunch.")
        if time_in > time_out:
            raise forms.ValidationError("Cannot leave before starting. Check your times.")
        
        #Don't allow two in the same day.
        ts = TimeSheet.objects.filter(date=cleaned_data.get('date'), student=cleaned_data.get('student'))
        
        if ts.count() > 0 and not cleaned_data.get('edit'):
            conf, created = Configuration.objects.get_or_create(name="Allow multiple time sheets in one day")
            if created:
                conf.help_text = "True\nFalse"
                conf.save()
            if conf.value == "False":
                txt = "Cannot submit two time sheets in one day.\n Please edit an existings time sheet if you've" + \
                    " made a mistake. Approved time sheets may only be edited by a supervisor or cwsp staff."
                raise forms.ValidationError(txt)
        # Always return the full collection of cleaned data.
        return cleaned_data

class ChangeSupervisorForm(forms.ModelForm):    
    class Meta:
        model = StudentWorker
        fields = ('primary_contact',)
        
    def __init__(self, *args, **kwargs):
        comp = kwargs.pop('company')
        super(ChangeSupervisorForm, self).__init__(*args, **kwargs)
        self.fields["primary_contact"].queryset = Contact.objects.filter(workteam=comp)

        
class AddSupervisor(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('fname', 'lname', 'phone', 'phone_cell', 'email',)
    
class ReportBuilderForm(forms.Form):
    custom_billing_begin = forms.DateField(widget=adminwidgets.AdminDateWidget(), required=False, validators=settings.DATE_VALIDATORS)
    custom_billing_end = forms.DateField(widget=adminwidgets.AdminDateWidget(), required=False, validators=settings.DATE_VALIDATORS)

class ReportTemplateForm(StudentReportWriterForm):
    date_begin = None
    date_end = None
    student = autocomplete_light.MultipleChoiceField('StudentUserAutocomplete', required=False)
    
    def clean(self):
        data = self.cleaned_data
        if not data.get('student') and not data.get('all_students'):
            raise forms.ValidationError("You must either check \"all students\" or select a student")
        if not data.get('template') and not data.get('upload_template'):
            raise forms.ValidationError("You must either select a template or upload one.")
        return data

class DolForm(forms.ModelForm):
    class Meta:
        model = ClientVisit
        widgets = {
            'date': adminwidgets.AdminDateWidget(),
            'work_environment': forms.RadioSelect(renderer=HorizRadioRenderer),
            'attendance_and_punctuality': forms.RadioSelect(renderer=TdNoTextRadioRenderer),
            'attitude_and_motivation': forms.RadioSelect(renderer=TdNoTextRadioRenderer),
            'productivity_and_time_management': forms.RadioSelect(renderer=TdNoTextRadioRenderer),
            'ability_to_learn_new_tasks': forms.RadioSelect(renderer=TdNoTextRadioRenderer),
            'professional_appearance': forms.RadioSelect(renderer=TdNoTextRadioRenderer),
            'interaction_with_coworkers': forms.RadioSelect(renderer=TdNoTextRadioRenderer),
            'initiative_and_self_direction': forms.RadioSelect(renderer=TdNoTextRadioRenderer),
            'accuracy_and_attention_to_detail': forms.RadioSelect(renderer=TdNoTextRadioRenderer),
            'organizational_skills': forms.RadioSelect(renderer=TdNoTextRadioRenderer),
        }
    dol = forms.BooleanField(initial=True, required=False, widget=forms.CheckboxInput(attrs={'style':'visibility: hidden;'}))
    
    def save(self, *args, **kwargs):
        commit = kwargs.pop('commit', True)
        instance = super(DolForm, self).save(*args, commit = False, **kwargs)
        instance.dol = True
        if commit:
            instance.save()
        return instance

class StudentWorkerBulkChangeForm(forms.Form):
    day = forms.ChoiceField(choices=[['','----']]+StudentWorker.dayOfWeek, required=False)
    placement = forms.ModelChoiceField(queryset=WorkTeam.objects.all(), required=False)
    clear_placement = forms.BooleanField(help_text="Set placement to None", required=False)
    school_pay_rate = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    student_pay_rate = forms.DecimalField(max_digits=5, decimal_places=2, required=False)

# Django form wizard sucks, not using it
class CompanyContactForm1(forms.ModelForm):
    class Meta:
        model = CompContract
        fields = ('company', 'company_name', 'name', 'title', 'date', 'number_students')
        widgets = {
           'company': forms.HiddenInput(),
        }
    company_name = forms.CharField(max_length=255)
    name = forms.CharField(max_length=255)
    title = forms.CharField(max_length=255)
    number_students = forms.IntegerField()

class CompanyContactForm2(forms.ModelForm):
    class Meta:
        model = CompContract
        fields = (
            'payment',
            'student_functional_responsibilities',
            'student_functional_responsibilities_other',
            'student_desired_skills',
            'student_desired_skills_other',
            'student_leave',
            'student_leave_lunch',
            'student_leave_errands',
            'student_leave_other',
        )
        widgets = {
            'payment': forms.RadioSelect(),
            'student_leave': forms.Select(choices=(('0', 'No'), ('1', 'Yes'))),
            'student_desired_skills': CustomCheckboxSelectMultiple(),
            'student_functional_responsibilities': CustomCheckboxSelectMultiple(),
        }

class CompanyContactForm3(forms.ModelForm):
    class Meta:
        model = CompContract
        fields = (
            'name',
        )
    email = forms.EmailField()
    i_agree = forms.BooleanField()
    
class QuickAttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ('student', 'tardy', 'tardy_time_in')
        widgets = {
            'tardy_time_in': adminwidgets.AdminTimeWidget(attrs={'tabindex':"-1",}),
        }
