from rest_framework import serializers
from .models import Assignment, Mark


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
