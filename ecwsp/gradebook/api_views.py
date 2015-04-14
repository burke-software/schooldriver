from rest_framework import viewsets
from .serializers import (
    AssignmentSerializer, MarkSerializer, AssignmentCategorySerializer, 
    AssignmentTypeSerializer, StudentMarkSerializer)
from .models import Assignment, Mark, AssignmentCategory, AssignmentType
from ecwsp.schedule.models import CourseSection



class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    queryset = Assignment.objects.all()


class MarkViewSet(viewsets.ModelViewSet):
    serializer_class = MarkSerializer
    queryset = Mark.objects.all()


class StudentMarkViewSet(viewsets.ModelViewSet):
    serializer_class = StudentMarkSerializer
    queryset = CourseSection.objects.all()
    filter_fields = ('id', 'enrollments__id')


class AssignmentCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentCategorySerializer
    queryset = AssignmentCategory.objects.all()


class AssignmentTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentTypeSerializer
    queryset = AssignmentType.objects.all()
