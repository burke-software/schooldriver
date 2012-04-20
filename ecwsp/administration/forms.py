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

class TemplateForm(forms.ModelForm):
    class Meta:
        model = TimeSheet

    def clean(self):
        super(TemplateForm, self).clean()
        if self.cleaned_data.get('file'):
            file = self.cleaned_data['file'].name
            type = file.split('.')[-1]
            if not type in ['odt', 'ods', 'xls', 'xlsx']:
                raise forms.ValidationError("Must be odt, ods, or xls file.")
        return self.cleaned_data