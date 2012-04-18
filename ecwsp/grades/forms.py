from django import forms

from ecwsp.sis.forms import *
from ecwsp.schedule.forms import *
from models import *
from forms import *

class GradeUpload(UploadFileForm, MarkingPeriodSelectForm):
    pass