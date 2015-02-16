from rest_framework import serializers
from .models import MarkingPeriod


class MarkingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkingPeriod
