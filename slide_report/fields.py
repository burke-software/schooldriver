from django import forms

class SimpleCompareField(forms.ChoiceField):
    default_choices = (
        ('exact', 'Equals'),
        ('gt', 'Greater than'),
        ('gte', 'Greater than or equals'),
        ('lt', 'Less than'),
        ('lte', 'Less than or equals'),
    )
    def __init__(self, **kwargs):
        kwargs['choices'] = self.default_choices
        return super(SimpleCompareField, self).__init__(**kwargs)
