from ecwsp.schedule.models import Course, CourseSection, Department
from ecwsp.sis.models import Faculty
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
    department = DepartmentNestedSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'fullname', 'credits', 'graded', 'department',)


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        exclude = ('password',)


class SimpleSectionSerializer(serializers.ModelSerializer):
    #teachers = TeacherSerializer()
    class Meta:
        model = CourseSection


class CourseSerializer(serializers.ModelSerializer):
    """
    serializing the Course Model for use with the API
    """

    id = serializers.ReadOnlyField()
    #sections = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    sections = SimpleSectionSerializer(many=True)
    department_id = serializers.PrimaryKeyRelatedField(
        source='department',
        queryset=Department.objects.all(),
    )
    department = DepartmentNestedSerializer(read_only=True)

    class Meta:
        model = Course
        depth = 0


class SectionSerializer(serializers.ModelSerializer):
    """
    serializing the CourseSection Model for use with the API
    """

    id = serializers.ReadOnlyField()
    course_id = serializers.PrimaryKeyRelatedField(
        source='course',
        queryset=Course.objects.all(),
    )
    course = CourseNestedSerializer(read_only=True)

    class Meta:
        model = CourseSection
