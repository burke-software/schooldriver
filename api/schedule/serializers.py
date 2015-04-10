from ecwsp.schedule.models import (
    Course, CourseSection, Department, CourseEnrollment, MarkingPeriod, Period, CourseMeet)
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


class FilteredCourseMeetSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        # print dir(data.filter)
        print dir(data.first())
        print type(data.first())
        # print data.first().period_id
        # print data.first().course_section_id

        # print self.context['request'].user
        data = data.filter(period=3, course_section=6)
        return super(FilteredCourseMeetSerializer, self).to_representation(data)


class CourseMeetSerializer(serializers.ModelSerializer):
    day_display = serializers.CharField(
        source='get_day_display', read_only=True)
   
    class Meta:
        model = CourseMeet
        # list_serializer_class = FilteredCourseMeetSerializer


class PeriodSerializer(serializers.ModelSerializer):
    coursemeet_set = CourseMeetSerializer(many=True)
    # id = serializers.SerializerMethodField()

    # def get_id(self, obj):
    #     # print self
    #     print dir(self)
    #     # print self.__dict__
    #     print obj.__dict__
    #     # print self.context['view'].queryset.all()
    #     return 'aaa'

    class Meta:
        model = Period


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
    periods = PeriodSerializer(many=True)
    teachers = serializers.StringRelatedField(many=True)

    class Meta:
        model = CourseSection


class MarkingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkingPeriod
        # fields = ('id', 'name')


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    course_section = SectionSerializer()
    
    class Meta:
        model = CourseEnrollment
        fields = ('course_section',)