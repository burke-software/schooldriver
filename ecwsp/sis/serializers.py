from rest_framework import serializers
from .models import (
	Student, StudentNumber, SchoolYear, Cohort, EmergencyContact, 
	EmergencyContactNumber)


class CohortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cohort
        fields = ('id', 'name', 'long_name', 'primary')


class StudentNumberSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(
        source='get_type_display', read_only=True)

    class Meta:
        model = StudentNumber
        fields = ('id', 'number', 'ext', 'type_display', 'note')


class EmergencyContactNumberSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(
        source='get_type_display', read_only=True)
    
    class Meta:
        model = EmergencyContactNumber


class EmergencyContactSerializer(serializers.ModelSerializer):
    emergencycontactnumber_set = EmergencyContactNumberSerializer(many=True)

    class Meta:
        model = EmergencyContact


class StudentSerializer(serializers.ModelSerializer):
    cohorts = CohortSerializer(many=True)
    class_of_year = serializers.StringRelatedField()
    year = serializers.StringRelatedField()
    emergency_contacts = EmergencyContactSerializer(many=True)
    studentnumber_set = StudentNumberSerializer(many=True)
    sex_display = serializers.CharField(
        source='get_sex_display', read_only=True)

    class Meta:
        model = Student


class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYear
        depth = 1
        fields = ('id', 'name', 'start_date', 'end_date', 'active_year',
                  'markingperiod_set')
