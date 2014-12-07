# Gradescales

Converting numberic grades to letter (A, B, C...) and other non linear number scales (4.0)

## Description

Number grades, often out of 100 or 4.0, are typically what teachers work with day to day. It is desired to display these grade results in an alternative scale representation defined by a range of two numbers. For example 93-100 would be an A or a 4.0.

Grade scales are set per year. [GradeScale model]

[GradeScale model]: https://github.com/burke-software/django-sis/blob/master/ecwsp/sis/models.py#L687

## Rounding and grade scales

[test_average_partial_round_before_letter]

Let grade one be `75.49` and grade two be `77.50`. The average would be `76.495`.
Let our grade scale ranges be `72.50 to 76.49 = C` and `76.50 to 79.49 = C+`.
`76.495` is technically inbetween the two scales - falling on no scale at all. 
To solve this and present a non absurd answer - the grade will be averaged to the number of significant digits the numeric grades are in. Grades are stored in Decimal(5,2) so our result would be averaged to `76.50` and thus result in an `C+`.

[test_average_partial_round_before_letter]: https://github.com/burke-software/django-sis/blob/7e30c299afadfd2cf045664ac45ca8463f12f39a/ecwsp/grades/tests.py#L186
