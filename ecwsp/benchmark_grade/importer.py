#   Copyright 2011 Burke Software and Consulting LLC
#   Author: John Milner <john@tmoj.net>
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

from sis.importer import *
from ecwsp.benchmark_grade.models import *

class BenchmarkGradeImporter(Importer):
    def _is_empty(self, s):
        return len(unicode(s).strip()) == 0
        
    @transaction.commit_on_success
    def import_grades(self, course, marking_period):
        """ This is all completely hard-coded for the Twin Cities school. """
        mark_count = 0
        # as requested, drop all old marks before importing
        Aggregate.objects.filter(singleCourse=course).delete()
        for oldItem in Item.objects.filter(course=course, markingPeriod=marking_period):
            Mark.objects.filter(item=oldItem).delete()
            oldItem.delete()
        
        # import all data from the Standards sheet
        # should probably discard "Session" columns and calculate ourselves
        sheet = self.book.sheet_by_name('Standards')
        nrow = 5
        while nrow < sheet.nrows:
            username = unicode(sheet.cell_value(nrow, 1)).strip()
            if len(username) == 0:
                nrow += 1
                continue
            current_standard = ''
            ncol = 4
            while ncol < sheet.ncols and ncol < 105: # stop before the hidden formulas
                standard_name = unicode(sheet.cell_value(3, ncol)).strip()
                if len(standard_name) > 0:
                    current_standard = standard_name
                if self._is_empty(sheet.cell_value(nrow, ncol)):
                    ncol += 1
                    continue
                markVal = sheet.cell_value(nrow, ncol)
                mark_desc = unicode(sheet.cell_value(4, ncol)).strip()
                try:
                    category, trash = Category.objects.get_or_create(name="Standards")
                    item, trash = Item.objects.get_or_create(name=current_standard,
                                                             course=course, markingPeriod=marking_period, category=category,
                                                             scale=Scale.objects.get(name="Four-Oh"))
                    mark = Mark()
                    mark.item = item
                    mark.student = Student.objects.get(username=username)
                    mark.description = mark_desc
                    mark.mark = str(markVal) # then it will be happy to convert to Decimal
                    mark.save()
                    mark_count += 1
                except:
                    print >> sys.stderr, str(sys.exc_info())
                ncol += 1
            nrow += 1
                
        # import all data from the Engagement sheet

        sheet = self.book.sheet_by_name('Engagement')
        nrow = 4
        while nrow < sheet.nrows:
            username = unicode(sheet.cell_value(nrow, 1)).strip()
            if len(username) == 0:
                nrow += 1
                continue
            ncol = 3
            while ncol < sheet.ncols:
                if self._is_empty(sheet.cell_value(nrow, ncol)):
                    ncol += 1
                    continue
                markVal = sheet.cell_value(nrow, ncol)
                item_date = self.convert_date(sheet.cell_value(3, ncol))
                try:
                    category, trash = Category.objects.get_or_create(name="Engagement")
                    item, trash = Item.objects.get_or_create(name=str(item_date), date=item_date,
                                                             course=course, markingPeriod=marking_period, category=category,
                                                             scale=Scale.objects.get(name="Four-Oh"))
                    mark = Mark()
                    mark.item = item
                    mark.student = Student.objects.get(username=username)
                    mark.mark = str(markVal) # then it will be happy to convert to Decimal
                    mark.save()
                    mark_count += 1
                except:
                    print >> sys.stderr, str(sys.exc_info())
                ncol += 1
            nrow += 1

        # import all data from the Organization sheet

        sheet = self.book.sheet_by_name('Organization')
        nrow = 4
        while nrow < sheet.nrows:
            username = unicode(sheet.cell_value(nrow, 1)).strip()
            if len(username) == 0:
                nrow += 1
                continue
            ncol = 3
            while ncol < sheet.ncols:
                if self._is_empty(sheet.cell_value(nrow, ncol)):
                    ncol += 1
                    continue
                markVal = sheet.cell_value(nrow, ncol)
                item_date = self.convert_date(sheet.cell_value(3, ncol))
                try:
                    category, trash = Category.objects.get_or_create(name="Organization")
                    item, trash = Item.objects.get_or_create(name=str(item_date), date=item_date,
                                                             course=course, markingPeriod=marking_period, category=category,
                                                             scale=Scale.objects.get(name="Four-Oh"))
                    mark = Mark()
                    mark.item = item
                    mark.student = Student.objects.get(username=username)
                    mark.mark = str(markVal) # then it will be happy to convert to Decimal
                    mark.save()
                    mark_count += 1
                except:
                    print >> sys.stderr, str(sys.exc_info())
                ncol += 1
            nrow += 1
        
        # import all data from the Daily Practice sheet
        
        sheet = self.book.sheet_by_name('Daily Practice')
        nrow = 5
        while nrow < sheet.nrows:
            username = unicode(sheet.cell_value(nrow, 1)).strip()
            if len(username) == 0:
                nrow += 1
                continue
            ncol = 5
            while ncol < sheet.ncols and ncol < 37: # stop before "logic" cells
                if self._is_empty(sheet.cell_value(nrow, ncol)):
                    ncol += 1
                    continue
                markVal = sheet.cell_value(nrow, ncol)
                name = sheet.cell_value(3, ncol)
                try:
                    scale_max = Decimal(str(sheet.cell_value(4, ncol)))
                    category, trash = Category.objects.get_or_create(name="Daily Practice")
                    scale, trash = Scale.objects.get_or_create(name="Daily Practice " + str(scale_max), minimum=0, maximum=scale_max)
                    item, trash = Item.objects.get_or_create(name=name, scale=scale,
                                                             course=course, markingPeriod=marking_period, category=category)
                    mark = Mark()
                    mark.item = item
                    mark.student = Student.objects.get(username=username)
                    mark.mark = str(markVal) # then it will be happy to convert to Decimal
                    mark.save()
                    mark_count += 1
                except:
                    print >> sys.stderr, str(sys.exc_info())
                ncol += 1
            nrow += 1
        return mark_count
