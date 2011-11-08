from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.forms.widgets import TextInput

from models import *

class CustomFieldModel():
    """
    Abstract class adds some helper functions a Model
    """
    @property
    def get_custom_fields(self):
        return CustomField.objects.filter(content_type=ContentType.objects.get_for_model(self))
        
    def get_custom_field(self, field_name):
        content_type=ContentType.objects.get_for_model(self)
        return CustomField.objects.get(content_type=content_type,name=field_name)
        
    def get_custom_value(self, field_name):
        custom_field = self.get_custom_field(field_name)
        return CustomFieldValue.objects.get_or_create(field=custom_field,object_id=self.id)[0].value
        
    def set_custom_value(self, field_name, value):
        custom_field = self.get_custom_field(field_name)
        custom_value = CustomFieldValue.objects.get_or_create(field=custom_field,object_id=self.id)[0]
        custom_value.value = value
        custom_value.save()
    

class NumberInput(TextInput):
    input_type = 'number'

class CustomFieldAdmin(admin.ModelAdmin):
    """
    Abstract class addes functionality to deal with custom fields in Django admin.
    """
    def __create_custom_form(self, obj_id=None):
        custom_fields = CustomField.objects.filter(content_type=ContentType.objects.get_for_model(self.model))
        
        custom_form = forms.Form(prefix="cstm")
        for field in custom_fields:
            if field.field_type == 'i':
                custom_form.fields[field.name] = forms.IntegerField(label=field.name, required=False, widget=NumberInput(attrs={'style':'text-align:right;','step':1}))
            elif field.field_type == 'b':
                custom_form.fields[field.name] = forms.BooleanField(label=field.name, required=False)
            else:
                custom_form.fields[field.name] = forms.CharField(label=field.name, max_length=255, required=False)
            if obj_id:
                value = CustomFieldValue.objects.get_or_create(field=field,object_id=obj_id)[0]
                custom_form.fields[field.name].initial = value
        return custom_form
    
    def render_change_form(self, request, context, *args, **kwargs):
        if 'original' in context:
            context['custom_form'] = self.__create_custom_form(context['original'].id)
        else:
            context['custom_form'] = self.__create_custom_form()
        return super(CustomFieldAdmin, self).render_change_form(request, context, *args, **kwargs)
        
    def save_model(self, request, obj, form, change):
        super(CustomFieldAdmin, self).save_model(request, obj, form, change)
        custom_form = self.__create_custom_form()
        custom_form.data = request.POST
        custom_form.is_bound = True
        if custom_form.is_valid():
            data = custom_form.cleaned_data
            for key,data_field in data.items():
                custom_field = CustomField.objects.get_or_create(content_type=ContentType.objects.get_for_model(self.model), name=key)[0]
                custom_value = CustomFieldValue.objects.get_or_create(field=custom_field,object_id=obj.id)[0]
                custom_value.value = data_field
                custom_value.save()
        # Hope that client side validation works since we don't handle errors here!