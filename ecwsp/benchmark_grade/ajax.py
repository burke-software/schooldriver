from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax
from ecwsp.benchmark_grade.models import Category

@dajaxice_register
def check_fixed_points_possible(request, category):
    dajax = Dajax()
    if Category.objects.get(id=category).fixed_points_possible is not None:
        dajax.assign('#id_item-points_possible', 'value', Category.objects.get(id=category).fixed_points_possible)
        dajax.assign('#id_item-points_possible', 'disabled', 'true')
    else:
        dajax.clear('#id_item-points_possible', 'disabled')
    return dajax.json()
