from django import forms
from ecwsp.standard_test.models import StandardTest
from ecwsp.sis.forms import UploadFileForm

class UploadNaviance(forms.Form):
    import_file = forms.FileField()
    test = forms.ModelChoiceField(queryset=StandardTest.objects.all())
    
class UploadStandardTestResultForm(UploadFileForm):
    test = forms.ModelChoiceField(queryset=StandardTest.objects.all())