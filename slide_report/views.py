from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.views.generic.edit import ProcessFormView
from django.utils import simplejson
from report_utils.utils import DataExportMixin
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


class DownloadReportView(DataExportMixin, SlideReportMixin, TemplateView):
    """ Show the report in various ways """
    template_name = "slide_report/table.html"
    
    def post(self, request, **kwargs):
        download_type = request.GET.get('type')
        context = self.get_context_data(**kwargs)
        if request.POST.get('data', None):
            data = simplejson.loads(request.POST['data'])
            self.report.handle_post_data(data)
            context['filter_errors'] = self.report.filter_errors
        
        if download_type == "preview":
            context['object_list'] = self.report.report_to_list(
                user=self.request.user, preview=True)
            context['headers'] = self.report.get_preview_fields()
            return render(request, self.template_name, context)
        elif download_type == "xlsx":
            data = self.report.report_to_list(self.request.user)
            return self.list_to_xlsx_response(data)
        elif download_type == 'django_admin':
            ids = self.report.get_queryset().values_list('id', flat=True)
            ids = ",".join(str(x) for x in ids)
            response = redirect('admin:{}_{}_changelist'.format(
                self.model._meta.app_label, self.model._meta.model_name))
            response['Location'] += '?id__in={}'.format(ids)
            return response
