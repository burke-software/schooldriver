# Basic grades and assignments

At the core a gradebook is a collection of assignments and marks a student earns.
See the Gradebook [models]. 

Grades are stored with 5 significant digits and 2 decimal places. 

If a student has not earned any mark for a assignment - it is not included in grade calculations.

**Example** [Unit test] GradeCalculationTests.test_basic_grades.

A teacher creates an assignment with 10 points possible. A student earns a "mark" of 5 points. 
By default the gradescale is out of 100 points. We will see later this can be configured.

The student earns a marking period grade of 50. Commonly we might call this 50%. 

Next an assignment with 5 points possible is created. The student earns 5 points. This assignment by it self would earn 100%. The marking period grade would be 66.67%. Note the rounding. We could write it as 066.67 to show all significant digits.

If an assignment is given of 5000 points and the student has no grade entered. The students grade remains 66.67. 

# Assignment Category

See [models] AssignmentCategory.
Assignment Categories are school wide defined categories for assignments. They are used in both benchmark driven grading or in a traditional gradebook.

**NEEDS UNIT TEST**

# Calculation Rules

See [models] CalculationRule.
Rules must be set with a first year effective. Years after this will use the same calculation rule unless a new one is specified. [Unit test] GradeCalculationTests.test_find_calculation_rule. 
The rule also specified the total points possible for a student to receive. For example this could be set to 4 to create a out of 4.0 scale. This should not be confused with a non linear 4.0 scale some schools use where percentage grades are boxed into arbitrary places between 0 and 4

**Example** [Unit test] GradeCalculationTests.test_calculation_rule

A calculation rule defines the points possible as 4. An assignment is created with 10 points possible. A student earns a 5 points mark. The student's grade would be 002.00.

## Weights per category

See [models] CalculationRulePerCourseCategory.
Calculation rules can include enforced weighting by category. These can optionally be restricted by department. This allows departments to set their own weighting categories. Note weights do not have to add up to 1.

When weights are used - all categories must be weigted. For instance it makes no sense to calculate a grade if one weight is 0.5 and another is None. This would raise an error.

**Example** [Unit test] GradeCalculationTests.test_calc_rule_per_course_category

Category1 has a weight of 0.7. Category2 has a weight of 0.3.
Assignments include
- 10 Points possible, category1, student earns 0
- 10 points possible, category2, student earns 10
- 30 points possible, category2, student earns 30

The student would receive a 30%

## Grade Substitutions

See [models] CalculationRuleSubstitution.
A final grade can get substituted with a letter grade, numeric, or both. 
Rules are set to compare a mark against. If the mark criteria is met - the grade is substituted. When communiting to the grades app - the gradebook will return both numeric and letter grades. The numeric grade is used in calculations while the letter grade is displayed on reports.
Substitutions can optionally apply only to specific departments or categories.
Grade substitutions can also be used to visually flag a grade that meets it's criteria.

**Example** [Unit test] GradeCalculationTests.test_rule_substitution

Let a rule be any mark < 3.0 be displayed as 'INC' but calculated normally.
Assignments include
- 4 points possible, 3 points earned. Grade is now 75.
- 4 points possible, 2.5 points earned. Grade is now INC because this assignment meets the substitute criteria.

# Assignment Types

Assignment types are teacher defined categories. We'll use only the term Type for them to avoid confusion with AssignmentCategory. Default types can be set schoolwide too. Assignment types allow a teacher to define weights. Schooldriver supports setting both Category and Type weights. The double weights would be computed into a compound weight for the grade and then applied.
Assignment type weights do not have to add up to one but are not allowed to be None.

**Example** [Unit test] GradeCalculationTests.test_assignment_type

Let type1 be weighted as 0.4
Let type2 be weighted as 0.5
Let type2 be weighted as 0.1
Assignments:
- 10 possible, 5 earned, type1. Grade is 50.00
- 10 possible, 8 earned, type2. Grade is now 66.67
- 10 possible 10 earned, type3. Grade is now 70.00

# Demonstrations

Demonstrations allow students to retake an assigment for a better score. 
It's often used in benchmark driven grading systems.
All but the best demonstration is discarded in calculations. 
Demonstrations can only be enabled by checking Allow Multiple Demostrations from an Assignment Category.
A grade calculation might average assignment grades that have demonstrations and some that don't. This is done by taking only the max mark for any assignment. 
Technically speaking the demonstration table only is used for storing meta data about a demonstration that might be seen in a gradebook UI. It is not used in any calculations.

**Example** [Unit test] GradeCalculationTest.test_demonstration

Let Assignment Category1 allow multiple demostrations
Let an assignment be worth 4 points. Set this assignment's category to Category1
A student earns 1 point on demostration1. The student's grade is now 25.00
A student earns 4 points on demostration2 for the same assignment. The student's grade is now 100.00.

## Students Demonstrated

## Demonstrated

# Course Average

# Comments

[models]: https://github.com/burke-software/django-sis/blob/benchmark_experiment/ecwsp/gradebook/models.py
[Unit test]: https://github.com/burke-software/django-sis/blob/benchmark_experiment/ecwsp/gradebook/tests.py
