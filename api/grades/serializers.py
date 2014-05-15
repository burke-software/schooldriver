from ecwsp.grades.models import Grade
from rest_framework import serializers

class GradeSerializer(serializers.ModelSerializer):
    """
    serializing the Grade Model for use with the API
    """
    id = serializers.Field()
    student = serializers.RelatedField(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(source='student')
    marking_period = serializers.RelatedField(read_only=True)
    marking_period_id = serializers.PrimaryKeyRelatedField(source='marking_period')
    grade = serializers.WritableField(source='api_grade')

    class Meta:
        model = Grade
