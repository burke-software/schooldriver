from rest_framework import viewsets
from rest_framework import filters
from ecwsp.schedule.models import (
    Course, CourseSection, CourseEnrollment, MarkingPeriod)
from api.schedule.serializers import (
    CourseSerializer, SectionSerializer, CourseEnrollmentSerializer)
from datetime import date


class CourseViewSet(viewsets.ModelViewSet):
    """
    an API endpoint for the Course model
    """
    queryset = Course.objects.prefetch_related(
        'sections', 'sections__periods', 'sections__teachers',
        'sections__enrollments', 'sections__cohorts',
        'sections__marking_period')
    serializer_class = CourseSerializer
    paginate_by = 100


class SectionViewSet(viewsets.ModelViewSet):
    """
    an API endpoint for the CourseSection model
    """
    queryset = CourseSection.objects.all()
    serializer_class = SectionSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('course', 'enrollments', 'marking_period',)


class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    """
    an API endpoint for the CourseEnrollment model
    """
    today = date.today()
    current_mp = MarkingPeriod.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
    ).order_by('-start_date').first()
    if current_mp:
        queryset = CourseEnrollment.objects.filter(
            course_section__marking_period=current_mp.id)
    else:
        queryset = CourseEnrollment.objects.none()
    serializer_class = CourseEnrollmentSerializer
    filter_fields = ('user',)
