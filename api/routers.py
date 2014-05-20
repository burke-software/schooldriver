from rest_framework import routers
from api.grades.views import GradeViewSet

router = routers.DefaultRouter()
router.register(r'grades', GradeViewSet)
api_urls = router.urls
