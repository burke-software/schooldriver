from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib import messages
import os
from ecwsp.administration.models import Configuration

def is_installed(program):
    """ http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    Returns true if unix program name exists
    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    for path in os.environ["PATH"].split(os.pathsep):
        exe_file = os.path.join(path, program)
        if is_exe(exe_file):
            return True
    return False

class BadInstall(Exception):
    pass

def setup(request):
    can_sync = True
    if not is_installed('wine'):
        messages.warning(request, 'wine is not installed!')
        can_sync = False
    
    ez_binary_config = Configuration.get_or_default(
        'SchoolReach sync binary',
        default='',
        help_text='Upload EZDataSync.exe http://www.schoolreach.com/ez-school-data-integration.html')
    if not ez_binary_config.file:
        messages.warning(request, 'EZ data sync is not installed under configuration, SchoolReach sync binary!')
        can_sync = False
    elif not ez_binary_config.file.name[-3:] == "exe":
        messages.warning(request, 'EZ data sync binary %s is not an exe did you upload the right file?' % ez_binary_config.file.name)
        can_sync = False
    
    ez_binary_config = Configuration.get_or_default(
        'SchoolReach sync config',
        default='',
        help_text='EZ sync xml conf file made with EZ data sync (run it on your desktop)')
    if not ez_binary_config.file:
        messages.warning(request, 'EZ data sync config file is not installed under configuration, SchoolReach sync config!')
        can_sync = False
    elif not ez_binary_config.file.name[-3:] == "fig":
        messages.warning(request, 'EZ data sync config %s is not an config file did you upload the right file?' % ez_binary_config.file.name)
        can_sync = False
        
    if can_sync and request.POST:
        pass
        
    return render_to_response('schoolreach/setup.html', {
        'msg':'',
    }, RequestContext(request, {}),)

class SchoolReach:
    pass