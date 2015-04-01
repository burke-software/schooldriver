from rest_framework import viewsets
from .serializers import (
    AssignmentSerializer, MarkSerializer, AssignmentCategorySerializer, 
    AssignmentTypeSerializer)
from .models import Assignment, Mark, AssignmentCategory, AssignmentType


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    queryset = Assignment.objects.all()


class MarkViewSet(viewsets.ModelViewSet):
    serializer_class = MarkSerializer
    queryset = Mark.objects.all()


class AssignmentCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentCategorySerializer
    queryset = AssignmentCategory.objects.all()


class AssignmentTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentTypeSerializer
    queryset = AssignmentType.objects.all()
