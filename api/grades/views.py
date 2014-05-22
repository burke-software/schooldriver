from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from ecwsp.grades.models import Grade
from api.grades.serializers import GradeSerializer

class GradeViewSet(viewsets.ModelViewSet):
    """
    an API endpoint for the Grade model
    """
    permission_classes = (IsAdminUser,)
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
