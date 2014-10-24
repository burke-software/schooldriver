from ecwsp.admissions.models import Applicant
from ecwsp.admissions.models import ApplicantCustomField
from ecwsp.admissions.models import StudentApplicationTemplate
from rest_framework import serializers

class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant

class ApplicantCustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantCustomField

class JSONFieldSerializer(serializers.WritableField):
    def to_native(self, obj):
        return obj

class StudentApplicationTemplateSerializer(serializers.ModelSerializer):
    json_template = JSONFieldSerializer()
    class Meta:
        model = StudentApplicationTemplate