from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.permissions import BelongsToStudent
from api.filters import BelongsToStudentFilter
from rest_framework import filters
from ecwsp.grades.models import Grade
from ecwsp.schedule.models import CourseSection
from api.grades.serializers import GradeSerializer
from rest_framework import mixins

class GradeViewSet(viewsets.ModelViewSet):
    """
    an API endpoint for the Grade model
    """
    permission_classes = (IsAuthenticated, BelongsToStudent)
    queryset = Grade.objects.all()
    #filter_backends = (BelongsToStudentFilter,)
    serializer_class = GradeSerializer
    filter_fields = ('course_section', 'course_section__marking_period__school_year')

