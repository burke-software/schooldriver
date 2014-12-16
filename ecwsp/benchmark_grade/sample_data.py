from ecwsp.sis.sample_data import SisData
from ecwsp.sis.models import SchoolYear
from ecwsp.administration.models import Configuration
from ecwsp.schedule.models import Department, DepartmentGraduationCredits
from .models import *

class BenchmarkSisData(SisData):
    def create_tc_calculation_rules(self):
        school_year = SchoolYear.objects.get(active_year=True)
        school_year.benchmark_grade = True
        school_year.save()
        self.calculation_rule = CalculationRule.objects.create(
            first_year_effective=school_year,
            points_possible = 4,
            decimal_places = 2,
        )
        Category.objects.bulk_create([
            Category(name="Precision and Accuracy"),
            Category(
                name="Standards",
                allow_multiple_demonstrations=True,
                demonstration_aggregation_method='Max',
                display_in_gradebook=True,
                fixed_points_possible=4.0,
                fixed_granularity=0.5,
                display_order=1,
            ),
            Category(
                name="Engagement",
                display_in_gradebook=True,
                fixed_points_possible=4.0,
                fixed_granularity=0.5,
                display_order=2,
            ),
            Category(
                name="Assignment Completion",
                display_in_gradebook=True,
                fixed_points_possible=4.0,
                fixed_granularity=0.5,
                display_order=3,
            ),
            Category(
                name="Daily Practice",
                display_in_gradebook=True,
                display_order=4,
                display_scale=100.00,
                display_symbol='%',
            ),
        ])
        CalculationRulePerCourseCategory.objects.bulk_create([
            CalculationRulePerCourseCategory(
                category=Category.objects.get(name="Standards"),
                weight=0.7,
                calculation_rule=self.calculation_rule,
            ),
            CalculationRulePerCourseCategory(
                category=Category.objects.get(name="Engagement"),
                weight=0.1,
                calculation_rule=self.calculation_rule,
            ),
            CalculationRulePerCourseCategory(
                category=Category.objects.get(name="Assignment Completion"),
                weight=0.1,
                calculation_rule=self.calculation_rule,
            ),
            CalculationRulePerCourseCategory(
                category=Category.objects.get(name="Daily Practice"),
                weight=0.1,
                calculation_rule=self.calculation_rule,
            ),
        ])
        Department.objects.bulk_create([
            Department(name="English"),
            Department(name="Math"),
            Department(name="Corporate Work Study"),
            Department(name="Science"),
            Department(name="Religion"),
            Department(name="Social Studies"),
            Department(name="World Languages"),
            Department(name="P.E. & Health"),
            Department(name="Elective"),
            Department(name="Multi-Course Average"),
        ])
        normal_depts = Department.objects.exclude(
            name="Corporate Work Study").exclude(name="Multi-Course Average")
        for rcat in CalculationRulePerCourseCategory.objects.all():
            for dept in normal_depts:
                rcat.apply_to_departments.add(dept)

        x = CalculationRulePerCourseCategory.objects.create(
            category=Category.objects.get(name="Standards"),
            weight=1.0,
            calculation_rule=self.calculation_rule,
        )
        x.apply_to_departments.add(Department.objects.get(
            name="Corporate Work Study"))
        sub1 = CalculationRuleSubstitution.objects.create(
            operator='<', match_value=3, display_as='INC',
            flag_visually=True,
            calculation_rule=self.calculation_rule,
        )
        for dept in normal_depts:
            sub1.apply_to_departments.add(dept)
        sub1.apply_to_departments.add(Department.objects.get(
            name="Corporate Work Study"))
        sub1.apply_to_categories.add(Category.objects.get(name="Standards"))
        sub2 = CalculationRuleSubstitution.objects.create(
            operator='==', match_value=0, flag_visually=True,
            calculation_rule=self.calculation_rule,
        )
        for dept in normal_depts:
            sub2.apply_to_departments.add(dept)
        sub2.apply_to_categories.add(Category.objects.get(
            name="Daily Practice"))
        sub2.apply_to_departments.add(Department.objects.get(
            name="Corporate Work Study"))
        conf = Configuration.objects.get_or_create(
            name="Gradebook extra information")[0]
        conf.value = "demonstrations"
        conf.save()

