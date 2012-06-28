from django.db.models import Q

from ecwsp.sis.forms import *
from ecwsp.sis.xlsReport import *
from ecwsp.sis.report import *
import xlwt


def fail_report(request):
    from ecwsp.grades.models import Grade
    form = MarkingPeriodForm(request.POST)
    if form.is_valid():
        marking_periods = form.cleaned_data['marking_period']
        students = Student.objects.filter(courseenrollment__course__marking_period__in=marking_periods).distinct()
        titles = ['']
        departments = Department.objects.filter(course__courseenrollment__user__inactive=False).distinct()
        
        for department in departments:
            titles += [department]
        titles += ['Total', '', 'Username', 'Year','GPA', '', 'Failed courses']
        
        passing_grade = int(Configuration.get_or_default('Passing Grade','70').value)
        
        data = []
        iy=3
        for student in students:
            row = [student]
            ix = 1 # letter A
            student.failed_grades = Grade.objects.none()
            for department in departments:
                failed_grades = Grade.objects.filter(override_final=False,course__department=department,course__courseenrollment__user=student,grade__lte=passing_grade,marking_period__in=marking_periods)
                row += [failed_grades.count()]
                student.failed_grades = student.failed_grades | failed_grades
                ix += 1
            row += [
                xlwt.Formula(
                    'sum(b%s:%s%s)' % (str(iy),i_to_column_letter(ix),str(iy))
                    ),
                '',
                student.username,
                student.year,
                student.gpa,
                '',
                ]
            for grade in student.failed_grades:
                row += [grade.course, grade.marking_period, grade.grade]
            data += [row]
            iy += 1
            
        report = xlsReport(data, titles, "fail_report.xls", heading="Failure Report")
        return report.finish()
        
def student_grade(request, form):
    data = form.cleaned_data
    if data['template']:
        # use selected template
        template = data['template']
        template_path = template.get_template_path(request)
        if not template_path:
            form.fields['template'].queryset = Template.objects.filter(Q(report_card=True) | Q(transcript=True))
            #return render_to_response('sis/grade_report.html', {'form':form, 'mp_form':mp_form}, RequestContext(request, {}),)
        report_card = template.report_card
        transcript = template.transcript
    else:
        # or use uploaded template, saving it to temp file
        template = request.FILES['upload_template']
        tmpfile = mkstemp()[1]
        f = open(tmpfile, 'wb')
        f.write(template.read())
        f.close()
        template_path = tmpfile
        report_card = True
        transcript = True
    file_format = UserPreference.objects.get_or_create(user=request.user)[0].get_format(type="document")
    return pod_report_grade(template_path, options=data, students=form.get_students(data), format=file_format, report_card=report_card,
                            transcript=transcript)

def aggregate_grade_report(request):
    from ecwsp.grades.models import Grade
    mp_form = MarkingPeriodForm(request.POST)
    if mp_form.is_valid():
        mps = mp_form.cleaned_data['marking_period']
        data = []
        titles = ["Teacher", "Range", "No. Students", ""]
        for level in GradeLevel.objects.all():
            titles += [level, ""]
        ranges = [['100', '90'], ['89.99', '80'], ['79.99', '70'], ['69.99', '60'], ['59.99', '50'], ['49.99', '0']]
        letter_ranges = ['P', 'F']
        for teacher in Faculty.objects.filter(course__marking_period__in=mps).distinct():
            data.append([teacher])
            grades = Grade.objects.filter(
                marking_period__in=mps,
                course__teacher=teacher,
                student__inactive=False,
                override_final=False,
            ).filter(
                Q(grade__isnull=False) |
                Q(letter_grade__isnull=False)
            )
            teacher_students_no = grades.distinct().count()
            if teacher_students_no:
                for range in ranges:
                    no_students = grades.filter(
                            grade__range=(range[1],range[0]),
                        ).distinct().count()
                    percent = float(no_students) / float(teacher_students_no)
                    percent = ('%.2f' % (percent * 100,)).rstrip('0').rstrip('.') + "%"
                    row = ["", str(range[1]) + " to " + str(range[0]), no_students, percent]
                    for level in GradeLevel.objects.all():
                        no_students = grades.filter(
                                grade__range=(range[1],range[0]),
                                student__year__in=[level],
                            ).distinct().count()
                        level_students_no = grades.filter(
                                student__year__in=[level],
                            ).distinct().count()
                        percent = ""
                        if level_students_no:
                            percent = float(no_students) / float(level_students_no)
                            percent = ('%.2f' % (percent * 100,)).rstrip('0').rstrip('.') + "%"
                        row += [no_students, percent]
                    data.append(row)
                for range in letter_ranges:
                    no_students = grades.filter(
                            letter_grade=range,
                        ).distinct().count()
                    if teacher_students_no:
                        percent = float(no_students) / float(teacher_students_no)
                        percent = ('%.2f' % (percent * 100,)).rstrip('0').rstrip('.') + "%"
                    else:
                        percent = ""
                    row = ["", str(range), no_students, percent]
                    for level in GradeLevel.objects.all():
                        no_students = grades.filter(
                                letter_grade=range,
                                student__year__in=[level],
                            ).distinct().count()
                        level_students_no = grades.filter(
                                student__year__in=[level],
                            ).distinct().count()
                        if level_students_no:
                            percent = float(no_students) / float(level_students_no)
                            percent = ('%.2f' % (percent * 100,)).rstrip('0').rstrip('.') + "%"
                        else:
                            percent = ""
                        row += [no_students, percent]
                    data.append(row)
        report = xlsReport(data, titles, "aggregate_grade_report.xls", heading="Teacher aggregate")
        
        passing = 70
        data = []
        titles = ['Grade']
        for dept in Department.objects.all():
            titles.append(dept)
            titles.append('')
        for level in GradeLevel.objects.all():
            row = [level]
            for dept in Department.objects.all():
                fails = Grade.objects.filter(
                    marking_period__in=mps,
                    course__department=dept,
                    student__inactive=False,
                    student__year__in=[level],   # Shouldn't need __in. Makes no sense at all.
                    grade__lt=passing,
                    override_final=False,
                ).count()
                total = Grade.objects.filter(
                    marking_period__in=mps,
                    course__department=dept,
                    student__inactive=False,
                    student__year__in=[level],
                    override_final=False,
                ).count()
                if total:
                    percent = float(fails) / float(total)
                else:
                    percent = 0
                percent = ('%.2f' % (percent * 100,)).rstrip('0').rstrip('.')
                row.append(fails)
                row.append(percent)
            data.append(row)
        report.addSheet(data, titles=titles, heading="Class Dept aggregate")
        return report.finish()
        

