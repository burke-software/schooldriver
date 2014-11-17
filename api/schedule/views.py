from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework import filters
from ecwsp.schedule.models import Course, CourseSection
from api.schedule.serializers import CourseSerializer, SectionSerializer

class CourseViewSet(viewsets.ModelViewSet):
    """
    an API endpoint for the Course model
    """
    permission_classes = (IsAdminUser,)
    queryset = Course.objects.prefetch_related(
            'sections', 'sections__periods', 'sections__teachers', 'sections__enrollments', 'sections__cohorts', 'sections__marking_period')
    serializer_class = CourseSerializer
    paginate_by = 100

class SectionViewSet(viewsets.ModelViewSet):
    """
    an API endpoint for the CourseSection model
    """
    permission_classes = (IsAdminUser,)
    queryset = CourseSection.objects.all()
    serializer_class = SectionSerializer          
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('course',)
