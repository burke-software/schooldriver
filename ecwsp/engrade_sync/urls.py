from django.conf.urls import *
from views import *

urlpatterns = patterns('',
    (r'^setup/$', setup),
)
