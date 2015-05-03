from rest_framework import serializers
from .models import Assignment, Mark, AssignmentCategory, AssignmentType
from ecwsp.sis.models import Student
from ecwsp.schedule.models import CourseEnrollment, CourseSection


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark


class GradebookSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSection


class GradebookStudentSerializer(serializers.ModelSerializer):
    gradebook_mark_set = MarkSerializer(many=True)
    # gradebook_mark_set = serializers.SerializerMethodField('get_items')

    class Meta:
        model = Student
        fields = ('first_name', 'last_name', 'gradebook_mark_set')

    # def get_items(self, obj):
    #     items = obj.gradebook_mark_set.filter(assignment__course_section=6)
    #     serializer = MarkSerializer(instance=items, many=True)
    #     return serializer.data


class GradebookEnrollmentSerializer(serializers.ModelSerializer):
    student = GradebookStudentSerializer()

    class Meta:
        model = CourseEnrollment
        fields = ('id', 'student')


class AssignmentSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment


class StudentMarkSerializer(serializers.ModelSerializer):
    enrollments = GradebookEnrollmentSerializer(many=True)
    assignment_set = AssignmentSetSerializer(many=True)

    id = serializers.SerializerMethodField()
    def get_id(self, obj):
        return obj.id

    class Meta:
        model = CourseSection
        fields = ('id', 'enrollments', 'assignment_set')


class AssignmentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentCategory


class AssignmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentType