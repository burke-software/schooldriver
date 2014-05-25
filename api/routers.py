from rest_framework import routers
from api.grades.views import GradeViewSet
from api.schedule.views import CourseViewSet

router = routers.DefaultRouter()
router.register(r'grades', GradeViewSet)
router.register(r'courses', CourseViewSet)
api_urls = router.urls
