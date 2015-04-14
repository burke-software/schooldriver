from rest_framework import routers
from api.schedule.views import (
	CourseViewSet, SectionViewSet, CourseEnrollmentViewSet)
from api.admissions.views import (
    ApplicantViewSet, ApplicantCustomFieldViewSet, ApplicationTemplateViewSet,
    ApplicantAdditionalInformationViewSet, EmergencyContactViewSet,
    ApplicantForeignKeyRelatedFieldChoicesViewSet)
from ecwsp.sis.api_views import StudentViewSet, SchoolYearViewSet
from ecwsp.grades.api_views import (
    GradeCommentViewSet, GradeViewSet, FinalGradeViewSet)
from ecwsp.gradebook.api_views import (
    AssignmentViewSet, MarkViewSet, AssignmentCategoryViewSet, 
    AssignmentTypeViewSet, StudentMarkViewSet)
from ecwsp.benchmarks.api_views import BenchmarkViewSet


router = routers.DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'school_years', SchoolYearViewSet)
router.register(r'grades', GradeViewSet)
router.register(r'grade_comments', GradeCommentViewSet)
router.register(r'final_grades', FinalGradeViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'enrollments', CourseEnrollmentViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'marks', MarkViewSet)
router.register(r'student_marks', StudentMarkViewSet)
router.register(r'assignment_categorys', AssignmentCategoryViewSet)
router.register(r'assignment_types', AssignmentTypeViewSet)
router.register(r'benchmarks', BenchmarkViewSet)
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
