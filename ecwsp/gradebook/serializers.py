from rest_framework import serializers
from .models import Assignment, Mark, AssignmentCategory, AssignmentType


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark


class AssignmentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentCategory


class AssignmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentType