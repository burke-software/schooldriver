from django.conf.urls.defaults import *
from ecwsp.sis.views import *
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include("massadmin.urls")),
    (r'^admin_export/', include("admin_export.urls")),
    (r'^ckeditor/', include('ckeditor.urls')),
    (r'^grappelli/', include('grappelli.urls')),
    (r'^$', 'ecwsp.sis.views.index'),

    (r'^sis/', include('ecwsp.sis.urls')),
    (r'^admin/jsi18n', 'django.views.i18n.javascript_catalog'),
    
    (r'^accounts/password_change/$', 'django.contrib.auth.views.password_change'),
    (r'^accounts/password_change_done/$', 'django.contrib.auth.views.password_change_done'),
    (r'^logout/$', logout_view),
  #  (r'^chart/$',chart_fte),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/jsi18n/$', 'django.views.i18n.javascript_catalog'),
    (r'^admin/', include(admin.site.urls) ),
    
    (r'^ajax_select/', include('ajax_select.urls')),
    (r'^ajax_filtered_fields/', include('ajax_filtered_fields.urls')),
)

if settings.GAPPS:
    urlpatterns += patterns('', (r'^accounts/login/$', 'google_auth.views.login'), )
else:
    urlpatterns += patterns('', (r'^accounts/login/$', 'django.contrib.auth.views.login'), )

if 'ldap_groups' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',(r'^ldap_grp/', include('ldap_groups.urls')),)
if 'admin_advanced_filter' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^admin_advanced_filter/', include('admin_advanced_filter.urls')), )
    
if 'ecwsp.discipline' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^discipline/', include('ecwsp.discipline.urls')), )
if 'ecwsp.attendance' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^attendance/', include('ecwsp.attendance.urls')), )
if 'ecwsp.schedule' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^schedule/', include('ecwsp.schedule.urls')), )
if 'ecwsp.work_study' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^work_study/', include('ecwsp.work_study.urls')), )
if 'ecwsp.admissions' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^admissions/', include('ecwsp.admissions.urls')), )
if 'ecwsp.omr' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^omr/', include('ecwsp.omr.urls')), )
if 'ecwsp.volunteer_track' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^volunteer_track/', include('ecwsp.volunteer_track.urls')), )
if 'ecwsp.benchmark_grade' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^benchmark_grade/', include('ecwsp.benchmark_grade.urls')), )
if 'ecwsp.inventory' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^inventory/', include('ecwsp.inventory.urls')), )
if 'ecwsp.engrade_sync' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^engrade_sync/', include('ecwsp.engrade_sync.urls')), )
if 'ecwsp.grades' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^grades/', include('ecwsp.grades.urls')), )
if 'ecwsp.naviance_sso' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^naviance_sso/', include('ecwsp.naviance_sso.urls')), )
if 'ecwsp.alumni' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^alumni/', include('ecwsp.alumni.urls')), )
if 'ecwsp.integrations.canvas_sync' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^canvas_sync/', include('ecwsp.integrations.canvas_sync.urls')), )
if 'ecwsp.integrations.schoolreach' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^schoolreach/', include('ecwsp.integrations.schoolreach.urls')), )
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )
if 'report_builder' in settings.INSTALLED_APPS:
    urlpatterns += url(r'^report_builder/', include('report_builder.urls')),
    
if 'sentry' in settings.INSTALLED_APPS:    
    urlpatterns += patterns('', (r'^sentry/', include('sentry.web.urls')),)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,})
    )

if settings.CAS:
    urlpatterns += patterns('',
        (r'^accounts/login/$', 'django_cas.views.login'),
        (r'^accounts/logout/$', 'django_cas.views.logout'),
    )

def handler500(request):
    """
    500 error handler which includes ``request`` in the context.

    Templates: `500.html`
    Context: None
    """
    from django.template import Context, loader
    from django.http import HttpResponseServerError

    t = loader.get_template('500.html') # You need to create a 500.html template.
    return HttpResponseServerError(t.render(Context({
        'request': request,
    })))
