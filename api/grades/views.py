from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework import filters
from ecwsp.grades.models import Grade
from ecwsp.schedule.models import CourseSection
from api.grades.serializers import GradeSerializer
from rest_framework_bulk.generics import ListBulkCreateUpdateDestroyAPIView
from rest_framework import mixins
from rest_framework_bulk.mixins import BulkCreateModelMixin, BulkUpdateModelMixin, BulkDestroyModelMixin

class ListBulkCreateUpdateDestroyViewSet(BulkCreateModelMixin,
                                BulkUpdateModelMixin,
                                BulkDestroyModelMixin,
                                viewsets.ModelViewSet):

    def update(self, request, *args, **kwargs):
        return self.bulk_update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.bulk_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.bulk_update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_bulk_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.bulk_destroy(request, *args, **kwargs)

class GradeViewSet(viewsets.ModelViewSet):
    """
    an API endpoint for the Grade model
    """
    permission_classes = (IsAdminUser,)
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    filter_fields = ('course', 'marking_period__school_year')

    def initial(self, request, *args, **kwargs):
        super(GradeViewSet, self).initial(request, *args, **kwargs)
        if 'course' in request.QUERY_PARAMS:
            """
            if 'course' is passed in the query params, make sure that
            every student has a grade for that course, even if it is null
            """
            try:
                section_id = request.QUERY_PARAMS['course']
                course_section = CourseSection.objects.get(id=section_id)
                if course_section:
                    course_section.populate_all_grades()
            except:
                pass


            
