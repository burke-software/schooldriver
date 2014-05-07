from ecwsp.grades.models import Grade
from rest_framework import serializers

class GradeSerializer(serializers.HyperlinkedModelSerializer):
    """
    serializing the Grade Model for use with the API
    """
    id = serializers.Field()
    student = serializers.PrimaryKeyRelatedField()
    course = serializers.PrimaryKeyRelatedField()
    marking_period = serializers.PrimaryKeyRelatedField(required=False)

    class Meta:
        model = Grade
