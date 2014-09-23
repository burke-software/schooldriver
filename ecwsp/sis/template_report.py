from appy.pod.renderer import Renderer
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from ecwsp.administration.models import Configuration
from ecwsp.sis.models import SchoolYear, UserPreference
from ecwsp.sis.helper_functions import strip_unicode_to_ascii
from constance import config
import datetime
import tempfile
import os
import re


class TemplateReport(object):
    data = {}
    filename = "Template Report"
    
    def __init__(self, user=None):
        self.get_default_data()
        if user:
            self.file_format = UserPreference.objects.get_or_create(user=user)[0].get_format(type="document")
        
    
    def get_default_data(self):
        """ This data should be available to all templates
        """
        data={}
        data['school_name'] = config.SCHOOL_NAME
        try:
            data['school_year'] = unicode(SchoolYear.objects.get(active_year=True))
        except SchoolYear.DoesNotExist:
            data['school_year'] = SchoolYear.objects.create(
                active_year=True,
                name="Default Year",
                start_date = datetime.date.today(),
                end_date = datetime.date.today())
        data['date'] = unicode(datetime.date.today().strftime('%b %d, %Y'))
        data['long_date'] = unicode(datetime.date.today().strftime('%B %d, %Y'))
        self.data = data
        
        
    def pod_save(self, template, ext=None, get_tmp_file=False):
        """ Use Appy POD to make the report
        Returns a HttpRepsonse with the file.
        """
        import time
        
        if ext == None:
            #ext = "." + self.file_format
            ext = ".odt"
        
        # Strictly sanitize filename since Content-Disposition is really fussy
        filename = re.sub(
            '[^A-Za-z0-9]+',
            '_',
            strip_unicode_to_ascii(self.filename)
        )
        
        file_name = tempfile.gettempdir() + '/appy' + str(time.time()) + ext
        renderer = Renderer(template, self.data, file_name)
        renderer.run()
        
        if ext == ".doc":
            content = "application/msword"
        elif ext == ".docx":
            content = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ext == ".pdf":
            content = "application/pdf"
        elif ext == ".rtf":
            content = "application/rtf"
        elif ext == '.ods':
            content = "application/vnd.oasis.opendocument.spreadsheet"
        else: # odt, prefered
            content = "application/vnd.oasis.opendocument.text"
            
        if get_tmp_file:
            return file_name
        
        wrapper = FileWrapper(file(file_name)) # notice not using the tmp file! Not ideal.
        response = HttpResponse(wrapper, content_type=content)
        response['Content-Length'] = os.path.getsize(file_name)
        response['Content-Disposition'] = 'attachment; filename=' + filename + ext
        try: os.remove(file_name)
        except: pass # this sucks. But Ubuntu can't run ooo as www-data
        
        return response
