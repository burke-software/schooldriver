from ecwsp.grades.models import Grade
from ecwsp.sis.models import Student
from ecwsp.schedule.models import MarkingPeriod, CourseSection
from rest_framework import serializers


class GradeSerializer(serializers.ModelSerializer):
    """
    serializing the Grade Model for use with the API
    """
    id = serializers.IntegerField(read_only=True)
    student = serializers.StringRelatedField(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        source='student',
        queryset=Student.objects.all(),
    )
    marking_period = serializers.StringRelatedField(read_only=True)
    marking_period_id = serializers.PrimaryKeyRelatedField(
        source='marking_period',
        required=False,
        allow_null=True,
        default=None,
        queryset=MarkingPeriod.objects.all(),
    )
    course_section = serializers.StringRelatedField(read_only=True)
    course_section_id = serializers.PrimaryKeyRelatedField(
        source='course_section',
        required=False,
        queryset=CourseSection.objects.all(),
    )
    grade = serializers.CharField(
        source='api_grade', required=False, allow_blank=True)

    class Meta:
        model = Grade
        exclude = ('letter_grade',)

    def validate_grade(self, value):
        Grade.validate_grade(value)
        return value
