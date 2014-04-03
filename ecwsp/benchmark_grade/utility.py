#   Copyright 2012 Burke Software and Consulting LLC
#   Author: John Milner <john@tmoj.net>
#   
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#     
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#      
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

from ecwsp.benchmark_grade.models import CalculationRule, Aggregate, Item, Mark, Category, AggregateTask, CalculationRulePerCourseCategory
from ecwsp.benchmark_grade.models import benchmark_get_or_flush, benchmark_get_create_or_flush
from ecwsp.schedule.models import MarkingPeriod, Department, Course
from ecwsp.benchmark_grade.tasks import benchmark_aggregate_task
from django.db.models import Avg, Sum, Min, Max
import logging
from decimal import Decimal, ROUND_HALF_UP
import celery.utils

def benchmark_find_calculation_rule(school_year):
    rules = CalculationRule.objects.filter(first_year_effective=school_year)
    if rules:
        # We have a rule explicitly matching this marking period's school year
        rule = rules[0]
    else:
        # No explicit match, so find the most recent rule that went into effect *before* this marking period's school year
        rules = CalculationRule.objects.filter(first_year_effective__start_date__lt=school_year.start_date).order_by('-first_year_effective__start_date')
        if rules:
            rule = rules[0]
        elif CalculationRule.objects.count() == 0 and Category.objects.count() <= 1:
            # The school hasn't configured anything; cut them some slack
            rule = CalculationRule.objects.get_or_create(first_year_effective = school_year)[0]
            if Category.objects.count() == 1:
                category = Category.objects.all()[0]
            else:
                category = Category.objects.get_or_create(name="Everything")[0]
            per_course_category = CalculationRulePerCourseCategory.objects.get_or_create(calculation_rule=rule, category=category)[0]
            per_course_category.apply_to_departments.add(*Department.objects.all())
        else:
            # The school has touched the configuration; don't guess at what they want
            raise Exception('There is no suitable calculation rule for the school year {}.'.format(school_year))
    return rule

def benchmark_calculate_category_as_course_aggregate(student, category, marking_period):
    agg, created = benchmark_get_create_or_flush(student.aggregate_set, course=None, category=category, marking_period=marking_period)
    agg.name = 'G! {} - {} (All Courses, {})'.format(student, category, marking_period)
    agg.cached_substitution = None
    calculation_rule = benchmark_find_calculation_rule(marking_period.school_year)
    category_as_course = calculation_rule.category_as_course_set.get(category=category)
    category_numer = category_denom = Decimal(0)
    for course in Course.objects.filter(courseenrollment__user__username=student.username, marking_period=marking_period, department__in=category_as_course.include_departments.all()).distinct():
        credits = Decimal(course.credits) / course.marking_period.count()
        try:
            category_aggregate = benchmark_get_or_flush(Aggregate, student=student, marking_period=marking_period, category=category, course=course)
        except Aggregate.DoesNotExist:
            category_aggregate = benchmark_calculate_course_category_aggregate(student, course, category, marking_period)[0]
        if category_aggregate is not None and category_aggregate.cached_value is not None:
            calculate_as, display_as = calculation_rule.substitute(category_aggregate, category_aggregate.cached_value)
            category_numer += credits * calculate_as
            category_denom += credits
            # yes, agg will just end up with the last substitution, but tough
            if display_as is not None and len(display_as):
                agg.cached_substitution = display_as
    if category_denom:
        agg.cached_value = category_numer / category_denom
    else:
        agg.cached_value = None
    agg.save()
    return agg, created

