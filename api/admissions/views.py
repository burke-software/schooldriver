from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from ecwsp.admissions.models import Applicant
from ecwsp.admissions.models import ApplicantCustomField
from ecwsp.admissions.models import StudentApplicationTemplate
from ecwsp.admissions.models import ApplicantAdditionalInformation
from api.admissions.serializers import ApplicantSerializer
from api.admissions.serializers import ApplicantCustomFieldSerializer
from api.admissions.serializers import StudentApplicationTemplateSerializer
from api.admissions.serializers import ApplicantAdditionalInformationSerializer
from rest_framework_bulk import BulkCreateModelMixin

class ApplicantViewSet(viewsets.ModelViewSet):

    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer

class ApplicantCustomFieldViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAdminUser,)
    queryset = ApplicantCustomField.objects.all()
    serializer_class = ApplicantCustomFieldSerializer

class ApplicationTemplateViewSet(viewsets.ModelViewSet):

    queryset = StudentApplicationTemplate.objects.all()
    serializer_class = StudentApplicationTemplateSerializer

class ApplicantAdditionalInformationViewSet(viewsets.ModelViewSet, BulkCreateModelMixin):

    queryset = ApplicantAdditionalInformation.objects.all()
    serializer_class = ApplicantAdditionalInformationSerializer