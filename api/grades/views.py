from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework import filters
from ecwsp.grades.models import Grade
from ecwsp.schedule.models import CourseSection
from api.grades.serializers import GradeSerializer
from rest_framework import mixins
from django.db.models import F, Q

class GradeViewSet(viewsets.ModelViewSet):
    """
    an API endpoint for the Grade model
    """
    permission_classes = (IsAdminUser,)
    queryset = Grade.objects.filter(
        # Exclude orphans from MPs no longer assigned to the CourseSection 
        # except for grade objects with an explicit null marking period
        # and override_final flag since those grade objects are used to 
        # override the final grade in their associated course section
        Q(course_section__marking_period=F('marking_period')) | ( Q(marking_period=None) & Q(override_final=True) ),
        course_section__course__graded = True,
    ).select_related('student', 'marking_period', 'course_section', 'course_section__course').distinct()

    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    serializer_class = GradeSerializer
    filter_fields = ('student', 'course_section', 'course_section__marking_period__school_year')
    ordering_fields = ('marking_period__start_date',)
