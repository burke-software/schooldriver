from rest_framework import serializers
from .models import Benchmark


class BenchmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benchmark
