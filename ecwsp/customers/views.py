from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, TemplateView
from ecwsp.customers.tasks import create_tenant
from .models import SignUp, Client


class SignUpForm(forms.ModelForm):
    class Meta:
        model = SignUp
        fields = ('name', 'domain_url', 'client_name', 'client_email',
                  'client_number')

    def clean_domain_url(self):
        data = self.cleaned_data['domain_url']
        if data in ['dev', 'public', 'master']:
            raise forms.ValidationError('This domain url is reserved')
        if Client.objects.filter(domain_url=data).first():
            raise forms.ValidationError('This domain url is already taken')
        return data

    def clean_name(self):
        data = self.cleaned_data['name']
        if data in ['dev', 'public', 'master']:
            raise forms.ValidationError('This name is reserved')
        if Client.objects.filter(name=data).first():
            raise forms.ValidationError('This name is already taken')
        return data


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "sign-up.html"

    def form_valid(self, form):
        self.object = form.save()
        create_tenant.delay(self.object.pk)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('sign-up-thanks')


class SignUpThanksView(TemplateView):
    template_name = "sign-up-thanks.html"
