from rest_framework import viewsets
from .models import Student, StudentNumber, SchoolYear
from .serializers import (
	StudentSerializer, StudentNumberSerializer, SchoolYearSerializer)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentNumberViewSet(viewsets.ModelViewSet):
    queryset = StudentNumber.objects.all()
    serializer_class = StudentNumberSerializer
    filter_fields = ('student',)


class SchoolYearViewSet(viewsets.ModelViewSet):
    queryset = SchoolYear.objects.all()
    serializer_class = SchoolYearSerializer
    filter_fields = ('markingperiod__coursesection__enrollments',)
