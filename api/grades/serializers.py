from ecwsp.grades.models import Grade
from rest_framework import serializers
from django.core.exceptions import ValidationError

class GradeSerializer(serializers.ModelSerializer):
    """
    serializing the Grade Model for use with the API
    """
    id = serializers.Field()
    student = serializers.RelatedField(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(source='student')
    marking_period = serializers.RelatedField(read_only=True)
    marking_period_id = serializers.PrimaryKeyRelatedField(source='marking_period', required=False)
    course_section = serializers.RelatedField(source='course_section', read_only=True)
    course_section_id = serializers.PrimaryKeyRelatedField(source='course_section', required=False)
    grade = serializers.WritableField(source='api_grade', required=False)

    class Meta:
        model = Grade

    def validate_grade(self, attrs, source):
        value = attrs[source]
        Grade.validate_grade(value)
        return attrs
