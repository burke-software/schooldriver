from ecwsp.sis.forms import *
from ecwsp.sis.xlsReport import *
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