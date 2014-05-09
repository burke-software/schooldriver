from ecwsp.grades.models import Grade
from rest_framework import serializers

class GradeSerializer(serializers.ModelSerializer):
    """
    serializing the Grade Model for use with the API
    """
    id = serializers.Field()
    student = serializers.RelatedField()
    student_id = serializers.PrimaryKeyRelatedField(source='student')

    class Meta:
        model = Grade
