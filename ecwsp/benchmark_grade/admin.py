from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE

from ecwsp.benchmark_grade.models import *

admin.site.register(Scale)
admin.site.register(Mapping)
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Mark)
admin.site.register(Aggregate)