from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Grade
from ecwsp.sis.models import Student
from ecwsp.schedule.models import MarkingPeriod, CourseSection

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ('grade', 'marking_period', 'student_id', 'course_section_id',
                  'enrollment')
