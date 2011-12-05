from django import template

register = template.Library()
from django.template.defaultfilters import floatformat

@register.filter
def percentage(value):
    if value is None:
        return None
    try:
        return floatformat(value * 100.0, 0) + '%'
    except:
        return None