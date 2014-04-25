from rest_framework import viewsets
from ecwsp.grades.models import Grade
from api.grades.serializers import GradeSerializer

class GradeViewSet(viewsets.ModelViewSet):
    """
    an API endpoint for the Grade model
    """
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
