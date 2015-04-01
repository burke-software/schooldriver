from rest_framework import viewsets
from .serializers import BenchmarkSerializer
from .models import Benchmark


class BenchmarkViewSet(viewsets.ModelViewSet):
    serializer_class = BenchmarkSerializer
    queryset = Benchmark.objects.all()
