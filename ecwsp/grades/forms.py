from django import forms

from ecwsp.sis.forms import UploadFileForm
from ecwsp.schedule.forms import MarkingPeriodSelectForm
from .models import *
from .forms import *

class GradeUpload(UploadFileForm, MarkingPeriodSelectForm):
    pass
