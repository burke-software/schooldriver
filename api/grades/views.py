from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework import filters
from ecwsp.grades.models import Grade
from ecwsp.schedule.models import CourseSection
from api.grades.serializers import GradeSerializer
from rest_framework import mixins

class GradeViewSet(viewsets.ModelViewSet):
    """
    an API endpoint for the Grade model
    """
    permission_classes = (IsAdminUser,)
    queryset = Grade.objects.filter(
        course_section__course__graded = True,
        ).select_related('student', 'marking_period', 'course_section', 'course_section__course')

    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    serializer_class = GradeSerializer
    filter_fields = ('student', 'course_section', 'course_section__marking_period__school_year')
    ordering_fields = ('marking_period__start_date',)

