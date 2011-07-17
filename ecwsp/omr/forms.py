from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.forms.formsets import DELETION_FIELD_NAME
from django.contrib.admin.widgets import FilteredSelectMultiple

from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField

from ecwsp.omr.models import *
from ecwsp.sis.models import Student

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ('name', 'school_year', 'teachers', 'marking_period', 'courses')
    teachers = AutoCompleteSelectMultipleField('faculty', required=True)
    students = forms.ModelMultipleChoiceField(queryset=Student.objects.filter(inactive=False), widget=FilteredSelectMultiple("Students",False,attrs={'rows':'10'}), required=False)
    
    def save(self, *args, **kwargs):
        instance = super(TestForm, self).save(*args, **kwargs)
        instance.enroll_students(self.cleaned_data['students'])
        return instance

class TestQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        widgets = {
            'test': forms.HiddenInput,
        }
    benchmarks = AutoCompleteSelectMultipleField('benchmark', required=False)
    themes = AutoCompleteSelectMultipleField('theme', required=False)
        
AnswerFormSet = inlineformset_factory(Question, Answer, extra=0)
NewAnswerFormSet = inlineformset_factory(Question, Answer, extra=2)

#class BaseQuestionFormset(BaseInlineFormSet):
#    """ http://yergler.net/blog/2009/09/27/nested-formsets-with-django/ """
#    def add_fields(self, form, index):
#        # allow the super class to create the fields as usual
#        super(BaseQuestionFormset, self).add_fields(form, index)
#        # created the nested formset
#        try:
#            instance = self.get_queryset()[index]
#            pk_value = instance.pk
#        except IndexError:
#            instance=None
#            pk_value = form.prefix
#        # store the formset in the .nested property
#        
#        if self.data:
#            #self.data['ANSWERS_question_set-2-TOTAL_FORMS'] = 0
#            #self.data['ANSWERS_question_set-0-INITIAL_FORMS'] = 0
#            form.nested = [
#                AnswerFormset(data=self.data,
#                                instance = instance,
#                                prefix = 'ANSWERS_%s' % pk_value)]
#        else:
#            form.nested = [
#                AnswerFormset( instance = instance,
#                            prefix = 'ANSWERS_%s' % pk_value)]
#    
#    def is_valid(self):
#        result = super(BaseQuestionFormset, self).is_valid()
#        for form in self.forms:
#            if hasattr(form, 'nested'):
#                for n in form.nested:
#                    # make sure each nested formset is valid as well
#                    result = result and n.is_valid()
#        return result
#    
#    def save_new(self, form, commit=True):
#        """Saves and returns a new model instance for the given form."""
#        instance = super(BaseQuestionFormset, self).save_new(form, commit=commit)
#        # update the form's instance reference
#        form.instance = instance
#        # update the instance reference on nested forms
#        for nested in form.nested:
#            nested.instance = instance
#            # iterate over the cleaned_data of the nested formset and update the foreignkey reference
#            for cd in nested.cleaned_data:
#                cd[nested.fk.name] = instance
#        return instance
#    
#    def should_delete(self, form):
#        """Convenience method for determining if the form's object will
#        be deleted; cribbed from BaseModelFormSet.save_existing_objects."""
#        if self.can_delete:
#            raw_delete_value = form._raw_value(DELETION_FIELD_NAME)
#            should_delete = form.fields[DELETION_FIELD_NAME].clean(raw_delete_value)
#            return should_delete
# 
#        return False
# 
#    def save_all(self, commit=True):
#        """Save all formsets and along with their nested formsets."""
#        # Save without committing (so self.saved_forms is populated)
#        # -- We need self.saved_forms so we can go back and access
#        #    the nested formsets
#        objects = self.save(commit=False) 
#        # Save each instance if commit=True
#        if commit:
#            for o in objects:
#                o.save()
#
#        # save many to many fields if needed
#        if not commit:
#            self.save_m2m()
#        # save the nested formsets
#        for form in set(self.initial_forms + self.saved_forms):
#            if self.should_delete(form): continue
#            for nested in form.nested:
#                nested.save(commit=commit)
#    
#
#QuestionFormset = inlineformset_factory(Test, Question, form=TestQuestionForm, formset=BaseQuestionFormset, extra=10)