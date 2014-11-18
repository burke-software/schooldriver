from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from ecwsp.admissions.models import Applicant
from ecwsp.admissions.models import ApplicantCustomField
from ecwsp.admissions.models import StudentApplicationTemplate
from ecwsp.admissions.models import ApplicantAdditionalInformation
from ecwsp.admissions.models import ReligionChoice, EthnicityChoice
from api.admissions.serializers import ApplicantSerializer
from api.admissions.serializers import ApplicantCustomFieldSerializer
from api.admissions.serializers import StudentApplicationTemplateSerializer
from api.admissions.serializers import ApplicantAdditionalInformationSerializer
from rest_framework_bulk import BulkCreateModelMixin
from api.admissions.permissions import ApplicantPermissions
from api.admissions.permissions import ApplicantTemplatePermissions
from ecwsp.sis.models import LanguageChoice

class ApplicantViewSet(viewsets.ModelViewSet):

    permission_classes = (ApplicantPermissions,)
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer

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
            "ethnicity" : EthnicityChoice
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


