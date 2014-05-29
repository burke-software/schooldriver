from ecwsp.schedule.models import Course, CourseSection
from rest_framework import serializers

class CourseSerializer(serializers.ModelSerializer):
    """
    serializing the Course Model for use with the API
    """

    id = serializers.Field()
    sections = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Course

class SectionSerializer(serializers.ModelSerializer):
    """
    serializing the CourseSection Model for use with the API
    """

    id = serializers.Field()

    class Meta:
        model = CourseSection
