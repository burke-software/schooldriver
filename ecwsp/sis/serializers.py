from rest_framework import serializers
from .models import Student, SchoolYear


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student


class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYear
        depth = 1
        fields = ('id', 'name', 'start_date', 'end_date', 'active_year',
                  'markingperiod_set')