def benchmark_calculate_course_category_aggregate(student, course, category, marking_period, items=None):
    if items is None:
        items = Item.objects.all()
        save = True
    else:
        # don't store aggregates for every one-off combination of items
        save = False
    items = items.filter(course=course, category=category)
    # if we're passed marking_period=None, we should consider items across the entire duration of the course
    # if we're passed a specific marking period instead, we should consider items matching only that marking period
    if marking_period is not None:
        items = items.filter(marking_period=marking_period)

    calculation_rule = benchmark_find_calculation_rule(course.marking_period.all()[0].school_year)

    # initialize attributes
    criteria = {'course': course, 'category': category, 'marking_period': marking_period}
    # silly name is silly, and should not be part of the criteria
    silly_name = 'G! {} - {} ({}, {})'.format(student, category, course, marking_period)
    # don't use get_or_create; otherwise we may end up saving an empty object
    try:
        agg = benchmark_get_or_flush(student.aggregate_set, **criteria)
        created = False
    except Aggregate.DoesNotExist:
        agg = Aggregate(student=student, **criteria)
        created = True
    agg.name = silly_name

    # begin the actual calculations!
    agg.cached_substitution = None
    category_numer = category_denom = Decimal(0)
    if category.allow_multiple_demonstrations:
        for category_item in items.exclude(points_possible=None):
            # Find the highest mark amongst demonstrations and count it as the grade for the item
            best = Mark.objects.filter(student=student, item=category_item).aggregate(Max('mark'))['mark__max']
            if best is not None:
                calculate_as, display_as = calculation_rule.substitute(category_item, best)
                category_numer += calculate_as
                category_denom += category_item.points_possible
                # yes, agg will just end up with the last substitution, but tough
                if display_as is not None:
                    agg.cached_substitution = display_as

    else:
        for category_mark in Mark.objects.filter(student=student, item__in=items).exclude(mark=None).exclude(item__points_possible=None):
            calculate_as, display_as = calculation_rule.substitute(category_mark.item, category_mark.mark)
            category_numer += calculate_as
            category_denom += category_mark.item.points_possible
            if display_as is not None:
                agg.cached_substitution = display_as
    if category_denom:
        agg.cached_value = category_numer / category_denom * agg._fallback_points_possible()
    else:
        agg.cached_value = None
    if save:
        agg.save()
    return agg, created

def benchmark_calculate_course_aggregate(student, course, marking_period, items=None, recalculate_all_categories=False):
    # doesn't recalculate component aggregates by default
    if items is None:
        # QUICK HACK to use new Aggregate calculation method
        # TODO: Subclass Aggregate and override mark_set for one-off sets of Items
        agg, created = benchmark_get_create_or_flush(Aggregate, student=student, course=course, marking_period=marking_period, category=None)
        agg.calculate(recalculate_all_categories)
        return agg, created
        # /HACK (haha, right.)

        # just leave items alone--we don't actually consider it here; we only pass it to benchmark_calculate_course_category_aggregate
        # setting items here will prevent benchmark_calculate_course_category_aggregate from saving anything
        save = True
        items_categories = ()
    else:
        # don't store aggregates for every one-off combination of items
        save = False
        # we'll have to miss cache and recaculate any category to which an item belongs
        items_categories = Category.objects.filter(item__in=items).distinct()

    calculation_rule = benchmark_find_calculation_rule(course.marking_period.all()[0].school_year)

    # initialize attributes
    criteria = {'course': course, 'category': None, 'marking_period': marking_period}
    # silly name is silly, and should not be part of the criteria
    silly_name = 'G! {} - Course Average ({}, {})'.format(student, course, marking_period)
    # don't use get_or_create; otherwise we may end up saving an empty object
    try:
        agg = benchmark_get_or_flush(student.aggregate_set, **criteria)
        created = False
    except Aggregate.DoesNotExist:
        agg = Aggregate(student=student, **criteria)
        created = True
    agg.name = silly_name

    # begin the actual calculations!
    agg.cached_substitution = None
    course_numer = course_denom = Decimal(0)
    for rule_category in calculation_rule.per_course_category_set.filter(apply_to_departments=course.department):
        criteria['category'] = rule_category.category
        cat_agg, cat_created = benchmark_get_create_or_flush(student.aggregate_set, **criteria)
        if cat_created or recalculate_all_categories or rule_category.category in items_categories:
            cat_agg, cat_created = benchmark_calculate_course_category_aggregate(student, course, rule_category.category, marking_period, items)
        if cat_agg.cached_value is not None:
            course_numer += rule_category.weight * cat_agg.cached_value
            course_denom += rule_category.weight
            # yes, agg will just end up with the last substitution, but tough
            if cat_agg.cached_substitution is not None:
                agg.cached_substitution = cat_agg.cached_substitution
    if course_denom:
        agg.cached_value = course_numer / course_denom
    else:
        agg.cached_value = None
    if save:
        agg.save()
    return agg, created