def date_based_gpa_report(request):
    input = request.POST.copy()
    input['template'] = 1 # Validation hack
    form = StudentGradeReportWriterForm(input, request.FILES)
    if form.is_valid():
        data = form.cleaned_data
        try:
            students = form.get_students(data)
        except:
            students = Student.objects.filter(inactive = False).order_by('-year__id')
        
        titles = ["Student", "9th", "10th", "11th","12th", "Current"]
        data = []
        current_year = SchoolYear.objects.get(active_year = True)
        two_years_ago = (current_year.end_date + timedelta(weeks=-(2*52))).year
        three_years_ago = (current_year.end_date + timedelta(weeks=-(3*52))).year
        four_years_ago = (current_year.end_date + timedelta(weeks=-(4*52))).year
        for student in students:
            row = []
            gpa = [None,None,None,None,None]
            count = 0
            #years is years that student has courses/grades
            years = SchoolYear.objects.filter(markingperiod__show_reports=True,start_date__lt=date.today(),markingperiod__course__courseenrollment__user=student
            ).exclude(omityeargpa__student=student).distinct().order_by('start_date')
            #if student has courses from any year and is given a grade level (freshman,sophomore, etc.),
            #it checks to see if the student's been at cristorey every year or if they transferred in and when
            current = 0
            try:
                if student.year.id == 12:
                    current = 3
                    if years[0].start_date.year > two_years_ago:
                        gpa[0] = "N/A"
                        gpa[1] = "N/A"
                        gpa[2] = "N/A"
                        count = 3
                    elif years[0].start_date.year > three_years_ago:
                        gpa[0] = "N/A"
                        gpa[1] = "N/A"
                        count = 2
                    elif years[0].start_date.year > four_years_ago:
                        gpa[0] = "N/A"
                        count = 1
                elif student.year.id == 11:
                    current = 2
                    if years[0].start_date.year > two_years_ago:
                        gpa[1] = "N/A"
                        gpa[0] = "N/A"
                        count = 2
                    elif years[0].start_date.year > three_years_ago:
                        gpa[0] = "N/A"
                        count = 1
                elif student.year.id == 10:
                    current = 1
                    if two_years_ago:
                        gpa[0] = "N/A"
                        count = 1
                elif student.year.id == 9:
                    current = 0
            except:pass
            
            for year in years:
                #cumulative gpa per year. Adds one day because it was acting weird and not giving me GPA for first year
                gpa[count] = student.calculate_gpa(year.end_date + timedelta(days=1))
                count +=1
            #if calculate_gpa does not return a value, it is set to "N/A"
            if not gpa[0]:
                gpa[0] = "N/A"
            if not gpa[1]:
                gpa[1] = "N/A"
            if not gpa[2]:
                gpa[2] = "N/A"
            if not gpa[3]:
                gpa[3] = "N/A"
            gpa[4] = gpa[current]
            row = [student, gpa[0],gpa[1],gpa[2],gpa[3],gpa[4]]
            data.append(row)
        report = xlsReport(data, titles, "gpas_by_year.xls", heading="GPAs")
        return report.finish()