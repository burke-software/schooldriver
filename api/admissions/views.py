from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from ecwsp.admissions.models import Applicant
from ecwsp.admissions.models import ApplicantCustomField
from ecwsp.admissions.models import StudentApplicationTemplate
from api.admissions.serializers import ApplicantSerializer
from api.admissions.serializers import ApplicantCustomFieldSerializer
from api.admissions.serializers import StudentApplicationTemplateSerializer

class ApplicantViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAdminUser,)
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer

class ApplicantCustomFieldViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAdminUser,)
    queryset = ApplicantCustomField.objects.all()
    serializer_class = ApplicantCustomFieldSerializer

class ApplicationTemplateViewSet(viewsets.ModelViewSet):

    queryset = StudentApplicationTemplate.objects.all()
    serializer_class = StudentApplicationTemplateSerializer

