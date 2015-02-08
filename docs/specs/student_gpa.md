# Student GPA (Grade Point Average)
The student's grade point average is typically found on report cards and transcripts and represents a cumulative representation of all grades that student has recieved. 


## Marking Period Calculation
Consider a student who is enrolled in the 4 courses below and has recieved the grades in parentheses for a particular marking period

- English (`99.00`)
- Math (`78.00`)
- Religion (`95.00`)
- Physics (`80.00`)

Let's also consider that each course counts for exactly `1` credits during this marking period. To determine the GPA for this marking period, we take the course grade, multiply it by the number of credits for that course, and add the result to the same calculation for each other course. For example:


Total Points = `99.00 x 1` + `78.00 x 1` + `95.00 x 1` + `80.00 x 1`

Total Points = `352.00`

We then take the total points and divide by the number of credits earned during this marking period. The resulting number is the student's marking period GPA.

GPA = Total Points / Total Credits = `352.00` / `4` = `88.00`

## School Year Calculation

The school year calculation is performed much in the same manner as the marking period calculation. Consider the gradebook below, which contains grades for 4 marking periods.

| Course     | MP1 | MP2 | MP3 | MP4 |
|------------|-----|-----|-----|-----|
| English    | 99  | 92  | 93  | 100 |
| Math       | 95  | 92  | 98  | 89  |
| Religion   | 95  | 92  |     |     |
| Mission    |     |     | 92  | 94  |




Let's say for this calculation that each course recieves `1` credit per marking period, so we can calculate the total points and total credits for each course like so:

| Course    | Total Points | Total Credits |
|-----------|--------------|---------------|
| English   |     384      |      4        |
| Math      |     374      |      4        |
| Religion  |     190      |      2        |
| Mission   |     186      |      2        |




Now we simply add the total points for all classes and divide by the total credits for all classes:

GPA = `(384 + 374 + 190 + 186) / (4 + 4 + 2 + 2)`

GPA = `94.50`



## Student Career Calculation

Finally, let's consider a student who has attended a particular school for three years and has recieved the yearly GPA and credits shown below:

| School Year | Year GPA     | Year Credits  |
|-------------|--------------|---------------|
| 2010-2011   |     95.00    |     32        |
| 2011-2012   |     94.30    |     29        |
| 2012-2013   |     91.15    |     31        |





Since the student's career GPA is weighted by the number of credits they have earned, we need to weight the yearly GPA's according to the credits earned each year. To do this we simply multiply the year GPA by the total credits to get a total number of points for each year:

- 2010-2011: `95.00 x 32` = `3040.00`
- 2011-2012: `94.30 x 29` = `2734.70`
- 2012-2013: `91.15 x 31` = `2825.65`

Now we just divide the total points by the total credits to recieve the student's total career GPA:

GPA = `(3040.00 + 2734.70 + 2825.65) / (32 + 29 + 31)`

GPA = `93.48`

### Mid-Year Calculation
Often a school will want to calculate the student's career GPA part of the way during the year. This GPA is calculated by weigthing the current year by the percent completion of that year. For example, let's consider the GPA calculation above, but taking into account that the 2012-2013 school year is only 50% complete:

GPA = `(3040.00 + 2734.70 + (2825.65 x 0.50) ) / (32 + 29 + (31 x 0.50) )`

GPA = `94.57`