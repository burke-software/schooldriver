# Course Grades

Each course section enrollment should have an average (final) grade based on particular marking period grades.

## Rounding

Grades are stored with 5 significant digits and 2 decimal places.
Rounding can be set for a school. 

Rounding happens at the end of a particular grade calculation unless explicitly set otherwise. 

**Example** [Unit test] GradeCalculationTests.test_basic_grades

Assume a student is enrolled in a course with three marking periods
Let rounding be set to 2 decimal places
Let marking period 1 grade = `100`
Let marking period 2 grade = `50`
Let marking period 3 grade = `90.5`

The final grade will result in 80.17 due to rounding.

## Marking Period Weights

A markign period can have a weight assigned to it. 

**Example** [Unit test] GradeCalculationTests.test_marking_period_weight

Let marking period 1 have a weight of 1.5. All others have weight of 1.
Let marking period grades be as follows 100, 50, 90.5 for marking periods 1 through 3.

The final grade would be 83.

## Final Grade Override

A course grade can be overriden - thus overriding any marking period grades.

**Example** [Unit test] GradeCalculationTests.test_final_override

Let marking period grades be anything. 
Let a final grade override for a course be 82.

The final grade for the course would be 82.

## Time and averages

A student could have multiple marking period grades for a course. 
One might ask what is the grade at time x? Or what if the student had a grade for a partially completed marking period.

[Student Reports] uses this concept often. The End Date provided will be used when determining course averages.

See [test_course_average_respect_time] unit test.

Let mp1 start_date=`2014-07-1` and end_date=`2014-9-1`
Let mp2 start_date=`2014-9-2` and end_date=`2015-3-1`
Let mp1 grade = `50`
Let mp2 grade = `100`

For date 2099-1-1 the grade should be 75.
For date 2014-10-1 the grade should be 50 because mp2 has not ended yet and credit is not yet earned.

## Course Type Weights

A Course has a reference to a Course Type which can affect grades.

**Example** [Unit test] GradeCalculationTests.test_course_type_weight 

Let Course1 have a course type with weight 0.5
Let Course2 have a course type with weight 1.0
Let Grade1 belong to Course1 with a grade of 50
Let Grade2 belong to Course2 with a grade of 100

Had no unit test.

[Student Reports]: https://github.com/burke-software/django-sis/blob/master/ecwsp/sis/scaffold_reports.py
[test_course_average_respect_time]: https://github.com/burke-software/django-sis/blob/5d24e855284374997da9772d43589d554977be54/ecwsp/grades/tests.py#L21
[Unit test]: https://github.com/burke-software/django-sis/blob/master/ecwsp/grades/tests/test_basic_grade_calculations.py

## Couse Type Boost

A course with a course type that has a boost will add the boost value to a course grade. 
Could be used in honors classes.

Let Course1 have a course type with boost of 1
Let Grade1 belong to Course1 with a grade of 50.
The calculated grade for the average of all courses is 51.

Has no unit test.
