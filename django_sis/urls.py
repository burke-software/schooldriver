from django.conf.urls import include, patterns, url
from ecwsp.sis import views as sis_views
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import admin
from api.routers import api_urls
from responsive_dashboard import views as dashboard_views
from ecwsp.sis.views import AttendanceReportView
from django.http import HttpResponse

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
    (r'^ckeditor/', include('ckeditor.urls')),
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
    (r'^reports/(?P<name>attendance_report)/$', AttendanceReportView.as_view()),
    (r'^reports/', include('scaffold_report.urls')),
    url(r'^impersonate/', include('impersonate.urls')),
    url(r'^api/', include(api_urls)),
    url(r'^api/', include('api.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Angular routes (nice for reversing)
    url(r'^portal/', sis_views.SpaView.as_view(), name="portal-home"),
    url(r'^portal/grades/', sis_views.SpaView.as_view(), name="portal-grades"),
)

if settings.GAPPS:
    urlpatterns += patterns('', (r'^accounts/login/$', 'google_auth.views.login'), )
else:
    urlpatterns += patterns('', (r'^accounts/login/$', 'django.contrib.auth.views.login'), )

urlpatterns += patterns('',(r'^ldap_grp/', include('ldap_groups.urls')),)
urlpatterns += patterns('', (r'^discipline/', include('ecwsp.discipline.urls')), )
urlpatterns += patterns('', (r'^attendance/', include('ecwsp.attendance.urls')), )
urlpatterns += patterns('', (r'^schedule/', include('ecwsp.schedule.urls')), )
# Course is a nicer looking url
urlpatterns += patterns('', (r'^course/', include('ecwsp.schedule.urls')), )
urlpatterns += patterns('', (r'^grades/', include('ecwsp.grades.urls')), )
urlpatterns += patterns('', (r'^course/', include('ecwsp.grades.urls')), )
urlpatterns += patterns('', (r'^work_study/', include('ecwsp.work_study.urls')), )
urlpatterns += patterns('', (r'^admissions/', include('ecwsp.admissions.urls')), )
urlpatterns += patterns('', (r'^volunteer_track/', include('ecwsp.volunteer_track.urls')), )
urlpatterns += patterns('', (r'^gradebook/', include('ecwsp.gradebook.urls')), )
urlpatterns += patterns('', (r'^engrade_sync/', include('ecwsp.engrade_sync.urls')), )
urlpatterns += patterns('', (r'^naviance_sso/', include('ecwsp.naviance_sso.urls')), )
urlpatterns += patterns('', (r'^alumni/', include('ecwsp.alumni.urls')), )
urlpatterns += patterns('', (r'^counseling/', include('ecwsp.counseling.urls')), )
urlpatterns += patterns('', (r'^canvas_sync/', include('ecwsp.integrations.canvas_sync.urls')), )
urlpatterns += patterns('', (r'^schoolreach/', include('ecwsp.integrations.schoolreach.urls')), )
urlpatterns += patterns('',
    url(r'^rosetta/', include('rosetta.urls')),
)
if 'social.apps.django_app.default' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', url('', include('social.apps.django_app.urls', namespace='social')),)
if 'file_import' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',(r'^file_import/', include('file_import.urls')),)
if settings.MULTI_TENANT is True:
    urlpatterns += patterns('', (r'', include('ecwsp.customers.urls')), )

urlpatterns += patterns('', (r'^administration/', include('ecwsp.administration.urls')), )
urlpatterns += patterns('', (r'^', include('responsive_dashboard.urls')), )

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,})
    )