def gradebook_recalculate_on_item_change(item, students=None, old_item=None):
    '''
    If passed an item, recacluate everything affected by that item.
    If passed an item and students, recalculate everything affected by that item for those students.
    If passed and item and an old_item, figure out what changed and recalculate accordingly.

    Item model fields:
        name - does not affect calculations
        description - does not affect calculations
        course - DOES affect calculations but should not change
        date - does not affect calculations
        * marking_period - DOES affect calculations
        * category - DOES affect calculations
        * points_possible - DOES affect calcualations; all marks must be re-normalized!
        assignment_type - does not affect calculations
        benchmark - does not affect calculations
    '''
    categories = set((item.category,)) 
    marking_periods = set((item.marking_period,))
    renormalization_required = False
    parting_calculation_required = False
    if old_item:
        if old_item.course != item.course:
            raise Exception('Items must not move between courses.')
        # proceed only if the change affects calculations
        if old_item.points_possible != item.points_possible:
            renormalization_required = True
        if old_item.category != item.category:
            # necessary to recalculate the old category as well as the new
            parting_calculation_required = True
            categories.add(old_item.category)
        if old_item.marking_period != item.marking_period:
            # necessary to recalculate the old marking period as well as the new
            parting_calculation_required = True
            marking_periods.add(old_item.marking_period)

    calculation_rule = benchmark_find_calculation_rule(item.course.marking_period.all()[0].school_year)
    course = item.course
    if students is None:
        students = Student.objects.filter(courseenrollment__course=item.course)

    if renormalization_required:
        # take care of re-normalization before returning
        for mark in item.mark_set.all():
            mark.save()

    # do other calculations in the background
    funcs_and_args = []
    aggregates = [] # list of aggregates to be affected by background calculations

    for student in students:
        # recalculate the aggregate for the item's course, category, and marking period
        funcs_and_args.append((benchmark_calculate_course_category_aggregate, (student, course, item.category, item.marking_period)))
        aggregates += Aggregate.objects.filter(student=student, course=course, category=item.category, marking_period=item.marking_period)
        if parting_calculation_required:
            # the item was previously in another category or marking period, which now also must be recalculated
            funcs_and_args.append((benchmark_calculate_course_category_aggregate, (student, course, old_item.category, old_item.marking_period)))
            aggregates += Aggregate.objects.filter(student=student, course=course, category=old_item.category, marking_period=old_item.marking_period)
        # recalculate the course-long (i.e. marking_period=None) aggregate for each affected category
        for category in categories:
            funcs_and_args.append((benchmark_calculate_course_category_aggregate, (student, course, category, None)))
            aggregates += Aggregate.objects.filter(student=student, course=course, category=category, marking_period=None)

    affects_overall_course = 0 < calculation_rule.per_course_category_set.filter(category__in=categories, apply_to_departments=course.department).count()
    affected_categories_as_courses = calculation_rule.category_as_course_set.filter(category__in=categories, include_departments=course.department)
    for student in students:
        # recalculate aggregates for affected marking periods
        for marking_period in marking_periods:
            if affects_overall_course:
                funcs_and_args.append((benchmark_calculate_course_aggregate, (student, course, marking_period)))
                aggregates += Aggregate.objects.filter(student=student, course=course, marking_period=marking_period, category=None)
            for category_as_course in affected_categories_as_courses:
                funcs_and_args.append((benchmark_calculate_category_as_course_aggregate, (student, category_as_course.category, marking_period)))
                aggregates += Aggregate.objects.filter(student=student, category=category_as_course.category, marking_period=marking_period, course=None)
        # recalculate aggregates for the whole duration of the course (i.e. marking_period=None)
        if affects_overall_course:
            funcs_and_args.append((benchmark_calculate_course_aggregate, (student, course, None)))
            aggregates += Aggregate.objects.filter(student=student, course=course, marking_period=None, category=None)

    if len(funcs_and_args):
        # flag aggregates that are being recalculated
        task_id = celery.utils.uuid()
        for aggregate in aggregates:
            aggregate_task = AggregateTask(aggregate=aggregate, task_id=task_id)
            try:
                aggregate_task.save()
            except IntegrityError as e:
                logging.warning('We are calculating {} ({}) multiple times!'.format(aggregate, aggregate.pk), exc_info=True)
        # queue a task with our predetermined uuid
        task = benchmark_aggregate_task.apply_async((funcs_and_args,), task_id=task_id)
        return aggregates

