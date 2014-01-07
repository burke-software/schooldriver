from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.http import QueryDict
from .fields import SimpleCompareField
from abc import abstractmethod
import inspect
import six

class Filter(object):
    """ A customized filter for querysets """
    name = None
    verbose_name = None
    template_name = None
    fields = None
    form_class = None
    form = None
    raw_form_data = None
    add_fields = []
    
    def __init__(self, **kwargs):
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)
        self.build_form()

    @abstractmethod
    def queryset_filter(self, queryset, report_context=None, form=None):
        """ Allow custom handeling of queryset
        Must return the queryset.
        """
        return queryset
    
    def render_form(self):
        """ Render the form using a template
        Only called if template_name is defined """
        context = self.get_template_context()
        return render_to_string(self.template_name, context)
    
    def process_filter(self, queryset, report_context=None):
        """ Run the actual filter based on client data """
        is_valid = self.get_form_data()
        if is_valid:
            return self.queryset_filter(queryset, report_context=report_context)
        else:
            return queryset
    
    def get_template_context(self):
        """ Get the context to be shown when rendering a template just
        for this filter """
        context = {}
        if self.form:
            context['form'] = self.form
        return context
    
    def get_report_context(self, report_context):
        """ Process any data that needs set for an entire report """
        return report_context

    def build_form(self):
        """ Construct form out of fields or form """
        if not self.form_class:
            self.form_class = forms.Form
        self.form = self.form_class()
        self.form.fields['filter_number'] = forms.IntegerField(widget=forms.HiddenInput())
        if self.fields:
            for i, field in enumerate(self.fields):
                if inspect.isclass(field):
                    self.form.fields['field_' + str(i)] = field()
                else:
                    self.form.fields['field_' + str(i)] = field
                self.form.fields['field_' + str(i)].label = ''

    def get_form_data(self):
        form_dict = QueryDict(self.raw_form_data)
        # Manually bound the form instead of Form(data)
        self.form.data = form_dict
        self.form.is_bound = form_dict
        if self.form.is_valid():
            self.cleaned_data = self.form.cleaned_data
            return True
        else:
            return False

    def get_verbose_name(self):
        if self.verbose_name:
            return self.verbose_name
        return self.get_name()

    def get_name(self):
        """ return unique name of this filter """
        if self.name:
            return self.name
        return self.__class__.__name__


class DecimalCompareFilter(Filter):
    """ X greater, less, etc than decimal field """
    fields = [
        SimpleCompareField, 
        forms.DecimalField(decimal_places=2, max_digits=6, min_value=0,),
    ]
    compare_field_string = None

    def queryset_filter(self, queryset, report_context=None, **kwargs):
        compare = self.cleaned_data['field_0']
        value = self.cleaned_data['field_1']
        compare_kwarg = {self.compare_field_string + '__' + compare: value}
        return queryset.filter(**compare_kwarg)


class ModelMultipleChoiceFilter(Filter):
    fields = [forms.ModelMultipleChoiceField,]
    compare_field_string = None
    queryset = None
    
    def build_form(self):
        self.form = forms.Form()
        self.form.fields['filter_number'] = forms.IntegerField(widget=forms.HiddenInput())
        self.form.fields['field_0'] = forms.ModelMultipleChoiceField(self.queryset, label='')
    
    def queryset_filter(self, queryset, report_context=None, **kwargs):
        selected = self.cleaned_data['field_0']
        compare_kwarg = {self.compare_field_string + '__in': selected}
        return queryset.filter(**compare_kwarg)


class IntCompareFilter(DecimalCompareFilter):
    """ x greater, less, etc than int field """
    fields = [
        SimpleCompareField, 
        forms.IntegerField(),
    ]

