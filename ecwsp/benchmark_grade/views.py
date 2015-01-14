from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q, Max, Count, Avg
from django.db import transaction
from django.template import RequestContext
from django.core.urlresolvers import reverse

from ecwsp.sis.models import SchoolYear, Student, Faculty
from ecwsp.schedule.models import CourseSection, MarkingPeriod
from ecwsp.grades.models import Grade
from ecwsp.grades.forms import GradeUpload
from ecwsp.administration.models import Configuration
from ecwsp.benchmark_grade.models import Category, Mark, Aggregate, Item, Demonstration, CalculationRule, AggregateTask, CalculationRulePerCourseCategory
from ecwsp.benchmark_grade.forms import GradebookFilterForm, ItemForm, DemonstrationForm, FillAllForm
from ecwsp.benchmarks.models import Benchmark
from ecwsp.benchmark_grade.utility import gradebook_get_average, gradebook_get_average_and_pk, gradebook_recalculate_on_item_change, gradebook_recalculate_on_mark_change
from ecwsp.benchmark_grade.utility import benchmark_find_calculation_rule

from decimal import Decimal
import logging
import json
import datetime
import reversion

def make_validationerror_raiser(message):
    from django.core.exceptions import ValidationError
    ''' Returns a function that raises a ValidationError with the specified message '''
    def validationerror_raiser(value):
        ''' Ignores specified value and raises a ValidationError '''
        raise ValidationError(message)
    return validationerror_raiser

def require_active_marking_period(marking_period):
    from django.core.exceptions import ValidationError
    if not marking_period.active:
        raise ValidationError('{} is not an active marking period.'.format(marking_period))

def require_item_in_active_marking_period(item):
    from django.core.exceptions import ValidationError
    if item.marking_period and not item.marking_period.active:
        raise ValidationError("This item's marking period, {}, is not active.".format(item.marking_period))

def get_teacher_course_sections(username):
    """ Utility function that returns course sections a given teacher may access """
    try:
        teacher = Faculty.objects.get(username=username)
        teacher_course_sections = CourseSection.objects.filter(
            course__graded=True,
            marking_period__school_year__active_year=True,
            teachers=teacher
        ).distinct()
    except Faculty.DoesNotExist:
        teacher_course_sections = None
    return teacher_course_sections


