from django.db.models import Q
from ecwsp.omr.models import *

class BenchmarkLookup(object):
    def get_query(self,q,request):
        result = Benchmark.objects.all()
        if request.session['omr_test_id']:
            test = Test.objects.get(id=request.session['omr_test_id'])
            if test.department:
                result = result.filter(measurement_topics__department=test.department)
        result = result.filter(Q(name__icontains=q) | Q(number__icontains=q))
        return result

    def format_result(self, object):
        return "%s %s" % (object.number, object.name)

    def format_item(self,object):
        return "%s %s" % (object.number, object.name)

    def get_objects(self,ids):
        return Benchmark.objects.filter(pk__in=ids).order_by('name')
        

class ThemeLookup(object):
    def get_query(self,q,request):
        result = Theme.objects.filter(Q(name__contains=q))
        return result

    def format_result(self, object):
        return "%s" % (object.name,)

    def format_item(self,object):
        return "%s" % (object.name,)

    def get_objects(self,ids):
        return Theme.objects.filter(pk__in=ids).order_by('name')