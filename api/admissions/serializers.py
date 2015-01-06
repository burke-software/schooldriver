from ecwsp.admissions.models import (
    Applicant, ApplicantCustomField, StudentApplicationTemplate,
    ApplicantAdditionalInformation, ReligionChoice, EthnicityChoice,
    HeardAboutUsOption, FeederSchool)
from ecwsp.sis.models import Student
from rest_framework import serializers
from ecwsp.sis.models import EmergencyContact, LanguageChoice


class ApplicantAdditionalInformationSerializer(serializers.ModelSerializer):
    applicant = serializers.PrimaryKeyRelatedField(
        queryset=Applicant.objects.all())

    class Meta:
        model = ApplicantAdditionalInformation


class ApplicantSerializer(serializers.ModelSerializer):
    additionals = ApplicantAdditionalInformationSerializer(
        many=True, read_only=True)
    religion = serializers.PrimaryKeyRelatedField(
        queryset=ReligionChoice.objects.all(),
        required = False)
    ethnicity = serializers.PrimaryKeyRelatedField(
        queryset=EthnicityChoice.objects.all(),
        required = False)
    family_preferred_language = serializers.PrimaryKeyRelatedField(
        queryset=LanguageChoice.objects.all(),
        required = False)
    heard_about_us = serializers.PrimaryKeyRelatedField(
        queryset=HeardAboutUsOption.objects.all(),
        required = False)
    present_school = serializers.PrimaryKeyRelatedField(
        queryset=FeederSchool.objects.all(),
        required = False)
    siblings = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        required = False)

    class Meta:
        model = Applicant
        read_only_fields = ('id', 'unique_id')


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
