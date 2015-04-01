from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .serializers import BenchmarkSerializer
from .models import Benchmark


class BenchmarkViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    serializer_class = BenchmarkSerializer
    queryset = Benchmark.objects.all()
