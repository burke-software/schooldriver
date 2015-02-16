from rest_framework import viewsets
from .models import Student, SchoolYear
from .serializers import StudentSerializer, SchoolYearSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class SchoolYearViewSet(viewsets.ModelViewSet):
    queryset = SchoolYear.objects.all()
    serializer_class = SchoolYearSerializer
    filter_fields = ('markingperiod__coursesection__enrollments',)