def gradebook_recalculate_on_mark_change(mark):
    return gradebook_recalculate_on_item_change(mark.item, (mark.student, ))

def gradebook_get_average(*args, **kwargs):
    return gradebook_get_average_and_pk(*args, **kwargs)[0]

def gradebook_get_average_and_pk(student, course, category=None, marking_period=None, items=None, omit_substitutions=False):
    try:
        if items is not None: # averages of one-off sets of items aren't saved and must be calculated every time
            # this is rather silly, but it avoids code duplication or a teensy four-line function.
            raise Aggregate.DoesNotExist
        agg = benchmark_get_or_flush(student.aggregate_set, course=course, category=category, marking_period=marking_period)
    except Aggregate.DoesNotExist:
        if category is None:
            agg, created = benchmark_calculate_course_aggregate(student, course, marking_period, items)
        else:
            agg, created = benchmark_calculate_course_category_aggregate(student, course, category, marking_period, items)
    if not omit_substitutions and agg.cached_substitution is not None:
        return agg.cached_substitution, agg.pk
    elif agg.cached_value is not None:
        calculation_rule = benchmark_find_calculation_rule(course.marking_period.all()[0].school_year)
        if category is not None and category.display_scale is not None:
            pretty = agg.cached_value / agg._fallback_points_possible() * category.display_scale
            pretty = '{}{}'.format(pretty.quantize(Decimal(10) ** (-1 * calculation_rule.decimal_places), ROUND_HALF_UP), category.display_symbol)
        else:
            pretty = agg.cached_value.quantize(Decimal(10) ** (-1 * calculation_rule.decimal_places), ROUND_HALF_UP)
        return pretty, agg.pk
    else:
        return None, agg.pk

def gradebook_get_category_average(student, category, marking_period):
    try:
        agg = benchmark_get_or_flush(student.aggregate_set, course=None, category=category, marking_period=marking_period)
    except Aggregate.DoesNotExist:
        agg, created = benchmark_calculate_category_as_course_aggregate(student, category, marking_period)
    if agg.cached_substitution is not None:
        return agg.cached_substitution
    elif agg.cached_value is not None:
        calculation_rule = benchmark_find_calculation_rule(marking_period.school_year)
        if category.display_scale is not None:
            pretty = agg.cached_value / agg._fallback_points_possible() * category.display_scale
            pretty = '{}{}'.format(pretty.quantize(Decimal(10) ** (-1 * calculation_rule.decimal_places), ROUND_HALF_UP), category.display_symbol)
        else:
            pretty = agg.cached_value.quantize(Decimal(10) ** (-1 * calculation_rule.decimal_places), ROUND_HALF_UP)
        return pretty
    else:
        return None


''' ye olde belowe '''
# TODO: This is still used for reports!!! Can we trash it?

