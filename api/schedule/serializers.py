from ecwsp.schedule.models import Course, CourseSection, Department
from rest_framework import serializers

class DepartmentNestedSerializer(serializers.ModelSerializer):
    """
    a department serializer for nesting purposes
    should be passed "read_only=True"
    """

    class Meta:
        model = Department
        fields = ('id', 'name',)

class CourseNestedSerializer(serializers.ModelSerializer):
    """
    a course serializer for nesting purposes
    should be passed "read_only=True"
    """
    department = DepartmentNestedSerializer(source='department', read_only=True) 

    class Meta:
        model = Course
        fields = ('id', 'fullname', 'credits', 'graded', 'department',)

class CourseSerializer(serializers.ModelSerializer):
    """
    serializing the Course Model for use with the API
    """

    id = serializers.Field()
    sections = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(source='department')
    department = DepartmentNestedSerializer(source='department', read_only=True)

    class Meta:
        model = Course

class SectionSerializer(serializers.ModelSerializer):
    """
    serializing the CourseSection Model for use with the API
    """

    id = serializers.Field()
    course_id = serializers.PrimaryKeyRelatedField(source='course')
    course = CourseNestedSerializer(source='course', read_only=True)

    class Meta:
        model = CourseSection





