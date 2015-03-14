from rest_framework import routers
from api.schedule.views import CourseViewSet, SectionViewSet
from api.admissions.views import (
    ApplicantViewSet, ApplicantCustomFieldViewSet, ApplicationTemplateViewSet,
    ApplicantAdditionalInformationViewSet, EmergencyContactViewSet,
    ApplicantForeignKeyRelatedFieldChoicesViewSet)
from ecwsp.sis.api_views import StudentViewSet, SchoolYearViewSet
from ecwsp.grades.api_views import GradeViewSet, FinalGradeViewSet
from ecwsp.gradebook.api_views import AssignmentViewSet, MarkViewSet


router = routers.DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'school_years', SchoolYearViewSet)
router.register(r'grades', GradeViewSet)
router.register(r'final_grades', FinalGradeViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'marks', MarkViewSet)
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