@staff_member_required
def gradebook(request, course_section_id, for_export=False):
    #if 'bypass' not in request.GET:
    #    return HttpResponse('Gradebooks are temporarily unavailable while urgent maintenance is performed. We apologize for the inconvenience.')
    course_section = get_object_or_404(CourseSection, pk=course_section_id)
    # lots of stuff will fail unceremoniously if there are no MPs assigned
    if not course_section.marking_period.count():
        messages.add_message(request, messages.ERROR,
            'The gradebook cannot be opened because there are no marking ' \
            ' periods assigned to the course section ' +
            course_section.name + '.')
        return HttpResponseRedirect(reverse('admin:index'))

    school_year = course_section.marking_period.all()[0].school_year
    try:
        calculation_rule = benchmark_find_calculation_rule(school_year)
    except Exception as e:
        if "There is no suitable calculation rule for the school year" not in unicode(e):
            raise
        messages.add_message(request, messages.ERROR, e)
        return HttpResponseRedirect(reverse('admin:index'))
    teacher_course_sections = get_teacher_course_sections(request.user.username)
    extra_info = Configuration.get_or_default('Gradebook extra information').value.lower().strip()
    quantizer = Decimal(10) ** (-1 * calculation_rule.decimal_places)
    if not request.user.is_superuser and not request.user.groups.filter(name='registrar').count() and \
    (teacher_course_sections is None or course_section not in teacher_course_sections):
        messages.add_message(request, messages.ERROR,
            'You do not have access to the gradebook for ' + course_section.name + '.')
        return HttpResponseRedirect(reverse('admin:index'))

    students = Student.objects.filter(is_active=True, coursesection=course_section)
    items = Item.objects.filter(course_section=course_section)
    filtered = False
    temporary_aggregate = False
    totals = {
        'filtered_average': Decimal(0),
        'filtered_average_count': Decimal(0),
        'course_section_average': Decimal(0),
        'course_section_average_count': Decimal(0),
        'filtered_standards_passing': 0,
        'filtered_standards_all': 0,
        'standards_passing': 0,
        'standards_all': 0
    }

    if request.GET:
        filter_form = GradebookFilterForm(request.GET)
        filter_form.update_querysets(course_section)
        if filter_form.is_valid():
            for filter_key, filter_value in filter_form.cleaned_data.iteritems():
                if filter_value is not None:
                    try:
                        if not len(filter_value):
                            continue
                    except TypeError:
                        # not everything has a len
                        pass
                    if filter_key == 'cohort': 
                        students = students.filter(cohorts=filter_value)
                        temporary_aggregate = True
                    if filter_key == 'marking_period':
                        items = items.filter(marking_period=filter_value)
                    if filter_key == 'benchmark':
                        items = items.filter(benchmark__in=filter_value)
                        temporary_aggregate = True
                    if filter_key == 'category':
                        items = items.filter(category=filter_value)
                    if filter_key == 'assignment_type':
                        items = items.filter(assignment_type=filter_value)
                        temporary_aggregate = True
                    if filter_key == 'name':
                        items = items.filter(name__icontains=filter_value)
                        temporary_aggregate = True
                    if filter_key == 'date_begin':
                        items = items.filter(date__gt=filter_value)
                        temporary_aggregate = True
                    if filter_key == 'date_end':
                        items = items.filter(date__lt=filter_value)
                        temporary_aggregate = True
                    filtered = True
    else:
        # show only the active marking period by default
        active_mps = course_section.marking_period.filter(active=True)
        if active_mps and not for_export: # no default filtering on export requests
            filter_form = GradebookFilterForm(initial={'marking_period': active_mps[0]})
            items = items.filter(marking_period=active_mps[0])
            filtered = True
        else:
            filter_form = GradebookFilterForm()
        filter_form.update_querysets(course_section)
        
    # make a note of any aggregates pending recalculation
    pending_aggregate_pks = Aggregate.objects.filter(course_section=course_section, aggregatetask__in=AggregateTask.objects.all()).values_list('pk', flat=True).distinct()
    
    # Freeze these now in case someone else gets in here!
    # TODO: something that actually works. all() does not evaluate a QuerySet.
    # https://docs.djangoproject.com/en/dev/ref/models/querysets/#when-querysets-are-evaluated
    items = items.order_by('id').all()
    # whoa, super roll of the dice. is Item.demonstration_set really guaranteed to be ordered by id?
    # precarious; sorting must match items (and demonstrations!) exactly
    marks = Mark.objects.filter(item__in=items).order_by('item__id', 'demonstration__id').all() 
    items_count = items.filter(demonstration=None).count() + Demonstration.objects.filter(item__in=items).count()
    for student in students:
        student_marks = marks.filter(student=student).exclude(item__category__allow_multiple_demonstrations=True, demonstration=None).select_related('item__category_id')
        student_marks_count = student_marks.count()
        if student_marks_count < items_count:
            # maybe student enrolled after assignments were created
            for item in items:
                if len(item.demonstration_set.all()):
                    # must create mark for each demonstration
                    for demonstration in item.demonstration_set.all():
                        mark, created = Mark.objects.get_or_create(item=item, demonstration=demonstration, student=student)
                    # Create one extra with demonstration=None to store the aggregate of Demonstrations
                    mark, created = Mark.objects.get_or_create(item=item, demonstration=None, student=student)
                else:
                    # a regular item without demonstrations; make only one mark
                    mark, created = Mark.objects.get_or_create(item=item, student=student)
        if student_marks_count > items_count:
            # Yikes, there are multiple marks per student per item. Stop loading the gradebook now.
            if 'dangerous' in request.GET:
                pass
            else:
                raise Exception('Multiple marks per student per item.')
        
        for mark in student_marks:
            mark.category_id = mark.item.category_id
        
        student.marks = student_marks
        student.average, student.average_pk = gradebook_get_average_and_pk(student, course_section, None, None, None)
        if student.average is not None:
            totals['course_section_average'] += Aggregate.objects.get(pk=student.average_pk).cached_value # can't use a substitution
            totals['course_section_average_count'] += 1
        if filtered:
            cleaned_or_initial = getattr(filter_form, 'cleaned_data', filter_form.initial)
            filter_category = cleaned_or_initial.get('category', None)
            filter_marking_period = cleaned_or_initial.get('marking_period', None)
            filter_items = items if temporary_aggregate else None
            student.filtered_average, student.filtered_average_pk = gradebook_get_average_and_pk(
                student, course_section, filter_category, filter_marking_period, filter_items)
            if student.filtered_average is not None:
                totals['filtered_average'] += Aggregate.objects.get(pk=student.filtered_average_pk).cached_value # can't use a substitution
                totals['filtered_average_count'] += 1
        if school_year.benchmark_grade and extra_info == 'demonstrations':
            # TC's column of counts
            # TODO: don't hardcode
            standards_category = Category.objects.get(name='Standards')
            PASSING_GRADE = 3
            standards_objects = Item.objects.filter(course_section=course_section, category=standards_category, mark__student=student).annotate(best_mark=Max('mark__mark')).exclude(best_mark=None)
            standards_count_passing = standards_objects.filter(best_mark__gte=PASSING_GRADE).count()
            standards_count_total = standards_objects.count()
            totals['standards_passing'] += standards_count_passing
            totals['standards_all'] += standards_count_total
            if standards_count_total:
                student.standards_counts = '{} / {} ({:.0f}%)'.format(standards_count_passing, standards_count_total, 100.0 * standards_count_passing / standards_count_total)
            else:
                student.standards_counts = None
            if filtered:
                standards_objects = items.filter(course_section=course_section, category=standards_category, mark__student=student).annotate(best_mark=Max('mark__mark')).exclude(best_mark=None)
                standards_count_passing = standards_objects.filter(best_mark__gte=PASSING_GRADE).count()
                standards_count_total = standards_objects.count()
                totals['filtered_standards_passing'] += standards_count_passing
                totals['filtered_standards_all'] += standards_count_total
                if standards_count_total:
                    student.filtered_standards_counts = '{} / {} ({:.0f}%)'.format(standards_count_passing, standards_count_total, 100.0 * standards_count_passing / standards_count_total)
                else:
                    student.filtered_standards_counts = None

            # TC's row of counts
            # TODO: don't hardcode
            for item in items:
                if item.category != standards_category:
                    item.marks_counts = 'N/A'
                    continue
                if item.category.allow_multiple_demonstrations:
                    mark_set = item.mark_set.exclude(demonstration=None)
                else:
                    mark_set = item.mark_set.filter(demonstration=None)
                marks_count_passing = mark_set.filter(mark__gte=PASSING_GRADE).count()
                marks_count_total = mark_set.exclude(mark=None).count()
                if marks_count_total:
                    item.marks_counts = '{} / {} ({:.0f}%)'.format(marks_count_passing, marks_count_total, 100.0 * marks_count_passing / marks_count_total)
                else:
                    item.marks_counts = None

    if extra_info == 'averages':
        for item in items:
            # listify the QuerySet now so we can modify it and use it in the template
            # if the template just reads the DB and instantiates new objects, they will not have our class_average attribute
            item.demonstration_list = list(item.demonstration_set.all())
            for demonstration in item.demonstration_list:
                # TODO: make sure we only count enrolled students
                demonstration.class_average = demonstration.mark_set.aggregate(Avg('mark'))['mark__avg']
                try:
                    demonstration.class_average = Decimal(demonstration.class_average).quantize(quantizer)
                except TypeError: # e.g. Decimal(None)
                    pass
            item.class_average = item.mark_set.aggregate(Avg('mark'))['mark__avg']
            try:
                item.class_average = Decimal(item.class_average).quantize(quantizer)
            except TypeError: # e.g. Decimal(None)
                pass

    # Gather visual flagging criteria
    absolute_category_flag_criteria = {}
    normalized_category_flag_criteria = {}
    for category in Category.objects.filter(item__in=items).distinct():
        if category.fixed_points_possible:
            # assume the criterion is absolute if the category has fixed # of points possible
            use_dict = absolute_category_flag_criteria
        else:
            # assume we need to divide the mark by points possible before comparing to criterion
            use_dict = normalized_category_flag_criteria
        use_dict[category.pk] = []
        substitutions = calculation_rule.substitution_set.filter(apply_to_departments=course_section.department, apply_to_categories=category, flag_visually=True)
        for substitution in substitutions:
            use_dict[category.pk].append(substitution.operator + ' ' + str(substitution.match_value))

    # calculate course-section-wide averages and counts
    if totals['course_section_average_count']:
        totals['course_section_average'] = Decimal(totals['course_section_average'] / totals['course_section_average_count']).quantize(quantizer)
    else:
        totals['course_section_average'] = None
    if totals['filtered_average_count']:
        totals['filtered_average'] = Decimal(totals['filtered_average'] / totals['filtered_average_count']).quantize(quantizer)
    else:
        totals['filtered_average'] = None
    if totals['standards_all']:
        totals['standards_text'] = '{} / {} ({:.0f}%)'.format(totals['standards_passing'], totals['standards_all'],
            100.0 * totals['standards_passing'] / totals['standards_all'])
    else:
        totals['standards_text'] = None
    if totals['filtered_standards_all']:
        totals['filtered_standards_text'] = '{} / {} ({:.0f}%)'.format(totals['filtered_standards_passing'], totals['filtered_standards_all'],
            100.0 * totals['filtered_standards_passing'] / totals['filtered_standards_all'])
    else:
        totals['filtered_standards_text'] = None

    data_dictionary = {
        'items': items,
        'item_pks': ','.join(map(str,items.values_list('pk', flat=True))),
        'pending_aggregate_pks': json.dumps(map(str, pending_aggregate_pks)),
        'students': students,
        'course_section': course_section,
        'teacher_course_sections': teacher_course_sections,
        'filtered' : filtered,
        'filter_form': filter_form,
        'absolute_category_flag_criteria': absolute_category_flag_criteria,
        'normalized_category_flag_criteria': normalized_category_flag_criteria,
        'extra_info': extra_info,
        'totals': totals,
        'item_form_exclude': ItemForm().get_user_excludes(),
    }
    if for_export:
        return data_dictionary
    else:
        return render_to_response('benchmark_grade/gradebook.html', data_dictionary,
            RequestContext(request, {}),)

