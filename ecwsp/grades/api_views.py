from rest_framework import filters, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .serializers import GradeSerializer, SetGradeSerializer
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
        serializer = SetGradeSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['student'] is None:
                Grade.set_marking_period_grade(
                    serializer.validated_data['marking_period'],
                    serializer.validated_data['enrollment'],
                    serializer.validated_data['grade'])
            else:
                Grade.set_marking_period_student_course_grade(
                    serializer.validated_data['marking_period'],
                    serializer.validated_data['student'],
                    serializer.validated_data['course_section'],
                    serializer.validated_data['grade'])
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
