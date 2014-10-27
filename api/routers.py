from rest_framework import routers
from api.grades.views import GradeViewSet
from api.schedule.views import CourseViewSet, SectionViewSet
from api.admissions.views import ApplicantViewSet
from api.admissions.views import ApplicantCustomFieldViewSet
from api.admissions.views import ApplicationTemplateViewSet
from api.admissions.views import ApplicantAdditionalInformationViewSet

router = routers.DefaultRouter()
router.register(r'grades', GradeViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'applicant', ApplicantViewSet)
router.register(r'applicant-custom-field', ApplicantCustomFieldViewSet)
router.register(r'application-template', ApplicationTemplateViewSet )
router.register(r'applicant-additional-information', ApplicantAdditionalInformationViewSet )
api_urls = router.urls