def benchmark_calculate_grade_for_courses(student, courses, marking_period=None, date_report=None):
    # TODO: Decimal places configuration value
    DECIMAL_PLACES = 2
    # student: a single student
    # courses: all courses involved in the GPA calculation
    # marking_period: restricts GPA calculation to a _single_ marking period
    # date_report: restricts GPA calculation to marking periods _ending_ on or before a date

    mps = None
    if marking_period is not None:
        mps = MarkingPeriod.objects.filter(id=(marking_period.id))
    else:
        mps = MarkingPeriod.objects.filter(id__in=courses.values('marking_period').distinct())
        if date_report is not None:
            mps = mps.filter(end_date__lte=date_report)
        else:
            mps = course.marking_period.all()

    student_numer = student_denom = float(0)
    for mp in mps.filter(school_year__benchmark_grade=True):
        mp_numer = mp_denom = float(0)
        rule = benchmark_find_calculation_rule(mp.school_year)
        for course in courses.filter(marking_period=mp).exclude(credits=None).distinct(): # IMO, Course.credits should be required, and we should not treat None as 0.
            # Handle per-course categories according to the calculation rule
            course_numer = course_denom = float(0)
            for category in rule.per_course_category_set.filter(apply_to_departments=course.department):
                try: category_aggregate = benchmark_get_or_flush(Aggregate, student=student, marking_period=mp, course=course, category=category.category)
                except Aggregate.DoesNotExist: category_aggregate = None
                if category_aggregate is not None and category_aggregate.cached_value is not None:
                    # simplified normalization; assumes minimum is 0
                    normalized_value = category_aggregate.cached_value / rule.points_possible
                    course_numer += float(category.weight) * float(normalized_value)
                    course_denom += float(category.weight)
            if course_denom > 0:
                credits = float(course.credits) / course.marking_period.count()
                mp_numer += credits * course_numer / course_denom
                mp_denom += credits

        # Handle aggregates of categories that are counted as courses
        # TODO: Change CalculationRule model to have a field for the weight of each category. For now, assume 1.
        # Categories as courses shouldn't increase the weight of a marking period!
        mp_denom_before_categories = mp_denom
        for category in rule.category_as_course_set.all():
            category_numer = category_denom = float(0)
            for course in courses.filter(marking_period=mp, department__in=category.include_departments.all()).distinct():
                credits = float(course.credits) / course.marking_period.count()
                try: category_aggregate = benchmark_get_or_flush(Aggregate, student=student, marking_period=mp, category=category.category, course=course)
                except Aggregate.DoesNotExist: category_aggregate = None
                if category_aggregate is not None and category_aggregate.cached_value is not None:
                    # simplified normalization; assumes minimum is 0
                    normalized_value  = category_aggregate.cached_value / rule.points_possible
                    category_numer += credits * float(normalized_value)
                    category_denom += credits
            if category_denom > 0:
                mp_numer += category_numer / category_denom
                mp_denom += 1

        if mp_denom > 0:
            mp_numer *= float(rule.points_possible)
            student_numer += mp_numer / mp_denom * mp_denom_before_categories 
            student_denom += mp_denom_before_categories
            mp_denom = mp_denom_before_categories # in this version, mp_denom isn't used again, but this may save someone pain in the future.

    # Handle non-benchmark-grade years. Calculation rules don't apply.
    legacy_courses = courses.filter(marking_period__in=mps.filter(school_year__benchmark_grade=False))
    for course in legacy_courses.exclude(credits=None).distinct(): # IMO, Course.credits should be required, and we should not treat None as 0.
        try:
            grade, credits = student._calculate_grade_for_single_course(course, marking_period, date_report)
            student_numer += grade * credits
            student_denom += credits
        except:
            pass#logging.warning('Legacy course grade calculation failed for student {}, course {}, marking_period {}, date_report {}'.format(student, course, marking_period, date_report), exc_info=True)
            
    if student_denom > 0:
        return Decimal(student_numer / student_denom).quantize(Decimal(10) ** (-1 * DECIMAL_PLACES), ROUND_HALF_UP)
    else:
        return 'N/A'
