# Course Grades

Each course section enrollment should have an average (final) grade based on particular marking period grades.

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


[Student Reports]: https://github.com/burke-software/django-sis/blob/master/ecwsp/sis/scaffold_reports.py
[test_course_average_respect_time]: https://github.com/burke-software/django-sis/blob/5d24e855284374997da9772d43589d554977be54/ecwsp/grades/tests.py#L21
