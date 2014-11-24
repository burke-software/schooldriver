from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from ecwsp.admissions.models import Applicant
from ecwsp.admissions.models import ApplicantCustomField
from ecwsp.admissions.models import StudentApplicationTemplate
from ecwsp.admissions.models import ApplicantAdditionalInformation
from ecwsp.admissions.models import ReligionChoice, EthnicityChoice, HeardAboutUsOption
from api.admissions.serializers import ApplicantSerializer
from api.admissions.serializers import ApplicantCustomFieldSerializer
from api.admissions.serializers import StudentApplicationTemplateSerializer
from api.admissions.serializers import ApplicantAdditionalInformationSerializer
from api.admissions.serializers import EmergencyContactSerializer
from rest_framework_bulk import BulkCreateModelMixin
from api.admissions.permissions import ApplicantPermissions
from api.admissions.permissions import ApplicantTemplatePermissions
from ecwsp.sis.models import LanguageChoice, EmergencyContact
import json

class ApplicantViewSet(viewsets.ModelViewSet):

    permission_classes = (ApplicantPermissions,)
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer

    def post_save(self, obj, created):
        if created:
            data = self.request.DATA
            if 'emergency_contacts' in data:
                for contact in data['emergency_contacts']:
                    try:
                        serializer = EmergencyContactSerializer(data=contact)
                        serializer.is_valid()
                        new_contact = serializer.object
                        new_contact.save()
                        obj.parent_guardians.add(new_contact)
                    except Exception as e:
                        # this doens't actually do anything... need to trigger
                        # an API error...
                        return Response({"error":"error saving contact information"})


class EmergencyContactViewSet(viewsets.ModelViewSet):

    permission_classes = (ApplicantPermissions,)
    queryset = EmergencyContact.objects.all()
    serializer_class = EmergencyContactSerializer


class ApplicantCustomFieldViewSet(viewsets.ModelViewSet):

    permission_classes = (ApplicantTemplatePermissions, ) 
    queryset = ApplicantCustomField.objects.all()
    serializer_class = ApplicantCustomFieldSerializer

class ApplicationTemplateViewSet(viewsets.ModelViewSet):

    permission_classes = (ApplicantTemplatePermissions, ) 
    queryset = StudentApplicationTemplate.objects.all()
    serializer_class = StudentApplicationTemplateSerializer
    filter_fields = ('is_default',)

class ApplicantAdditionalInformationViewSet(viewsets.ModelViewSet, BulkCreateModelMixin):

    permission_classes = (ApplicantPermissions,)
    queryset = ApplicantAdditionalInformation.objects.all()
    serializer_class = ApplicantAdditionalInformationSerializer

class ApplicantForeignKeyRelatedFieldChoicesViewSet(viewsets.ViewSet):

    def list(self, request):
        choiceMap = {
            "religion" : ReligionChoice,
            "family_preferred_language" : LanguageChoice,
            "ethnicity" : EthnicityChoice,
            "heard_about_us" : HeardAboutUsOption,
        }
        data = {}

        for choiceKey, choiceModel in choiceMap.iteritems():
            data[choiceKey] = []
            for choice in choiceModel.objects.all():
                data[choiceKey].append({
                    "display_name":choice.name, 
                    "value":choice.id,
                    })
        
        return Response(data)


