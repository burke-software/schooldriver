from django import forms
from django.forms.widgets import CheckboxSelectMultiple, TextInput
from django.contrib.auth.models import User
from django.contrib.localflavor.us.forms import *

from ecwsp.engrade_sync.models import *
from ecwsp.schedule.models import MarkingPeriod

class SetupCoursesForm(forms.Form):
    marking_period = forms.ModelChoiceField(MarkingPeriod.objects.all())