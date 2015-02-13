from django import forms

from ecwsp.sis.forms import UploadFileForm
from ecwsp.schedule.forms import MarkingPeriodSelectForm


class GradeUpload(UploadFileForm, MarkingPeriodSelectForm):
    pass
