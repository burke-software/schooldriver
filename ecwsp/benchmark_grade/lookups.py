from ecwsp.sis.lookups import StudentLookupSmall
from ecwsp.sis.models import Student
from ecwsp.schedule.models import Course
from django.db.models import Q
import logging

class ReferingCourseStudentLookup(StudentLookupSmall):
    # Why can't these people spell? http://en.wikipedia.org/wiki/HTTP_referer
    def get_query(self,q,request):
        course = None
        try:
            # Assume a "refering [sic]" URL whose last component is a course id, e.g.
            # http://moo.moo/grades/teacher_grade/upload/7
            course_id = long(str(request.META['HTTP_REFERER']).split('/')[-1])
            course = Course.objects.get(id=course_id)
        except:
            logging.warning('ReferingCourseStudentLookup failed to get a course from the HTTP referer. Students will not be filtered.', exc_info=True)
        if course is None:
            return super(ReferingCourseStudentLookup, self).get_query(q, request)
        else:
            qs = Student.objects.filter(courseenrollment__section=course)
        for word in q.split():
            qs = qs.filter(Q(lname__icontains=word) | Q(fname__icontains=word))
        return qs.order_by('lname')
