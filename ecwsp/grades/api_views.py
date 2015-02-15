from rest_framework import filters, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    GradeSerializer, FinalGradeSerializer, SetGradeSerializer,
    SetFinalGradeSerializer)
from .models import Grade, FinalGrade


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.filter(
        enrollment__course_section__course__graded=True,
    )

    filter_backends = (filters.DjangoFilterBackend,)
    serializer_class = GradeSerializer
    filter_fields = ('enrollment__course_section',)


class FinalGradeViewSet(viewsets.ModelViewSet):
    queryset = FinalGrade.objects.filter(
        enrollment__course_section__course__graded=True,
    )
    serializer_class = FinalGradeSerializer
    filter_fields = ('enrollment__course_section',)


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


class SetFinalGradeView(APIView):
    def post(self, request, format=None):
        serializer = SetFinalGradeSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['student'] is None:
                FinalGrade.set_final_grade(
                    serializer.validated_data['enrollment'],
                    serializer.validated_data['grade'])
            else:
                FinalGrade.set_student_course_final_grade(
                    serializer.validated_data['student'],
                    serializer.validated_data['course_section'],
                    serializer.validated_data['grade'])
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
