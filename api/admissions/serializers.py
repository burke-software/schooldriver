from ecwsp.admissions.models import Applicant
from ecwsp.admissions.models import ApplicantCustomField
from ecwsp.admissions.models import StudentApplicationTemplate
from ecwsp.admissions.models import ApplicantAdditionalInformation
from rest_framework import serializers
from ecwsp.sis.models import EmergencyContact


class ApplicantAdditionalInformationSerializer(serializers.ModelSerializer):
    applicant = serializers.PrimaryKeyRelatedField(
        queryset=Applicant.objects.all())

    class Meta:
        model = ApplicantAdditionalInformation

class ApplicantSerializer(serializers.ModelSerializer):
    additionals = ApplicantAdditionalInformationSerializer(many=True, required=False)

    class Meta:
        model = Applicant
        depth = 1

class ApplicantCustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantCustomField

class JSONFieldSerializer(serializers.Field):
    def to_representation(self, obj):
        return obj

class StudentApplicationTemplateSerializer(serializers.ModelSerializer):
    json_template = JSONFieldSerializer()
    class Meta:
        model = StudentApplicationTemplate

class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
