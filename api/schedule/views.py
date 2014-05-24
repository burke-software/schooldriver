from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework import filters
from ecwsp.schedule.models import Course
from api.schedule.serializers import CourseSerializer

class CourseViewSet(viewsets.ModelViewSet):
    """
    an API endpoint for the Course model
    """
    permission_classes = (IsAdminUser,)
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

            
