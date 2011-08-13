#       forms.py
#       
#       Copyright 2010 Cristo Rey New York High School
#        Author David M Burke <david@burkesoftware.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
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
from ecwsp.work_study.models import *
from ecwsp.administration.models import *
from ecwsp.sis.forms import StudentReportWriterForm

from django import forms
from django.contrib.admin import widgets as adminwidgets
from django.contrib.localflavor.us.forms import *
from django.contrib.formtools.wizard import FormWizard
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.conf import settings

from decimal import Decimal
from datetime import datetime, date
from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField
from itertools import chain

class StudentForm(forms.ModelForm):
    class Meta:
        model = StudentWorker
    
    ssn = USSocialSecurityNumberField(required=False)
    state = USStateField(required=False)
    zip = USZipCodeField(required=False)
    emergency_contacts = AutoCompleteSelectMultipleField('emergency_contact', required=False)


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


class MapImageWidget(forms.CheckboxInput):
    def render(self, name, value, attrs=None):
        output = []
        output.append(super(MapImageWidget, self).render(name, value, attrs))
        output.append("If checked, the above map file will be overwritten with Google Maps. <table><tr><td><a href=\"javascript:get_map()\">Preview Google Maps</a></td></tr><tr><td> <iframe width=\"400px\" height=\"400px\" name=\"mapframe\"></iframe> </td></tr></table>")
        return mark_safe(u''.join(output))
        
            
class TimeSheetForm(forms.ModelForm):
    class Meta:
        model = TimeSheet

    my_supervisor = forms.ModelChoiceField(queryset=Contact.objects.all(), required=False)
    date = forms.DateTimeField(widget=adminwidgets.AdminDateWidget()) 
    time_in = forms.TimeField()
    time_lunch = forms.TimeField()
    time_lunch_return = forms.TimeField()
    time_out = forms.TimeField()
    performance = forms.ChoiceField(required=False, widget = forms.RadioSelect(renderer=TdRadioRenderer), choices=(
        ('1', 'Unacceptable'), ('2', 'Expectations Not Met'), ('3', 'Meets Expectations'), 
        ('4', 'Exceeds Expectations'), ('5', 'Far Exceeds Expectations')))
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

class WorkTeamForm(forms.ModelForm):
    class Meta:
        model = WorkTeam
    
    use_google_maps = forms.BooleanField(required=False, widget=MapImageWidget)
        
class AddSupervisor(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('fname', 'lname', 'phone', 'phone_cell', 'email',)
    
class ReportBuilderForm(forms.Form):
    student_data = forms.BooleanField(required=False)
    student_demographics = forms.BooleanField(required=False)
    student_day = forms.BooleanField(required=False)
    student_fax = forms.BooleanField(required=False)
    student_email = forms.BooleanField(required=False)
    student_unique = forms.BooleanField(required=False)
    student_work_number = forms.BooleanField(required=False)
    student_year = forms.BooleanField(required=False)
    student_company = forms.BooleanField(required=False)
    student_primary_contact = forms.BooleanField(required=False)
    student_home = forms.BooleanField(required=False)
    student_contact = forms.BooleanField(required=False)
    student_contact_limit = forms.BooleanField(required=False)
    company_data = forms.BooleanField(required=False)
    company_login = forms.BooleanField(required=False)
    company_id = forms.BooleanField(required=False)
    company_paying = forms.BooleanField(required=False)
    company_industry = forms.BooleanField(required=False)
    company_cra = forms.BooleanField(required=False)
    company_pickup = forms.BooleanField(required=False)
    company_location = forms.BooleanField(required=False)
    company_dol = forms.BooleanField(required=False)
    contact_data = forms.BooleanField(required=False)
    contact_phone = forms.BooleanField(required=False)
    contact_cell_phone = forms.BooleanField(required=False)
    contact_email = forms.BooleanField(required=False)
    custom_billing_begin = forms.DateField(widget=adminwidgets.AdminDateWidget(), required=False)
    custom_billing_end = forms.DateField(widget=adminwidgets.AdminDateWidget(), required=False)

class ReportTemplateForm(StudentReportWriterForm):
    date_begin = None
    date_end = None
    student = AutoCompleteSelectMultipleField('studentworker', required=False)
    
    def clean(self):
        data = self.cleaned_data
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
    i_agree = forms.BooleanField()