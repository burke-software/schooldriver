from django.conf.urls import include, patterns, url
from ecwsp.sis import views as sis_views
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import admin
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from api.routers import api_urls
from responsive_dashboard import views as dashboard_views
from ecwsp.sis.views import AttendanceReportView
from django.http import HttpResponse

dajaxice_autodiscover()
admin.autodiscover()
admin.site.login = login_required(admin.site.login)

def robots(request):
    ''' Try to prevent search engines from indexing
    uploaded media. Make sure your web server is
    configured to deny directory listings. '''
    return HttpResponse(
        'User-agent: *\r\nDisallow: /media/\r\n',
        content_type='text/plain'
    )

urlpatterns = patterns('',
    (r'^robots.txt', robots),
    (r'^admin/', include("massadmin.urls")),
    (r'^admin_export/', include("admin_export.urls")),
    (r'^ckeditor/', include('ecwsp.ckeditor_urls')),#include('ckeditor.urls')),
    (r'^grappelli/', include('grappelli.urls')),
    (r'^$', 'ecwsp.sis.views.index'),
    (r'^sis/', include('ecwsp.sis.urls')),
    (r'^admin/jsi18n', 'django.views.i18n.javascript_catalog'),

    (r'^report_builder/', include('report_builder.urls')),
    (r'^simple_import/', include('simple_import.urls')),
    url(r'^accounts/password_change/$', 'django.contrib.auth.views.password_change'),
    url(r'^accounts/password_change_done/$', 'django.contrib.auth.views.password_change_done', name="password_change_done"),

    (r'^logout/$', sis_views.logout_view),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/jsi18n/$', 'django.views.i18n.javascript_catalog'),
    (r'^admin/', include(admin.site.urls) ),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(dajaxice_config.dajaxice_url, include('ecwsp.dajaxice_urls')),
    (r'^reports/(?P<name>attendance_report)/$', AttendanceReportView.as_view()),
    (r'^reports/', include('scaffold_report.urls')),
    url(r'^impersonate/', include('impersonate.urls')),
    url(r'^api/', include(api_urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)

if settings.GAPPS:
    urlpatterns += patterns('', (r'^accounts/login/$', 'google_auth.views.login'), )
else:
    urlpatterns += patterns('', (r'^accounts/login/$', 'django.contrib.auth.views.login'), )

if 'ldap_groups' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',(r'^ldap_grp/', include('ldap_groups.urls')),)
if 'ecwsp.discipline' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^discipline/', include('ecwsp.discipline.urls')), )
if 'ecwsp.attendance' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^attendance/', include('ecwsp.attendance.urls')), )
if 'ecwsp.schedule' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^schedule/', include('ecwsp.schedule.urls')), )
    # Course is a nicer looking url
    urlpatterns += patterns('', (r'^course/', include('ecwsp.schedule.urls')), )
    urlpatterns += patterns('', (r'^grades/', include('ecwsp.grades_new.urls')), )
    urlpatterns += patterns('', (r'^course/', include('ecwsp.grades_new.urls')), )
if 'ecwsp.work_study' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^work_study/', include('ecwsp.work_study.urls')), )
if 'ecwsp.admissions' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^admissions/', include('ecwsp.admissions.urls')), )
if 'ecwsp.volunteer_track' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^volunteer_track/', include('ecwsp.volunteer_track.urls')), )
    urlpatterns += patterns('', (r'^gradebook/', include('ecwsp.gradebook.urls')), )
if 'ecwsp.inventory' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^inventory/', include('ecwsp.inventory.urls')), )
if 'ecwsp.engrade_sync' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^engrade_sync/', include('ecwsp.engrade_sync.urls')), )
if 'ecwsp.naviance_sso' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^naviance_sso/', include('ecwsp.naviance_sso.urls')), )
if 'ecwsp.alumni' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^alumni/', include('ecwsp.alumni.urls')), )
if 'ecwsp.counseling' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^counseling/', include('ecwsp.counseling.urls')), )
if 'ecwsp.integrations.canvas_sync' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^canvas_sync/', include('ecwsp.integrations.canvas_sync.urls')), )
if 'ecwsp.integrations.schoolreach' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', (r'^schoolreach/', include('ecwsp.integrations.schoolreach.urls')), )
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )
if 'social.apps.django_app.default' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', url('', include('social.apps.django_app.urls', namespace='social')),)
if 'file_import' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',(r'^file_import/', include('file_import.urls')),)

urlpatterns += patterns('', (r'^administration/', include('ecwsp.administration.urls')), )
urlpatterns += patterns('', (r'^', include('responsive_dashboard.urls')), )

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,})
    )
