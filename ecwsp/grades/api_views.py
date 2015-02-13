from rest_framework import filters, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .serializers import GradeSerializer
from .models import Grade


class GradeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = Grade.objects.filter(
        enrollment__course_section__course__graded=True,
    ).select_related(
    ).distinct()

    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    serializer_class = GradeSerializer
    filter_fields = ('enrollment__course_section',)
    ordering_fields = ('marking_period__start_date',)


class SetGradeView(APIView):
    def post(self, request, format=None):
        Grade.objects.get_or_create()
        request.data
        return Response()