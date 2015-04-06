from rest_framework import serializers
from .models import Student, StudentNumber, SchoolYear, Cohort


class CohortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cohort
        fields = ('id', 'name', 'long_name', 'primary')


class StudentNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentNumber


class StudentSerializer(serializers.ModelSerializer):
    cohorts = CohortSerializer(many=True)
    class_of_year = serializers.StringRelatedField()
    year = serializers.StringRelatedField()
    # student_numbers = StudentNumberSerializer(many=True)

    class Meta:
        model = Student


class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYear
        depth = 1
        fields = ('id', 'name', 'start_date', 'end_date', 'active_year',
                  'markingperiod_set')
