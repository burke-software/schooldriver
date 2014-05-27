import autocomplete_light
from .models import Benchmark

class BenchmarkAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['number', 'name']

autocomplete_light.register(Benchmark, BenchmarkAutocomplete)
