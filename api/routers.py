from rest_framework import routers
from api.grades.views import GradeViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'grades', GradeViewSet)
