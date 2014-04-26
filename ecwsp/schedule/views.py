from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.models import Count
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory

from ecwsp.sis.models import *
from ecwsp.sis.uno_report import *
from ecwsp.sis.xl_report import XlReport
from ecwsp.schedule.models import *
from ecwsp.schedule.forms import *
from ecwsp.administration.models import *

from decimal import Decimal, ROUND_HALF_UP
import time
import logging

class struct(): pass

@user_passes_test(lambda u: u.groups.filter(name='faculty').count() > 0 or u.is_superuser, login_url='/')   
def schedule(request):
    years = SchoolYear.objects.all().order_by('-start_date')[:3]
    mps = MarkingPeriod.objects.all().order_by('-start_date')[:12]
    periods = Period.objects.all()[:20]
    courses = Course.objects.all().order_by('-startdate')[:20]
    
    if SchoolYear.objects.count() > 2: years.more = True
    if MarkingPeriod.objects.count() > 3: mps.more = True
    if Period.objects.count() > 6: periods.more = True
    if Course.objects.count() > 6: courses.more = True
    
    return render_to_response('schedule/schedule.html', {'request': request, 'years': years, 'mps': mps, 'periods': periods, 'courses': courses})