@staff_member_required
@transaction.commit_on_success
def ajax_delete_item_form(request, course_section_id, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if not request.user.has_perm('grades.delete_grade') and not item.marking_period.active:
        # you aren't a registrar, so you can't modify an inactive marking period
        return HttpResponse(status=403)
    ghost_item = Item()
    ghost_item.course_section = item.course_section
    ghost_item.category = item.category
    ghost_item.marking_period = item.marking_period
    message = '%s deleted' % (item,)
    item.delete()
    gradebook_recalculate_on_item_change(ghost_item)
    messages.success(request, message)
    return HttpResponse('SUCCESS')

@staff_member_required
@transaction.commit_on_success
def ajax_get_item_form(request, course_section_id, item_id=None):
    ''' the transaction decorator helps, but people can still hammer the submit button
    and create tons of assignments. for some reason, only one shows up right away, and the rest
    don't appear until reload '''
    course_section = get_object_or_404(CourseSection, pk=course_section_id)
    item = None
    lists = None
    
    if request.POST:
        if item_id:
            # modifying an existing item
            item = get_object_or_404(Item, pk=item_id)
            form = ItemForm(request.POST, instance=item, prefix="item")
            if not request.user.has_perm('grades.change_grade') and not item.marking_period.active:
                # you aren't a registrar, so you can't modify an item from an inactive marking period
                form.fields['marking_period'].validators.append(
                    make_validationerror_raiser('This item belongs to the inactive marking period {}.'.format(item.marking_period))
                )
            if item.course_section_id != long(form.data['item-course_section']):
                # don't support moving items between course sections
                form.fields['course_section'].validators.append(
                    make_validationerror_raiser('Please click "Make a Copy" if you would like to add this item to another course section.')
                )
            try:
                new_category = Category.objects.get(pk=long(form.data['item-category']))
                if item.category.allow_multiple_demonstrations != new_category.allow_multiple_demonstrations and \
                    item.demonstration_set.count() > 1:
                    form.fields['category'].validators.append(
                        make_validationerror_raiser(
                            'You must remove all but one demonstration before '
                            'changing to a category that does not allow multiple demonstrations.'
                        )
                    )
            except Category.DoesNotExist:
                pass # invalid form data, will be handled by standard Django
        else:
            # creating a new item
            form = ItemForm(request.POST, prefix="item")
            if not request.user.has_perm('grades.add_grade'): # registrars should have this, as opposed to change_own_grade
                # restrict regular teachers to the active marking period
                try:
                    form.fields['marking_period'].validators.append(require_active_marking_period)
                except KeyError:
                    pass # field was disabled by user configuration
        if form.is_valid():
            with reversion.create_revision():
                if item_id is None:
                    # a new item!
                    item = form.save()
                    dem = None
                    if item.category.allow_multiple_demonstrations:
                        # must have at least one demonstration; create a new one
                        dem = Demonstration()
                        dem.name = 'Dem. 1'
                        dem.item = item
                        dem.save()
                    # must create blank marks for each student
                    for student in Student.objects.filter(coursesection=course_section):
                        mark, created = Mark.objects.get_or_create(item=item, student=student, demonstration=dem)
                else:
                    # modifying an existing item
                    old_item = Item.objects.get(pk=item.pk)
                    item = form.save()
                    # Deal with changes between Categories that support multiple
                    # Demonstrations and those that don't
                    if old_item.category.allow_multiple_demonstrations != item.category.allow_multiple_demonstrations:
                        if item.category.allow_multiple_demonstrations:
                            # Previous category didn't allow demonstrations; this one does
                            if item.demonstration_set.exists():
                                raise Exception('Item {} should not have any Demonstrations yet.'.format(item.pk))
                            dem = Demonstration()
                            dem.name = 'Dem.1'
                            dem.item = item
                            dem.save()
                            item.mark_set.update(demonstration=dem)
                        else:
                            # This category does not allow demonstrations, but the previous one did
                            if item.demonstration_set.count() != 1:
                                raise Exception('Item {} should have exactly one Demonstration.'.format(item.pk))
                            # Remove cached multi-demonstration aggregate Marks
                            item.mark_set.filter(demonstration=None).delete()
                            dem = item.demonstration_set.first()
                            item.mark_set.filter(demonstration=dem).update(demonstration=None)
                            dem.delete()
                    # Recalculate lots of stuff!
                    gradebook_recalculate_on_item_change(item, old_item=old_item)
                reversion.set_user(request.user)
                reversion.set_comment("gradebook")

            # Should I use the django message framework to inform the user?
            # This would not work in ajax unless we make some sort of ajax
            # message handler.
            messages.success(request, '%s saved' % (item,))
            return HttpResponse('SUCCESS')
        
    else:
        if item_id:
            item = get_object_or_404(Item, pk=item_id)
            form = ItemForm(instance=item, prefix="item")
            # TODO: remove TC hard-coding
            try:
                Category.objects.get(name='Standards') # are we in TC land?
                if item.category.name == 'Standards':
                    students_missing = Student.objects.filter(mark__item=item).annotate(best_mark=Max('mark__mark')).filter(best_mark__lt=3)
                    if not students_missing: students_missing = ('None',)
                    lists = ({'heading':'Students Missing This Item', 'items':students_missing},)
            except Category.DoesNotExist:
                pass_letters = Configuration.get_or_default("Letter Passing Grade").value.split(',')
                pass_number = float(Configuration.get_or_default("Passing Grade").value) / 100 # yay, assumptions
                students_missing = Student.objects.filter(mark__item=item).annotate(best_mark=Max('mark__normalized_mark')).filter(best_mark__lt=pass_number)
                text_missing = []
                for student in students_missing:
                    if item.mark_set.get(student=student).letter_grade in pass_letters:
                        continue
                    text_missing.append(u'{} / {} ({:.0f}%) {}'.format(
                        student.best_mark * float(item.points_possible), item.points_possible, student.best_mark * 100, unicode(student)))
                lists = ({'heading':'Students Missing This Item', 'items':text_missing},)
        else:
            active_mps = course_section.marking_period.filter(active=True)
            if active_mps:
                form = ItemForm(initial={'course_section': course_section, 'marking_period':active_mps[0]}, prefix="item")
            else:
                form = ItemForm(initial={'course_section': course_section}, prefix="item")
    
    # some fields may have been disabled by user configuration
    try: form.fields['marking_period'].queryset = course_section.marking_period.all()
    except KeyError: pass
    try: form.fields['category'].queryset = Category.objects.filter(display_in_gradebook=True)
    except KeyError: pass
    try: form.fields['benchmark'].queryset = Benchmark.objects.filter()
    except KeyError: pass
    available_course_sections = get_teacher_course_sections(request.user.username)
    if request.user.has_perm('grades.change_grade'):
        available_course_sections = CourseSection.objects.all()
    try: form.fields['course_section'].queryset = available_course_sections
    except KeyError: pass
    try:
        form.fields['category'].widget.attrs = {
            'onchange': "Dajaxice.ecwsp.benchmark_grade.check_fixed_points_possible(Dajax.process, {'category':this.value})"}
        if item and item.category.fixed_points_possible:
            form.fields['points_possible'].widget.attrs = {'disabled': 'true'}
    except KeyError:
        pass

    return render_to_response('sis/gumby_modal_form.html', {
        'my_form': form,
        'item_id': item_id,
        'lists': lists,
    }, RequestContext(request, {}),)

@staff_member_required
def ajax_get_item_tooltip(request, course_section_id, item_id):
    course_section = get_object_or_404(CourseSection, pk=course_section_id)
    item = get_object_or_404(Item, pk=item_id)
    attribute_names = (
        'name',
        'description',
        'date',
        'marking_period',
        'category',
        'points_possible',
        'assignment_type',
        'benchmark',
    )
    verbose_name_overrides = {
        'benchmark': 'standard',
    }
    details = {}
    for a in attribute_names:
        if a in ItemForm().get_user_excludes():
            continue
        if a in verbose_name_overrides:
            verbose_name = verbose_name_overrides[a]
        else:
            verbose_name = item._meta.get_field(a).verbose_name
        value = getattr(item, a)
        details[verbose_name] = value
    return render_to_response('benchmark_grade/item_details.html', {
        'details': details,
    }, RequestContext(request, {}),)

@staff_member_required
@transaction.commit_on_success
def ajax_delete_demonstration_form(request, course_section_id, demonstration_id):
    demonstration = get_object_or_404(Demonstration, pk=demonstration_id)
    item = demonstration.item
    if not request.user.has_perm('grades.delete_grade') and not item.marking_period.active:
        # you aren't a registrar, so you can't modify an inactive marking period
        return HttpResponse(status=403)
    ghost_item = Item()
    ghost_item.course_section = item.course_section
    ghost_item.category = item.category
    ghost_item.marking_period = item.marking_period
    message = '%s deleted' % (demonstration,)
    demonstration.delete()
    # TODO: degrossify
    if not Demonstration.objects.filter(item=item):
        if Mark.objects.filter(item=item):
            raise Exception('Stray marks found after attempting to delete last demonstration.')
        else:
            # the last demonstration is dead. kill the item.
            item.delete()

    gradebook_recalculate_on_item_change(ghost_item)
    messages.success(request, message)
    return HttpResponse('SUCCESS')

@staff_member_required
@transaction.commit_on_success
def ajax_get_demonstration_form(request, course_section_id, demonstration_id=None):
    ''' the transaction decorator helps, but people can still hammer the submit button
    and create tons of assignments. for some reason, only one shows up right away, and the rest
    don't appear until reload '''
    course_section = get_object_or_404(CourseSection, pk=course_section_id)
    lists = None
    
    if request.POST:
        if demonstration_id:
            # modifying an existing demonstration
            demonstration = get_object_or_404(Demonstration, pk=demonstration_id)
            old_demonstration = get_object_or_404(Demonstration, pk=demonstration_id)
            form = DemonstrationForm(request.POST, instance=demonstration, prefix="demonstration")
            if not request.user.has_perm('grades.change_grade') and not demonstration.item.marking_period.active:
                # you aren't a registrar, so you can't modify a demonstration from an inactive marking period
                form.fields['item'].validators.append(
                    make_validationerror_raiser('This demonstration belongs to the inactive marking period {}.'.format(demonstration.item.marking_period))
                )
        else:
            # creating a new demonstration
            form = DemonstrationForm(request.POST, prefix="demonstration")
            if not request.user.has_perm('grades.add_grade'):
                # you aren't a registrar, so make sure you can only select items in active marking periods
                form.fields['item'].validators.append(require_item_in_active_marking_period)
        if form.is_valid():
            demonstration = form.save()
            if demonstration_id is None:
                # a new demonstration; must create blank marks for each student
                for student in Student.objects.filter(coursesection=course_section):
                    mark, created = Mark.objects.get_or_create(item=demonstration.item, demonstration=demonstration, student=student)
            else:
                # do we belong to a different Item?
                if old_demonstration.item_id != demonstration.item_id:
                    # update all our Marks to reference the new Item
                    for mark in Mark.objects.filter(demonstration=demonstration):
                        mark.item = demonstration.item
                        mark.save()
                    # recalculate both Items
                    gradebook_recalculate_on_item_change(demonstration.item, old_item=old_demonstration.item)
                    # is the old Item totally abandoned now?
                    if not old_demonstration.item.demonstration_set.count():
                        if old_demonstration.item.mark_set.count():
                            raise Exception('Stray Marks found after attempting to reassign last Demonstration.')
                        else:
                            # no Demonstrations are left. kill the Item.
                            old_demonstration.item.delete()

            # Should I use the django message framework to inform the user?
            # This would not work in ajax unless we make some sort of ajax
            # message handler.
            messages.success(request, '%s saved' % (demonstration,))
            return HttpResponse('SUCCESS')
        
    else:
        if demonstration_id:
            demonstration = get_object_or_404(Demonstration, pk=demonstration_id)
            form = DemonstrationForm(instance=demonstration, prefix="demonstration")
            # TODO: remove TC hard-coding
            if demonstration.item.category.name == 'Standards':
                students_missing = Student.objects.filter(mark__demonstration=demonstration, mark__mark__lt=3)
                if not students_missing: students_missing = ('None',)
                lists = ({'heading':'Students Missing This Demonstration', 'items':students_missing},)
        else:
            form = DemonstrationForm(initial={'course_section': course_section}, prefix="demonstration")
    
    form.fields['item'].queryset = Item.objects.filter(course_section=course_section,
                                                       category__display_in_gradebook=True, category__allow_multiple_demonstrations=True)

    return render_to_response('benchmark_grade/demonstration_form_fragment.html', {
        'form': form,
        'demonstration_id': demonstration_id,
        'lists': lists,
    }, RequestContext(request, {}),)

@staff_member_required
def ajax_get_student_info(request, course_section_id, student_id):
    student = get_object_or_404(Student, pk=student_id)
    course_section = get_object_or_404(CourseSection, pk=course_section_id)

    # TODO: remove TC hard-coding
    try:
        Category.objects.get(name='Standards') # are we in TC land?
        standards_missing = Item.objects.filter(course_section=course_section, category__name='Standards', mark__student=student).annotate(best_mark=Max('mark__mark')).filter(best_mark__lt=3)
        if not standards_missing: standards_missing = ('None',)
        lists = ({'heading':'Standards Missing for {}'.format(student), 'items':standards_missing},)
    except Category.DoesNotExist:
        pass_letters = Configuration.get_or_default("Letter Passing Grade").value.split(',')
        pass_number = float(Configuration.get_or_default("Passing Grade").value) / 100 # yay, assumptions
        items_missing = Item.objects.filter(course_section=course_section, mark__student=student).annotate(best_mark=Max('mark__normalized_mark')).filter(
            best_mark__lt=pass_number)
        text_missing = []
        for item in items_missing:
            if item.mark_set.get(student=student).letter_grade in pass_letters:
                continue
            text_missing.append(u'{} / {} ({:.0f}%) {}'.format(
                item.best_mark * float(item.points_possible), item.points_possible, item.best_mark * 100, unicode(item)))
        lists = ({'heading':'Items Missing for {}'.format(student), 'items':text_missing},)
    afterword = '<a onclick="open_grade_detail({}, {})">Create report from current view of gradebook (in new tab)</a>'
    afterword = afterword.format(course_section_id, student_id)

    return render_to_response('sis/generic_list_fragment.html', {
        'lists': lists,
        'afterword': afterword,
    }, RequestContext(request, {}),)

@staff_member_required
def ajax_get_fill_all_form(request, course_section_id, object_type, object_id):
    model_base = Item if object_type == 'item' else Demonstration
    item_or_demonstration = get_object_or_404(model_base, pk=object_id)
    course_section = get_object_or_404(CourseSection, pk=course_section_id)
    if type(item_or_demonstration) == Item and item_or_demonstration.course_section != course_section:
        raise Exception('This Item does not belong to the specified CourseSection.')
    if type(item_or_demonstration) == Demonstration and item_or_demonstration.item.course_section != course_section:
        raise Exception('This Demonstration does not belong to the specified CourseSection.')
    if type(item_or_demonstration) == Item and item_or_demonstration.category.allow_multiple_demonstrations:
        raise Exception('Marks must be assigned to Demonstrations for this Item, not directly to the Item.')
    if not item_or_demonstration.mark_set.count:
        raise Exception('This {} has no Marks.'.format(item_or_demonstration._meta.object_name))

    if request.POST:
        # we must pass in an instance, otherwise we fail unique validation 
        instance = item_or_demonstration.mark_set.all()[0]
        form = FillAllForm(request.POST, instance=instance, prefix="fill_all")
        try:
            marking_period = item_or_demonstration.marking_period
        except AttributeError:
            marking_period = item_or_demonstration.item.marking_period
        if not request.user.has_perm('grades.change_grade') and marking_period is not None and not marking_period.active:
                # you aren't a registrar, so you can't modify an item from an inactive marking period
                form.fields['mark'].validators.append(
                    make_validationerror_raiser('This {} belongs to the inactive marking period {}.'.format(object_type, marking_period))
                )
        if form.is_valid():
            for m in item_or_demonstration.mark_set.all():
                m.set_grade(form.cleaned_data['mark'])
                with reversion.create_revision():
                    m.save()
                    reversion.set_user(request.user)
                    reversion.set_comment("gradebook fill all")
                # really expensive!
                gradebook_recalculate_on_mark_change(m)
            messages.success(request, 'Marked all students {} for {}'.format(form.cleaned_data['mark'], item_or_demonstration))
            # the client will reload the whole page, so there's no need to pass a list of affected aggregate pks
            return HttpResponse('SUCCESS')
    else:
        form = FillAllForm(instance=item_or_demonstration.mark_set.all()[0], prefix="fill_all")
    return render_to_response('benchmark_grade/fill_all_form_fragment.html', {
        'action': request.path,
        'form': form,
        'subtitle': unicode(item_or_demonstration),
    }, RequestContext(request, {}),)

@staff_member_required
def ajax_save_grade(request):
    if 'mark_id' in request.POST and 'value' in request.POST:
        mark_id = request.POST['mark_id'].strip()
        value = request.POST['value'].strip()
        try: mark = Mark.objects.get(id=mark_id)
        except Mark.DoesNotExist: return HttpResponse('NO MARK WITH ID ' + mark_id, status=404) 
        if not request.user.is_superuser and not request.user.groups.filter(name='registrar').count() \
            and not mark.item.course_section.teachers.filter(username=request.user.username).exists():
            return HttpResponse(status=403)

        if not request.user.has_perm('grades.change_grade') \
            and mark.item.marking_period is not None \
            and not mark.item.marking_period.active:
            # you aren't a registrar, so you can't modify an item from an inactive marking period
            return HttpResponse(status=403)

        if len(value) and value.lower != 'none':
            mark.set_grade(value)
        else:
            mark.set_grade(None)
            value = 'None'
        try:
            with reversion.create_revision():
                mark.full_clean()
                mark.save()
                reversion.set_user(request.user)
                reversion.set_comment("gradebook")
        except Exception as e:
            return HttpResponse(e, status=400)
        try:
            affected_agg_pks = [x.pk for x in gradebook_recalculate_on_mark_change(mark)]
        except:
            # BAD BAD BAD... stale Aggregates ahead!
            logging.error("Mark {} saved successfully but Aggregate calculation failed".format(mark.pk), exc_info=True)
            affected_agg_pks = None
        # just the whole course section average for now
        # TODO: update filtered average
        #average = gradebook_get_average(mark.student, mark.item.course, None, None, None) 
        return HttpResponse(json.dumps({'success': 'SUCCESS', 'value': value, 'average': 'Please clear your browser\'s cache.', 'affected_aggregates': affected_agg_pks}))
    else:
        return HttpResponse('POST DATA INCOMPLETE', status=400) 

@staff_member_required
def ajax_task_poll(request, course_section_pk=None):
    if 'aggregate_pks' not in request.POST:
        # no aggregates specified; just return the number of active tasks for this course section
        course_section = get_object_or_404(CourseSection, pk=course_section_pk)
        count = AggregateTask.objects.values('task_id').distinct().count()
        return HttpResponse(json.dumps({'outstanding_tasks': count}))
    agg_pks = request.POST.getlist('aggregate_pks')
    aggs = Aggregate.objects.filter(pk__in=agg_pks)
    count = AggregateTask.objects.filter(aggregate__in=aggs).values('task_id').distinct().count()
    if count:
        # thank you, come again
        return HttpResponse(json.dumps({'outstanding_tasks': count}), status=202)
    else:
        # no outstanding tasks! return actual values!
        results = {}
        for agg in aggs:
            if agg.cached_substitution is not None:
                results[agg.pk] = str(agg.cached_substitution)
            else:
                results[agg.pk] = str(agg.cached_value)
        return HttpResponse(json.dumps({'results': results}))

@login_required
def student_report(request, student_pk=None, course_section_pk=None, marking_period_pk=None):
    authorized = False
    family_available_students = None
    try:
        # is it a student?
        student = Student.objects.get(username=request.user.username)
        # ok! we'll ignore student_pk, and the student is authorized to see itself
        authorized = True
    except:
        student = None
    if not student:
        if request.user.is_staff:
            # hey, it's a staff member!
            student = get_object_or_404(Student, pk=student_pk)
            authorized = True
        else:
            # maybe it's a family member?
            family_available_students = Student.objects.filter(family_access_users=request.user)
            if student_pk:
                student = get_object_or_404(Student, pk=student_pk)
                if student in family_available_students:
                    authorized = True
            elif family_available_students.count():
                student = family_available_students[0]
                authorized = True
    
    # did all that make us comfortable with proceeding?
    if not authorized:
        error_message = 'Sorry, you are not authorized to see grades for this student. Please contact the school registrar.'
        return render_to_response('benchmark_grade/student_grade.html', {
            'error_message': error_message,
        }, RequestContext(request, {}),)

    # is this a summary or detail report?
    if not course_section_pk:
        # summary report for all course sections
        PASSING_GRADE = 3 # TODO: pull config value. Roche has it set to something crazy now and I don't want to deal with it
        school_year = SchoolYear.objects.get(active_year=True)
        calculation_rule = benchmark_find_calculation_rule(school_year)
        all_mps = MarkingPeriod.objects.filter(school_year=school_year, start_date__lte=datetime.date.today()).order_by('-start_date')
        if marking_period_pk is None:
            if all_mps.count():
                mps = (all_mps[0],)
            else:
                mps = ()
        else:
            mps = all_mps.filter(pk=marking_period_pk)
        mp_pks = [x.pk for x in mps]
        other_mps = all_mps.exclude(pk__in=mp_pks)
        for mp in mps:
            mp.course_sections = CourseSection.objects.filter(courseenrollment__user=student, course__graded=True, marking_period=mp).order_by('name')
            for course_section in mp.course_sections:
                course_section.categories = Category.objects.filter(item__course_section=course_section, item__mark__student=student).distinct()
                course_section.category_by_name = {}
                for category in course_section.categories:
                    try:
                        category.percentage = calculation_rule.per_course_category_set.get(
                            category=category, apply_to_departments=course_section.department).weight * 100
                        category.percentage = category.percentage.quantize(Decimal('0'))
                    except CalculationRulePerCourseCategory.DoesNotExist:
                        # sometimes a course section has items belonging to categories that don't count in the course section average
                        # but we want to display them anyway
                        category.percentage = 0
                    category.average = gradebook_get_average(student, course_section, category, mp, None)
                    items = Item.objects.filter(course_section=course_section, category=category, marking_period=mp, mark__student=student).annotate(best_mark=Max('mark__mark'))
                    counts = {}
                    counts['total'] = items.exclude(best_mark=None).distinct().count()
                    counts['missing'] = items.filter(best_mark__lt=PASSING_GRADE).distinct().count()
                    counts['passing'] = items.filter(best_mark__gte=PASSING_GRADE).distinct().count()
                    if counts['total']:
                        counts['percentage'] = (Decimal(counts['passing']) / counts['total'] * 100).quantize(Decimal('0'))
                    course_section.category_by_name[category.name] = counts
                course_section.average = gradebook_get_average(student, course_section, None, mp, None)
                try:
                    course_section.legacy_grade = course_section.grade_set.get(student=student, marking_period=mp).get_grade()
                    if course_section.legacy_grade == '':
                        course_section.legacy_grade = None # be consistent
                except Grade.DoesNotExist:
                    course_section.legacy_grade = None

        return render_to_response('benchmark_grade/student_grade.html', {
            'student': student,
            'available_students': family_available_students,
            'mps': mps,
            'other_mps': other_mps
        }, RequestContext(request, {}),)

    else:
        # detail report for a single course section
        course_section = get_object_or_404(CourseSection, pk=course_section_pk)

        # be careful of empty string in POST, as int('') raises ValueError
        if 'item_pks' in request.POST and len(request.POST['item_pks']):
            item_pks = request.POST['item_pks'].split(',')
            items = Item.objects.filter(pk__in=item_pks)
            specific_items = True
        else:
            items = Item.objects
            specific_items = False
        # always filter in case a bad person passes us items from a different course section
        items = items.filter(course_section=course_section, mark__student=student)

        all_mps = MarkingPeriod.objects.filter(item__in=items).distinct().order_by('-start_date')
        if specific_items:
            mps = all_mps
            other_mps = ()
        else:
            if marking_period_pk is None:
                if all_mps.count():
                    mps = (all_mps[0],)
                else:
                    mps = ()
            else:
                mps = all_mps.filter(pk=marking_period_pk)
            mp_pks = [x.pk for x in mps]
            other_mps = all_mps.exclude(pk__in=mp_pks)

        #if marking_period_pk:
        #    mp = get_object_or_404(MarkingPeriod, pk=marking_period_pk)
        #    mps = (mp,)
        #else:
        #    mps = MarkingPeriod.objects.filter(item__in=items).distinct().order_by('-start_date')

        for mp in mps:
            calculation_rule = benchmark_find_calculation_rule(mp.school_year)
            mp_items = items.filter(marking_period=mp)
            mp.categories = Category.objects.filter(item__in=mp_items).distinct()
            for category in mp.categories:
                category_items = mp_items.filter(category=category).annotate(best_mark=Max('mark__mark')).exclude(best_mark=None)
                item_names = category_items.values_list('name').distinct()
                category.item_groups = {}
                for item_name_tuple in item_names:
                    item_name = item_name_tuple[0]
                    category.item_groups[item_name] = category_items.filter(name=item_name).distinct() 
                if specific_items:
                    # get a disposable average for these specific items
                    category.average = gradebook_get_average(student, course_section, category, mp, category_items)
                else:
                    category.average = gradebook_get_average(student, course_section, category, mp, None)
                category.flagged_item_pks = []
                for substitution in calculation_rule.substitution_set.filter(
                        apply_to_categories=category
                ):
                    category.flagged_item_pks.extend(category_items.filter(
                        **substitution.as_filter('best_mark')
                    ).values_list('pk', flat=True))

        return render_to_response('benchmark_grade/student_grade_course_detail.html', {
            'student': student,
            'available_students': family_available_students,
            'course_section': course_section,
            'mps': mps,
            'other_mps': other_mps
        }, RequestContext(request, {}),)

@staff_member_required
def comments(request, course_section_id):
    course_section = get_object_or_404(CourseSection, pk=course_section_id)
    school_year = course_section.marking_period.all()[0].school_year
    teacher_course_sections = get_teacher_course_sections(request.user.username)
    if not request.user.is_superuser and not request.user.groups.filter(name='registrar').count() and \
    (teacher_course_sections is None or course_section not in teacher_course_sections):
        messages.add_message(request, messages.ERROR,
            'You do not have access to the gradebook for ' + course_section.name + '.')
        return HttpResponseRedirect(reverse('admin:index'))

    # lots of stuff will fail unceremoniously if there are no MPs assigned
    if not course_section.marking_period.count():
        messages.add_message(request, messages.ERROR,
            'The gradebook cannot be opened because there are no marking periods assigned to the course section ' +
            course_section.name + '.')
        return HttpResponseRedirect(reverse('admin:index'))

    marking_periods = list(course_section.marking_period.order_by('start_date'))
    for marking_period in reversed(marking_periods):
        if marking_period.active:
            marking_period.current = True
            break
    else:
        marking_periods[0].current = True

    for marking_period in marking_periods:
        marking_period.students = Student.objects.filter(courseenrollment__course_section=course_section)
        for student in marking_period.students:
            try:
                grade = Grade.objects.get(student=student, course_section=course_section, marking_period=marking_period)
                student.marking_period_average_pk = grade.pk
                student.marking_period_average = Grade.objects.get(student=student, course_section=course_section, marking_period=marking_period)
                student.comment = grade.comment
            except Grade.DoesNotExist:
                student.marking_period_average = None
                student.comment = None

    return render_to_response('benchmark_grade/comments.html', {
        'course_section' : course_section,
        'marking_periods': marking_periods,
        'max_length': Configuration.get_or_default('Grade comment length limit').value,
    }, RequestContext(request, {}),)
