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
from ecwsp.grades.models import Grade

class BenchmarkGradeImporter(Importer):
    def _is_empty(self, s):
        return len(unicode(s).strip()) == 0
        
    def _make_aggregates(self, course, marking_period):
        # clear out schedule grades; they'll be copied from the standards averages
        Grade.objects.filter(course=course, marking_period=marking_period).delete()
        
        category_scale = {'Standards': 'Four-Oh with YTD',
                          'Engagement': 'Four-Oh',
                          'Organization': 'Four-Oh'}
        if course.department.name == "Hire4Ed":
            category_scale['Standards'] = 'Four-Oh'
            category_scale['Precision and Accuracy'] = 'Four-Oh'
        else:
            category_scale['Daily Practice'] = 'Percent'
        for student in course.get_enrolled_students(show_deleted=True):
            for categoryName, scaleName in category_scale.iteritems():
                a, garbage = Aggregate.objects.get_or_create(singleStudent=student,
                                                             singleCourse=course,
                                                             singleMarkingPeriod=marking_period,
                                                             singleCategory=Category.objects.get(name=categoryName),
                                                             scale=Scale.objects.get(name=scaleName))
                if categoryName == 'Standards':
                    weakest = a.min(markDescription='Session')
                    # A YTD for you if any of your standards are below 3.0
                    # except Hire4Ed gets a free pass
                    if weakest is not None and weakest < 3 and course.department.name != "Hire4Ed":
                        a.cachedValue = 0 # better luck next time
                    else:
                        a.cachedValue = a.mean(markDescription='Session')
                    # I'd like to avoid re-writing SWORD
                    g, garbage = Grade.objects.get_or_create(student=student, course=course, marking_period=marking_period, override_final=False)
                    g.set_grade(a.cachedValue)
                    g.save() # recalculates a bogus GPA every time. ouch.
                else:
                    a.cachedValue = a.mean()
                a.name = unicode(a.cachedValue) + u' - ' + unicode(student) + u' - ' + unicode(categoryName)  + u' (' + unicode(course.fullname) + u')'
                a.save()
        
    @transaction.commit_on_success
    def import_grades(self, course, marking_period):
        """ This is all completely hard-coded for the Twin Cities school. """
        mark_count = 0
        # as requested, drop all old marks before importing
        Aggregate.objects.filter(singleCourse=course, singleMarkingPeriod=marking_period).delete()
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
                name = sheet.cell_value(3, ncol)
                item_date = self.convert_date(name)
                if item_date is not None:
                    name = str(item_date) # why am I doing this? standardization?
                try:
                    category, trash = Category.objects.get_or_create(name="Engagement")
                    item, trash = Item.objects.get_or_create(name=name, date=item_date,
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
                name = sheet.cell_value(3, ncol)
                item_date = self.convert_date(name)
                if item_date is not None:
                    name = str(item_date) # why am I doing this? standardization?
                try:
                    category, trash = Category.objects.get_or_create(name="Organization")
                    item, trash = Item.objects.get_or_create(name=name, date=item_date,
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
        if course.department.name != 'Hire4Ed':
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
        
        #import all data from the Precision and Accuracy sheet
        if course.department.name == 'Hire4Ed':
            sheet = self.book.sheet_by_name('Precision and Accuracy')
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
                    name = sheet.cell_value(3, ncol)
                    try:
                        category, trash = Category.objects.get_or_create(name="Precision and Accuracy")
                        item, trash = Item.objects.get_or_create(name=name, course=course, markingPeriod=marking_period, category=category,
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
            
        # make aggregates for this course
        self._make_aggregates(course, marking_period)
        
        return mark_count
