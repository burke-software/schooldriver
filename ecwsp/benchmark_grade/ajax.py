from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax
from ecwsp.benchmark_grade.models import Category
from ecwsp.benchmark_grade.views import get_teacher_courses
from ecwsp.grades.models import Grade

@dajaxice_register
def check_fixed_points_possible(request, category):
    dajax = Dajax()
    if Category.objects.get(id=category).fixed_points_possible is not None:
        dajax.assign('#id_item-points_possible', 'value', Category.objects.get(id=category).fixed_points_possible)
        dajax.assign('#id_item-points_possible', 'disabled', 'true')
    else:
        dajax.clear('#id_item-points_possible', 'disabled')
    return dajax.json()

@dajaxice_register
def save_marking_period_average_comment(request, grade_pk, comment):
    dajax = Dajax()
    try:
        marking_period_average = Grade.objects.get(pk=grade_pk)
        authorized = False
        if request.user.is_superuser or request.user.groups.filter(name='registrar').count():
            authorized = True
        else:
            teacher_courses = get_teacher_courses(request.user.username)
            if teacher_courses is not None and marking_period_average.course in teacher_courses:
                # regular folk can't touch inactive marking periods
                if marking_period_average.marking_period.active:
                    authorized = True
        if not authorized:
            raise Exception() # ew. get a message framework already.
        if marking_period_average.comment != comment:
            marking_period_average.comment = comment
            marking_period_average.save()
            dajax.remove_css_class('#grade-comment{}'.format(grade_pk), 'danger')
            dajax.add_css_class('#grade-comment{}'.format(grade_pk), 'success')
        else:
            # we did nothing
            dajax.remove_css_class('#grade-comment{}'.format(grade_pk), 'danger')
            dajax.remove_css_class('#grade-comment{}'.format(grade_pk), 'success')
    except:
        dajax.remove_css_class('#grade-comment{}'.format(grade_pk), 'success')
        dajax.add_css_class('#grade-comment{}'.format(grade_pk), 'danger')
    return dajax.json()
