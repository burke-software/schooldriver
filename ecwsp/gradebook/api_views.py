from rest_framework import viewsets
from .serializers import AssignmentSerializer, MarkSerializer
from .models import Assignment, Mark


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    queryset = Assignment.objects.all()


class MarkViewSet(viewsets.ModelViewSet):
    serializer_class = MarkSerializer
    queryset = Mark.objects.all()
