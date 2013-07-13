from django.forms import *
import floppyforms as forms

class Form(forms.Form):
    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        for key, field in self.fields.items():
            if not 'class' in field.widget.attrs:
                field.widget.attrs['class'] = ''
            if isinstance(field, ChoiceField):
                if not 'multiselect' in field.widget.attrs['class']:
                    field.is_select = True
            elif isinstance(field, DateField):
                field.widget.attrs['class'] += ' datepicker'
            else:
                field.widget.attrs['class'] += ' text input'

class ModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.items():
            if not 'class' in field.widget.attrs:
                field.widget.attrs['class'] = ''
            if isinstance(field, ChoiceField):
                if not 'multiselect' in field.widget.attrs['class']:
                    field.is_select = True
            elif isinstance(field, DateField):
                field.widget.attrs['class'] += ' datepicker text input'
            else:
                field.widget.attrs['class'] += ' text input'
