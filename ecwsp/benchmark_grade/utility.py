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

from ecwsp.benchmark_grade.models import CalculationRule, Item, Mark, Category, AggregateTask, CalculationRulePerCourseCategory
from ecwsp.benchmark_grade.models import (
    CategoryMarkingPeriodAggregate,
    CourseSectionAggregate,
    CourseSectionCategoryAggregate,
    CourseSectionCategoryMPAggregate,
    CourseSectionMarkingPeriodAggregate,
)
from ecwsp.schedule.models import MarkingPeriod, Department, CourseSection
from ecwsp.sis.models import Student
from ecwsp.benchmark_grade.tasks import benchmark_calculation_task
from ecwsp.grades.models import Grade
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

def gradebook_recalculate_on_item_change(item, students=None, old_item=None):
    '''
    If passed an item, recacluate everything affected by that item.
    If passed an item and students, recalculate everything affected by that item for those students.
    If passed and item and an old_item, figure out what changed and recalculate accordingly.

    Item model fields:
        name - does not affect calculations
        description - does not affect calculations
        course_section - DOES affect calculations but should not change
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
        if old_item.course_section != item.course_section:
            raise Exception('Items must not move between course sections.')
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

    calculation_rule = benchmark_find_calculation_rule(item.course_section.marking_period.all()[0].school_year)
    course_section = item.course_section
    if students is None:
        students = Student.objects.filter(courseenrollment__course_section=item.course_section)

    if renormalization_required:
        # take care of re-normalization before returning
        for mark in item.mark_set.all():
            mark.save()

    # list of aggregates to be calculated in the background and the
    # arguments passed to calculate() for each aggregate
    aggs_and_args = []

    affects_overall_course_section = calculation_rule.per_course_category_set.filter(
        category__in=categories, apply_to_departments=course_section.department
    ).exists()
    affected_categories_as_courses = calculation_rule.category_as_course_set.filter(
        category__in=categories, include_departments=course_section.department)

    for student in students:
        # recalculate the aggregate for the item's course_section, category, and marking period
        agg, created = CourseSectionCategoryMPAggregate.objects.get_or_create(
            student=student,
            course_section=course_section,
            category=item.category,
            marking_period=item.marking_period
        )
        aggs_and_args.append((
            agg,
            (),
            {'recalculate_all': True}
        ))
        if parting_calculation_required:
            # the item was previously in another category or marking period, which now also must be recalculated
            agg, created = CourseSectionCategoryMPAggregate.objects.get_or_create(
                student=student,
                course_section=course_section,
                category=old_item.category,
                marking_period=old_item.marking_period
            )
            aggs_and_args.append((
                agg,
                (),
                {'recalculate_all': True}
            ))

        # recalculate the course-section-long aggregate for each affected category
        for category in categories:
            agg, created = CourseSectionCategoryAggregate.objects.get_or_create(
                student=student,
                course_section=course_section,
                category=category
            )
            aggs_and_args.append((
                agg,
                (),
                {'recalculate_all': True}
            ))

        # recalculate aggregates for affected marking periods
        for marking_period in marking_periods:
            if affects_overall_course_section:
                # The user has explicitly edited one or more marking periods
                # in the gradebook. Pass copy_to_grade=True so that these edits
                # overwrite whatever's in grades.Grade.
                agg, created = CourseSectionMarkingPeriodAggregate.objects.get_or_create(
                    student=student,
                    course_section=course_section,
                    marking_period=marking_period
                )
                aggs_and_args.append((
                    agg,
                    (),
                    {'recalculate_all': True, 'copy_to_grade': True}
                ))
            for category_as_course in affected_categories_as_courses:
                agg, created = CategoryMarkingPeriodAggregate.objects.get_or_create(
                    student=student,
                    category=category_as_course.category,
                    marking_period=marking_period
                )
                aggs_and_args.append((
                    agg,
                    (),
                    {'recalculate_all': True}
                ))

        # recalculate aggregates for the whole duration of the course section
        if affects_overall_course_section:
            agg, created = CourseSectionAggregate.objects.get_or_create(
                student=student,
                course_section=course_section
            )
            aggs_and_args.append((
                agg,
                (),
                {'recalculate_all': True}
            ))

    if len(aggs_and_args):
        aggregates = []
        for aggregate, args, kwargs in aggs_and_args:
            task_id = celery.utils.uuid()
            # flag aggregate that is being recalculated
            aggregate_task = AggregateTask(content_object=aggregate, task_id=task_id)
            try:
                aggregate_task.save()
                aggregates.append(aggregate)
                # queue a task with our predetermined uuid
                task = benchmark_calculation_task.apply_async(
                    args=(
                        aggregate_task.content_type_id,
                        aggregate.pk
                    ) + args,
                    kwargs=kwargs,
                    task_id=task_id
                )
            except IntegrityError as e:
                logging.warning(
                    'We are calculating {} {} multiple times!'.format(
                        type(aggregate).__name__,
                        aggregate.pk
                    ),
                    exc_info=True
                )
        return aggregates

def gradebook_recalculate_on_mark_change(mark):
    return gradebook_recalculate_on_item_change(mark.item, (mark.student, ))

def benchmark_generate_all_aggregates():
    ''' Never called by any other code. Run this manually from the Django shell
    in special circumstances, e.g. after migrating from the old Aggregate model.
    '''

    # We'll be calculating only numbered aggregates directly. Indented aggregates
    # are calculated automatically by the numbered aggregates.
    # (1) CourseSectionAggregate depends on
    #         CourseSectionMarkingPeriodAggregate depends on
    #             CourseSectionCategoryMPAggregate depends on
    #                individual Marks 
    # (2) CourseSectionCategoryAggregate depends on
    #         CourseSectionCategoryMPAggregate (already calculated)
    # (3) CategoryMarkingPeriodAggregate depends on
    #         CourseSectionCategoryMPAggregate ** for every course in the MP **

    from ecwsp.sis.models import SchoolYear
    import sys
    # Figure the first benchmark-grade year from the oldest CalculationRule
    try:
        oldest_year = CalculationRule.objects.order_by(
            'first_year_effective__start_date').first().first_year_effective
    except AttributeError:
        print 'Cannot proceed without any CalculationRules!'
        return
    # Get all the years we should consider
    years = SchoolYear.objects.filter(
        start_date__gte=oldest_year.start_date).order_by('start_date')
    for year in years:
        # Get the rule that applies to this year
        rule = benchmark_find_calculation_rule(year)
        # Get the list of categories used as courses this year; we'll have to 
        # calculate these after finishing with the per-course aggregates
        categories_as_courses = Category.objects.filter(
            calculationrulecategoryascourse__calculation_rule=rule).distinct()
        # We'll need a list later of all the year's students
        students = set()
        # Get all this year's course sections
        course_sections = CourseSection.objects.filter(
            marking_period__school_year=year).distinct()
        for course_section in course_sections:
            print (u'{}\t' * 2).format(year, course_section)
            # Which categories does this course section use?
            categories = Category.objects.filter(
                item__course_section=course_section).distinct() 
            for student in course_section.enrollments.all():
                # Calculate (1) directly:
                agg, created = CourseSectionAggregate.objects.get_or_create(
                    student=student,
                    course_section=course_section
                )
                agg.calculate(recalculate_all=True)
                # Calculate (2) directly:
                for category in categories:
                    agg, created = CourseSectionCategoryAggregate.objects.get_or_create(
                        student=student,
                        course_section=course_section,
                        category=category
                    )
                    # Since (1) is complete, recalculate_all isn't necessary
                    agg.calculate()
                sys.stdout.write('.')
                sys.stdout.flush()
                # Remember this student for later
                students.add(student)
            print ''
        # Calculate (3) directly now that (1) and (2) are done:
        for category in categories_as_courses:
            for marking_period in year.markingperiod_set.all():
                print (u'{}\t' * 3).format(year, category, marking_period)
                for student in students:
                    agg, created = CategoryMarkingPeriodAggregate.objects.get_or_create(
                        student=student,
                        category=category,
                        marking_period=marking_period
                    )
                    # Since (1) and (2) are complete, recalculate_all isn't
                    # necessary
                    agg.calculate()
                    sys.stdout.write('.')
                    sys.stdout.flush()
                print ''
