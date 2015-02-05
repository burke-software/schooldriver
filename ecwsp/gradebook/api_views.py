from rest_framework import viewsets
from .serializers import AssignmentSerializer
from .models import Assignment


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    queryset = Assignment.objects.all()
