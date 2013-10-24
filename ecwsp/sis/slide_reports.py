from slide_report.report import SlideReport, Filter
from ecwsp.sis.models import Student

class GpaFilter(Filter):
    verbose_name = "Filter by GPA"

    def queryset_filter(self, queryset):
        print "hello!!"
        return queryset.filter(cache_gpa__gt=95)



class SisReport(SlideReport):
    name = "student_report"
    model = Student
    filters = (GpaFilter,)

SisReport()
