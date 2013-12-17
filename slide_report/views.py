from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.views.generic.edit import ProcessFormView
from django.utils import simplejson
from .report import *

class SlideReportMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.report = slide_reports[kwargs['name']]()
        except KeyError:
            raise Http404
        self.model = self.report.model
        return super(SlideReportMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SlideReportMixin, self).get_context_data(**kwargs)
        context['report'] = self.report
        context['filters'] = self.report.filters
        return context
        

class SlideReportView(SlideReportMixin, TemplateView):
    """ Base class for reporting """
    template_name = "slide_report/report.html"


class FilterView(SlideReportMixin, FormView):
    template_name = "slide_report/filter.html"


class AjaxPreviewView(SlideReportMixin, TemplateView):
    """ Show a ajax preview table """
    template_name = "slide_report/table.html"
    
    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.POST.get('data', None):
            data = simplejson.loads(request.POST['data'])
            self.report.handle_post_data(data)
            context['filter_errors'] = self.report.filter_errors
        context['object_list'] = self.report.report_to_list(user=self.request.user, preview=True)
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super(AjaxPreviewView, self).get_context_data(**kwargs)
        context['headers'] = self.report.get_preview_fields()
        return context
