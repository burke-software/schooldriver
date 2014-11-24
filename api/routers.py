from rest_framework import routers
from api.grades.views import GradeViewSet
from api.schedule.views import CourseViewSet, SectionViewSet
from api.admissions.views import ApplicantViewSet
from api.admissions.views import ApplicantCustomFieldViewSet
from api.admissions.views import ApplicationTemplateViewSet
from api.admissions.views import ApplicantAdditionalInformationViewSet
from api.admissions.views import EmergencyContactViewSet
from api.admissions.views import ApplicantForeignKeyRelatedFieldChoicesViewSet
from api.translations.views import AdmissionsTranslationViewSet
from api.translations.views import AdmissionsTranslationSync

router = routers.DefaultRouter()
router.register(r'grades', GradeViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'translations/admissions', AdmissionsTranslationViewSet, base_name='admissions-translations')
router.register(r'translations/admissions/sync', AdmissionsTranslationSync, base_name='admissions-translations-sync')
router.register(r'sections', SectionViewSet)
router.register(r'applicant', ApplicantViewSet)
router.register(r'applicant-custom-field', ApplicantCustomFieldViewSet)
router.register(r'application-template', ApplicationTemplateViewSet )
router.register(r'emergency-contact', EmergencyContactViewSet)
router.register(r'applicant-additional-information', ApplicantAdditionalInformationViewSet )
router.register(r'applicant-foreign-key-field-choices', 
    ApplicantForeignKeyRelatedFieldChoicesViewSet, 
    base_name='applicant-foreign-key-field-choices'
    )
api_urls = router.urls