from django import template
from django.template.defaultfilters import escape
from django.utils.safestring import mark_safe
from django.utils.safestring import SafeUnicode
import os
import re
register = template.Library()

@register.filter
def in_group(user, group):
	"""Returns True/False if the user is in the given group(s).
	Usage::
		{% if user|in_group:"Friends" %}
		or
		{% if user|in_group:"Friends,Enemies" %}
		...
		{% endif %}
	You can specify a single group or comma-delimited list.
	No white space allowed.
	"""
	import re
	if re.search(',', group): group_list = re.sub('\s+','',group).split(',')
	elif re.search(' ', group): group_list = group.split()
	else: group_list = [group]
	user_groups = []
	for group in user.groups.all(): user_groups.append(str(group.name))
	if filter(lambda x:x in user_groups, group_list): return True
	else: return False
in_group.is_safe = True


class_re = re.compile(r'(?<=class=["\'])(.*)(?=["\'])')
@register.filter
def add_class(value, css_class):
    string = unicode(value)
    match = class_re.search(string)
    if match:
        m = re.search(r'^%s$|^%s\s|\s%s\s|\s%s$' % (css_class, css_class, 
                                                    css_class, css_class), match.group(1))
        print match.group(1)
        if not m:
            return mark_safe(class_re.sub(match.group(1) + " " + css_class, 
                                          string))
    else:
        return mark_safe(string.replace('>', ' class="%s">' % css_class))
    return value