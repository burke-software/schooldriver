from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from ecwsp.admissions.models import Applicant
from ecwsp.admissions.models import ApplicantCustomField
from ecwsp.admissions.models import StudentApplicationTemplate
from ecwsp.admissions.models import ApplicantAdditionalInformation
from ecwsp.admissions.models import ReligionChoice, EthnicityChoice, HeardAboutUsOption, FeederSchool
from api.admissions.serializers import ApplicantSerializer
from api.admissions.serializers import ApplicantCustomFieldSerializer
from api.admissions.serializers import StudentApplicationTemplateSerializer
from api.admissions.serializers import ApplicantAdditionalInformationSerializer
from api.admissions.serializers import EmergencyContactSerializer
from rest_framework_bulk import BulkCreateModelMixin
from api.admissions.permissions import ApplicantPermissions
from api.admissions.permissions import ApplicantTemplatePermissions
from ecwsp.sis.models import LanguageChoice, EmergencyContact, EmergencyContactNumber

class ApplicantViewSet(viewsets.ModelViewSet):

    permission_classes = (ApplicantPermissions,)
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer

    def post_save(self, ApplicantObject, created):
        if created:
            data = self.request.DATA
            if 'emergency_contacts' in data:
                for contact in data['emergency_contacts']:
                    try:
                        serializer = EmergencyContactSerializer(data=contact)
                        serializer.is_valid()
                        new_contact = serializer.object
                        new_contact.save()
                        ApplicantObject.parent_guardians.add(new_contact)
                        self.save_phone_numbers(new_contact, contact)
                    except Exception as e:
                        # this doens't actually do anything... need to trigger
                        # an API error...
                        return Response({"error":"error saving contact information"})

    def save_phone_numbers(self, EmergencyContactObject, contact_data):
        if 'home_phone' in contact_data:
            new_phone = EmergencyContactNumber()
            new_phone.type = 'H'
            new_phone.number = contact_data['home_phone']
            new_phone.contact = EmergencyContactObject
            new_phone.save()
        if 'work_phone' in contact_data:
            new_phone = EmergencyContactNumber()
            new_phone.type = 'W'
            new_phone.note = contact_data['employer']
            new_phone.number = contact_data['work_phone']
            new_phone.contact = EmergencyContactObject
            new_phone.save()

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

class ApplicantAdditionalInformationViewSet(viewsets.ModelViewSet):

    permission_classes = (ApplicantPermissions,)
    queryset = ApplicantAdditionalInformation.objects.all()
    serializer_class = ApplicantAdditionalInformationSerializer

    def get_serializer(self, *args, **kwargs):
        """ overriding the default behavior to support bulk create,
        for reference: stackoverflow.com/questions/27869841/how-to-post-put-json-data-to-listserializer/27871396#27871396 
        """
        if "data" in kwargs:
            data = kwargs["data"]
            if isinstance(data, list):
                kwargs["many"] = True
        return super(ApplicantAdditionalInformationViewSet, self).get_serializer(*args, **kwargs)

class ApplicantForeignKeyRelatedFieldChoicesViewSet(viewsets.ViewSet):

    def list(self, request):
        choiceMap = {
            "religion" : ReligionChoice,
            "family_preferred_language" : LanguageChoice,
            "ethnicity" : EthnicityChoice,
            "heard_about_us" : HeardAboutUsOption,
            "present_school" : FeederSchool,
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


