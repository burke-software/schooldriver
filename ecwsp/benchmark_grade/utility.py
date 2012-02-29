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

from ecwsp.benchmark_grade.models import *

def benchmark_calculate_grade_for_courses(student, courses, marking_period=None, date_report=None):
    #print "b_c_g_f_c(", student, courses, marking_period, date_report, ")"
    # trying to rewrite this for the fourth time.
    # student: guess what? a student!
    # courses: all courses involved in the GPA calculation
    # marking_period: restricts GPA calculation to a _single_ marking period
    # date_report: restricts GPA calculation to marking periods _ending_ on or before a date

    benchmark_individual_cat_name = ('Standards', )
    benchmark_aggregate_cat_name = ('Engagement', 'Organization')

    legacy_numerator = 0
    legacy_denominator = 0

    benchmark_individual_cat = []
    benchmark_aggregate_cat = []
    # dicts within dicts: {MarkingPeriod: {Category: float}}
    benchmark_individual_numer = {} # still come from Aggregate, but then go into GPA individually
    benchmark_individual_denom = {}
    benchmark_aggregate_numer = {} # get averaged and then glommed onto the GPA like extra courses
    benchmark_aggregate_denom = {}
    benchmark_mp_weight = {} # beef up benchmark_grade averages at the end to compete with legacy ones 
    for cat_name in benchmark_individual_cat_name:
        benchmark_individual_cat.append(Category.objects.get(name=cat_name))
    for cat_name in benchmark_aggregate_cat_name:
        benchmark_aggregate_cat.append(Category.objects.get(name=cat_name))

    for course in courses.distinct():
        if course.marking_period.order_by('-start_date')[0].school_year.benchmark_grade:
            # a benchmark_grade course!
            mps = None
            if marking_period is not None:
                mps = (marking_period, )
            elif date_report is not None:
                mps = course.marking_period.filter(end_date__lte=date_report)
            else:
                mps = course.marking_period.all()
            for mp in mps:
                weight = float(course.credits) / course.marking_period.count()
                benchmark_mp_weight[mp.id] = benchmark_mp_weight.get(mp.id, 0) + weight
                for cat in benchmark_individual_cat:
                    try: agg = Aggregate.objects.get(singleStudent = student, singleCourse = course, singleCategory = cat, singleMarkingPeriod = mp)
                    except: continue
                    if agg.cachedValue is None: continue
                    # awfulness to avoid throwing KeyErrors
                    mp_numer_dict = benchmark_individual_numer.get(mp.id, {})
                    mp_denom_dict = benchmark_individual_denom.get(mp.id, {})
                    mp_numer_dict[cat.id] = mp_numer_dict.get(cat.id, 0) + weight * float(agg.cachedValue)
                    mp_denom_dict[cat.id] = mp_denom_dict.get(cat.id, 0) + weight
                    benchmark_individual_numer[mp.id] = mp_numer_dict
                    benchmark_individual_denom[mp.id] = mp_denom_dict
                for cat in benchmark_aggregate_cat:
                    try: agg = Aggregate.objects.get(singleStudent = student, singleCourse = course, singleCategory = cat, singleMarkingPeriod = mp)
                    except: continue
                    if agg.cachedValue is None: continue
                    mp_numer_dict = benchmark_aggregate_numer.get(mp.id, {})
                    mp_denom_dict = benchmark_aggregate_denom.get(mp.id, {})
                    mp_numer_dict[cat.id] = mp_numer_dict.get(cat.id, 0) + weight * float(agg.cachedValue)
                    mp_denom_dict[cat.id] = mp_denom_dict.get(cat.id, 0) + weight
                    benchmark_aggregate_numer[mp.id] = mp_numer_dict
                    benchmark_aggregate_denom[mp.id] = mp_denom_dict
        else:
            # legacy calculation
            try:
                grade, credit = __calculate_grade_for_single_course(course, marking_period, date_report)
                legacy_denominator += credit
                legacy_numerator += float(grade) * credit
            except Exception as e:
                #print e
                pass

    gpa_numerator = 0
    gpa_denominator = 0
    for (mp_id, mp_individual_numer) in benchmark_individual_numer.items():
        numerator = 0
        denominator = 0
        for (cat_id, cat_agg) in mp_individual_numer.items():
            numerator += cat_agg
            denominator += benchmark_individual_denom[mp_id][cat_id]
        #print "after individuals, gpa is", numerator / denominator, "(", numerator, "/", denominator, ")"
        for (cat_id, cat_agg) in benchmark_aggregate_numer[mp_id].items():
            numerator += cat_agg / benchmark_aggregate_denom[mp_id][cat_id]
            #print "glomming on", Category.objects.get(id=cat_id), cat_agg / benchmark_aggregate_denom[mp_id][cat_id]
            denominator += 1
        #print numerator, denominator
        if denominator > 0:
            gpa_numerator += (numerator / denominator) * benchmark_mp_weight[mp_id]
            gpa_denominator += benchmark_mp_weight[mp_id]
    #print "new", gpa_numerator, gpa_denominator
    #print "legacy", legacy_numerator, legacy_denominator
    gpa_numerator += legacy_numerator
    gpa_denominator += legacy_denominator
    if gpa_denominator > 0:
        return Decimal(str(gpa_numerator / gpa_denominator)).quantize(Decimal("0.01"), ROUND_HALF_UP)
    else:
        return "N/A" # follow the modelo
