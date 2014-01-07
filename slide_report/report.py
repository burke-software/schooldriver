from django.conf import settings
from django.utils.importlib import import_module
from django import forms
from django.views.generic import FormView
import imp
import inspect
import copy

class SlideReport(object):
    """ Base class for any actual slide reports
    A slide report is named after UI effects for moving 
    various filters and previews into the report
    building screen. All reports require customized 
    options set by the programmer.
    """
    name = ""
    name_verbose = None
    model = None
    preview_fields = ['last_name', 'first_name']
    num_preview = 3
    filters = []

    def register(self):
        slide_reports[self.name] = self.__class__

    def __init__(self):
        if not self.name in slide_reports:
            self.register()
        self._possible_filters = [] # developer selected filters from subclass
        self._active_filters = [] # end user selected filters from view
        self.report_context = {}
        self.filter_errors = []
        self.add_fields = []
        for possible_filter in self.filters:
            self._possible_filters += [possible_filter]

    @property
    def get_name(self):
        if self.name_verbose != None:
            return self.name_verbose
        return self.name.replace('_', ' ')
    
    def handle_post_data(self, data):
        for filter_data in data:
            for possible_filter in self._possible_filters:
                if possible_filter.__class__.__name__ == filter_data['name']:
                    filter_instance = copy.copy(possible_filter)
                    filter_instance.build_form()
                    filter_instance.raw_form_data = filter_data.get('form', None)
                    self._active_filters += [filter_instance]

    def get_queryset(self):
        """ Return a queryset of the model
        filtering any active filters
        """
        report_context = {}
        queryset = self.model.objects.all()
        for active_filter in self._active_filters:
            queryset = active_filter.process_filter(queryset, report_context)
            if active_filter.form.errors:
                self.filter_errors += [{
                    'filter': active_filter.form.data['filter_number'],
                    'errors': active_filter.form.errors,
                }]
            else:
                report_context = active_filter.get_report_context(report_context)
                self.add_fields += active_filter.add_fields
        return queryset

    def report_to_list(self, user, preview=False):
        """ Convert to python list """
        queryset = self.get_queryset()
        if preview:
            queryset = queryset[:self.num_preview]

        if self.preview_fields:
            preview_fields = self.preview_fields
        else:
            preview_fields = ['__unicode__']

        result_list = []
        for obj in queryset:
            result_row = []
            for field in preview_fields:
                cell = getattr(obj, field)
                if callable(cell):
                    cell = cell()
                result_row += [cell]
            for field in self.add_fields:
                cell = getattr(obj, field)
                if callable(cell):
                    cell = cell()
                result_row += [cell]
                
            result_list += [result_row]
        return result_list

    def get_preview_fields(self):
        if self.preview_fields:
            preview_fields = []
            all_preview_fields = self.preview_fields + self.add_fields
            for field in all_preview_fields:
                try:
                    preview_fields += [self.model._meta.get_field_by_name(field)[0].verbose_name.title()]
                except:
                    preview_fields += [field.replace('_', ' ')]
            return preview_fields
        else:
            return [self.model._meta.verbose_name_plural.title()]


slide_reports = {}
for app in settings.INSTALLED_APPS:
    # try to import the app
    try:
        app_path = import_module(app).__path__
    except AttributeError:
        continue

    # try to find a app.slide_reports module
    try:
        imp.find_module('slide_reports', app_path)
    except ImportError:
        continue

    # looks like we found it so import it !
    import_module('%s.slide_reports' % app)
