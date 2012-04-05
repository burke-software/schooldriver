#       Copyright 2010-2011 Burke Software and Consulting LLC
#       Author David M Burke <david@burkesoftware.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from django.contrib import admin

from ajax_select import make_ajax_form

from models import *

class DisciplineActionInstanceInline(admin.TabularInline):
    model = DisciplineActionInstance
    extra = 1
    
class StudentDisciplineAdmin(admin.ModelAdmin):
    form = make_ajax_form(StudentDiscipline, dict(students='discstudent'))

    list_per_page = 50
    fields = ['date', 'students', 'teacher', 'infraction', 'comments']
    list_display = ('show_students', 'date', 'comment_Brief', 'infraction')
    list_filter = ['date', 'infraction', 'action',]
    search_fields = ['comments', 'students__fname', 'students__lname']
    inlines = [DisciplineActionInstanceInline]

admin.site.register(StudentDiscipline, StudentDisciplineAdmin)
admin.site.register(DisciplineAction)
admin.site.register(Infraction)