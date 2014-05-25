from ecwsp.schedule.models import Course, CourseSection
from rest_framework import serializers

class CourseSerializer(serializers.ModelSerializer):
    """
    serializing the Course Model for use with the API
    """
    sections = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = Course
