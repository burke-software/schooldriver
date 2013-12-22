from slide_report.report import SlideReport
from slide_report.filters import DecimalCompareFilter, IntCompareFilter
from django import forms
from ecwsp.sis.models import Student

class SisReport(SlideReport):
    name = "student_report"
    model = Student
    filters = (
        DecimalCompareFilter(verbose_name="Filter by GPA", compare_field_string="cache_gpa"),
        IntCompareFilter(verbose_name="Tardies", compare_field_string="fuck"),
    )

sis = SisReport()
