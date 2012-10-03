#   Copyright 2011 David M Burke
#   Author David M Burke <david@burkesoftware.com>
#   
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#      
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

from django.contrib import admin

from ecwsp.sis.helper_functions import ReadPermissionModelAdmin
from ecwsp.benchmarks.models import Benchmark, MeasurementTopic, Department

class BenchmarkAdmin(ReadPermissionModelAdmin):
    list_display = ['number', 'name', 'display_measurement_topics']
    list_filter = ['measurement_topics','measurement_topics__department']
    search_fields = ['number', 'name','measurement_topics__name' ]
admin.site.register(Benchmark, BenchmarkAdmin)

class MeasurementTopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'department']
    list_filter = ['department']
    search_fields = ['department__name', 'name']
admin.site.register(MeasurementTopic,MeasurementTopicAdmin)

admin.site.register(Department)