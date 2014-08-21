import simplejson
from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax
from ecwsp.benchmark_grade.models import Category
from ecwsp.benchmark_grade.views import get_teacher_course_sections
from ecwsp.grades.models import Grade

@dajaxice_register
def check_fixed_points_possible(request, category):
    dajax = Dajax()
    if Category.objects.get(id=category).fixed_points_possible is not None:
        # str() otherwise json.dumps complains that it can't handle Decimals
        dajax.assign('#id_item-points_possible', 'value', str(Category.objects.get(id=category).fixed_points_possible))
        dajax.assign('#id_item-points_possible', 'disabled', 'true')
    else:
        dajax.clear('#id_item-points_possible', 'disabled')
    return dajax.json()

@dajaxice_register
def save_marking_period_average_comment(request, grade_pk, comment):
    dajax = Dajax()
    message = ""
    try:
        marking_period_average = Grade.objects.get(pk=grade_pk)
        authorized = False
        if request.user.is_superuser or request.user.groups.filter(name='registrar').count():
            authorized = True
        else:
            teacher_course_sections = get_teacher_course_sections(request.user.username)
            if teacher_course_sections is not None and marking_period_average.course_section in teacher_course_sections:
                # regular folk can't touch inactive marking periods
                if marking_period_average.marking_period.active:
                    authorized = True
                else:
                    message = "You may not modify an inactive marking period."
            else:
                message = "You may not modify this course section."
        if not authorized:
            raise Exception(message)
        if marking_period_average.comment != comment:
            marking_period_average.comment = comment
            marking_period_average.full_clean() # save() doesn't do validation
            marking_period_average.save()
            dajax.add_css_class('#grade-comment{}'.format(grade_pk), 'success')
        else:
            # we did nothing
            dajax.remove_css_class('#grade-comment{}'.format(grade_pk), 'success')
        dajax.remove_css_class('#grade-comment{}'.format(grade_pk), 'danger')
        dajax.script('hideAttentionGetter();')
    except Exception as e:
        dajax.remove_css_class('#grade-comment{}'.format(grade_pk), 'success')
        dajax.add_css_class('#grade-comment{}'.format(grade_pk), 'danger')
        if hasattr(e, 'messages'):
            message = u'; '.join(e.messages)
        elif hasattr(e, 'message'):
            message = e.message
        dajax.script(u'showAttentionGetter("{}");'.format(message))
    return dajax.json()
