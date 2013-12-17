from django import forms
from django.core.exceptions import ImproperlyConfigured
from .fields import SimpleCompareField
from abc import abstractmethod
import inspect
import six

class Filter(object):
    """ A customized filter for querysets """
    name = None
    verbose_name = None
    fields = None
    form_class = None
    form = None
    raw_form_data = None
    
    def __init__(self, **kwargs):
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)
        self.build_form()

    @abstractmethod
    def queryset_filter(self, queryset, form=None):
        """ Allow custom handeling of queryset
        Must return the queryset.
        """
        return queryset 
    
    def process_filter(self, queryset):
        """ Run the actual filter based on client data """
        is_valid = self.get_form_data()
        if is_valid:
            return self.queryset_filter(queryset)
        else:
            return queryset

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
        from urlparse import urlparse, parse_qs
        form_dict = parse_qs(self.raw_form_data)
        for key, item in form_dict.items():
            form_dict[key] = item[0]
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

    def __init__(self, **kwargs):
        self.compare_field_string = None
        super(DecimalCompareFilter, self).__init__(**kwargs)
        if not self.compare_field_string:
            raise ImproperlyConfigured('Requires compare_field_string')

    def queryset_filter(self, queryset, **kwargs):
        compare = self.cleaned_data['field_0']
        value = self.cleaned_data['field_1']
        compare_kwarg = {self.compare_field_string + '__' + compare: value}
        return queryset.filter(**compare_kwarg)


class IntCompareFilter(DecimalCompareFilter):
    """ x greater, less, etc than int field """
    fields = [
        SimpleCompareField, 
        forms.IntegerField(),
    ]

