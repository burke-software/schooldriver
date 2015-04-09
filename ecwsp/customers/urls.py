from django.conf.urls import patterns, url
from .views import SignUpView, SignUpThanksView


urlpatterns = patterns('',
    url(r'^sign-up/$', SignUpView.as_view(), name='sign-up'),
    url(r'^sign-up-thanks/$', SignUpThanksView.as_view(), name='sign-up-thanks'),
)
