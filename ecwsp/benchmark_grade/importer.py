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

import logging
from ecwsp.sis.importer import *
from ecwsp.benchmark_grade.models import *
from ecwsp.grades.models import Grade

class BenchmarkGradeImporter(Importer):
    def _is_empty(self, s):
        return len(unicode(s).strip()) == 0

    def _cell_name(self, r, c):
        rownum = r + 1
        colnum = c + 1
        colname = ''
        while colnum > 26:
            if colnum % 26 == 0:
                colname = chr(65) + colname
            else:
                colname = chr(64 + colnum % 26) + colname
            colnum /= 26
        colname = chr(64 + colnum) + colname
        return colname + str(rownum)
        
    def _make_aggregates(self, course, marking_period):
        raise Exception('_make_aggregates(): under construction.')
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
                a, garbage = Aggregate.objects.get_or_create(student=student,
                                                             course=course,
                                                             marking_period=marking_period,
                                                             category=Category.objects.get(name=categoryName),
                                                             scale=Scale.objects.get(name=scaleName))
                if categoryName == 'Standards':
                    weakest = a.min(markDescription='Session')
                    # A YTD for you if any of your standards are below 3.0
                    # except Hire4Ed gets a free pass
                    if weakest is not None and weakest < 3 and course.department.name != "Hire4Ed":
                        a.cached_value = 0 # better luck next time
                    else:
                        a.cached_value = a.mean(markDescription='Session')
                    # I'd like to avoid re-writing SWORD
                    g, garbage = Grade.objects.get_or_create(student=student, course=course, marking_period=marking_period, override_final=False)
                    g.set_grade(a.cached_value)
                    g.save() # recalculates a bogus GPA every time. ouch.
                else:
                    a.cached_value = a.mean()
                a.name = unicode(a.cached_value) + u' - ' + unicode(student) + u' - ' + unicode(categoryName)  + u' (' + unicode(course.fullname) + u')'
                a.save()
        
    @transaction.commit_on_success
    def import_grades(self, course, marking_period):
        # this function really isn't stringent enough to work with the online gradebook
        # specifically, it doesn't ensure that for every course, there is one mark per student per item
        raise Exception('import_grades() under construction.')
        """ This is all completely hard-coded for the Twin Cities school. """
        mark_count = 0
        # as requested, drop all old marks before importing
        Aggregate.objects.filter(course=course, marking_period=marking_period).delete()
        Mark.objects.filter(item__course=course, item__marking_period=marking_period).delete()

        # import all data from the Standards sheet
        # should probably discard "Session" columns and calculate ourselves
        # 20120821 jnm: really, we'll keep only "Session" and discard everything else
        
        sheet = self.book.sheet_by_name('Standards')
        category = Category.objects.get(name='Standards')
        # 20120606 jnm: worksheets are now inconsistent. hidden formulas don't always start at column 105
        # 20120821 jnm: don't assume grades are contiguous. find the last Session column the hard way
        last_session_column = 0
        for ncol in range(4, sheet.ncols):
            if unicode(sheet.cell_value(4, ncol)).strip() == 'Session':
                last_session_column = ncol
        ncol = 4
        while ncol <= last_session_column:
            mark_desc = unicode(sheet.cell_value(4, ncol)).strip()
            if mark_desc != 'Session':
                ncol += 1
                continue # sorry, we don't care about you
            # Make a new Item for every column!
            standard_name = unicode(sheet.cell_value(3, ncol - 4)).strip()
            item = Item(name=standard_name,
                        course=course, marking_period=marking_period, category=category,
                        points_possible=4)
            item.save()
            has_marks = False
            nrow = 5
            while nrow < sheet.nrows:
                username = unicode(sheet.cell_value(nrow, 1)).strip()
                if len(username) == 0:
                    nrow += 1
                    continue
                if self._is_empty(sheet.cell_value(nrow, ncol)):
                    markVal = None
                else:
                    markVal = sheet.cell_value(nrow, ncol)
                    has_marks = True
                try:
                    mark = Mark()
                    mark.item = item
                    mark.student = Student.objects.get(username=username)
                    mark.description = mark_desc
                    mark.mark = markVal
                    mark.save()
                    mark_count += 1
                except Exception as e:
                    return '<p><span style="color: red; font-weight: bold">ERROR:</span> There was a problem with the ' + sheet.name + ' sheet at cell ' + self._cell_name(nrow, ncol) + ': ' + str(e) + '</p>'
                nrow += 1
            if not has_marks:
                # nothing valid for this Item, so trash it
                mark_count -= item.mark_set.count()
                item.mark_set.all().delete()
                item.delete() # we make 'em, we break 'em
            ncol += 1

        # import all data from the Engagement sheet

        sheet = self.book.sheet_by_name('Engagement')
        category = Category.objects.get(name='Engagement')
        ncol = 3
        while ncol < sheet.ncols:
            name = sheet.cell_value(3, ncol)
            item_date = self.convert_date(name)
            if item_date is not None:
                name = str(item_date) # why am I doing this? standardization?
            item = Item(name=name, date=item_date,
                        course=course, marking_period=marking_period, category=category,
                        points_possible=4)
            item.save()
            has_marks = False
            nrow = 4
            while nrow < sheet.nrows:
                username = unicode(sheet.cell_value(nrow, 1)).strip()
                if len(username) == 0:
                    nrow += 1
                    continue
                if self._is_empty(sheet.cell_value(nrow, ncol)):
                    markVal = None
                else:
                    markVal = sheet.cell_value(nrow, ncol)
                    has_marks = True
                try:
                    mark = Mark()
                    mark.item = item
                    mark.student = Student.objects.get(username=username)
                    mark.mark = markVal
                    mark.save()
                    mark_count += 1
                except Exception as e:
                    return '<p><span style="color: red; font-weight: bold">ERROR:</span> There was a problem with the ' + sheet.name + ' sheet at cell ' + self._cell_name(nrow, ncol) + ': ' + str(e) + '</p>'
                nrow += 1
            if not has_marks:
                # nothing valid for this Item, so trash it
                mark_count -= item.mark_set.count()
                item.mark_set.all().delete()
                item.delete() # we make 'em, we break 'em
            ncol += 1

        # import all data from the Organization sheet

        sheet = self.book.sheet_by_name('Organization')
        category = Category.objects.get(name='Organization')
        ncol = 3
        while ncol < sheet.ncols:
            name = sheet.cell_value(3, ncol)
            item_date = self.convert_date(name)
            if item_date is not None:
                name = str(item_date) # why am I doing this? standardization?
            item = Item(name=name, date=item_date,
                        course=course, marking_period=marking_period, category=category,
                        points_possible=4)
            item.save()
            has_marks = False
            nrow = 4
            while nrow < sheet.nrows:
                username = unicode(sheet.cell_value(nrow, 1)).strip()
                if len(username) == 0:
                    nrow += 1
                    continue
                if self._is_empty(sheet.cell_value(nrow, ncol)):
                    markVal = None
                else:
                    markVal = sheet.cell_value(nrow, ncol)
                    has_marks = True
                try:
                    mark = Mark()
                    mark.item = item
                    mark.student = Student.objects.get(username=username)
                    mark.mark = markVal
                    mark.save()
                    mark_count += 1
                except Exception as e:
                    return '<p><span style="color: red; font-weight: bold">ERROR:</span> There was a problem with the ' + sheet.name + ' sheet at cell ' + self._cell_name(nrow, ncol) + ': ' + str(e) + '</p>'
                nrow += 1
            if not has_marks:
                # nothing valid for this Item, so trash it
                mark_count -= item.mark_set.count()
                item.mark_set.all().delete()
                item.delete() # we make 'em, we break 'em
            ncol += 1
        
        # import all data from the Daily Practice sheet
        if course.department.name != 'Hire4Ed':
            sheet = self.book.sheet_by_name('Daily Practice')
            category = Category.objects.get(name='Daily Practice')
            ncol = 5
            while ncol < sheet.ncols and ncol < 37: # stop before "logic" cells
                name = sheet.cell_value(3, ncol)
                item_date = self.convert_date(name)
                if item_date is not None:
                    name = str(item_date) # why am I doing this? standardization?
                points_possible = unicode(sheet.cell_value(4, ncol)).strip()
                if not len(points_possible):
                    ncol += 1
                    continue
                item = Item(name=name, date=item_date,
                            course=course, marking_period=marking_period, category=category,
                            points_possible=points_possible)
                item.save()
                has_marks = False
                nrow = 5
                while nrow < sheet.nrows:
                    username = unicode(sheet.cell_value(nrow, 1)).strip()
                    if len(username) == 0:
                        nrow += 1
                        continue
                    if self._is_empty(sheet.cell_value(nrow, ncol)):
                        markVal = None
                    else:
                        markVal = sheet.cell_value(nrow, ncol)
                        has_marks = True
                    try:
                        mark = Mark()
                        mark.item = item
                        mark.student = Student.objects.get(username=username)
                        mark.mark = markVal
                        mark.save()
                        mark_count += 1
                    except Exception as e:
                        return '<p><span style="color: red; font-weight: bold">ERROR:</span> There was a problem with the ' + sheet.name + ' sheet at cell ' + self._cell_name(nrow, ncol) + ': ' + str(e) + '</p>'
                    nrow += 1
                if not has_marks:
                    # nothing valid for this Item, so trash it
                    mark_count -= item.mark_set.count()
                    item.mark_set.all().delete()
                    item.delete() # we make 'em, we break 'em
                ncol += 1
        
        #import all data from the Precision and Accuracy sheet
        if course.department.name == 'Hire4Ed':
            sheet = self.book.sheet_by_name('Precision and Accuracy')
            category = Category.objects.get(name='Precision and Accuracy')
            ncol = 3
            while ncol < sheet.ncols:
                name = sheet.cell_value(3, ncol)
                item_date = self.convert_date(name)
                if item_date is not None:
                    name = str(item_date) # why am I doing this? standardization?
                item = Item(name=name, date=item_date,
                            course=course, marking_period=marking_period, category=category,
                            points_possible=4)
                item.save()
                has_marks = False
                nrow = 4
                while nrow < sheet.nrows:
                    username = unicode(sheet.cell_value(nrow, 1)).strip()
                    if len(username) == 0:
                        nrow += 1
                        continue
                    if self._is_empty(sheet.cell_value(nrow, ncol)):
                        markVal = None
                    else:
                        markVal = sheet.cell_value(nrow, ncol)
                        has_marks = True
                    try:
                        mark = Mark()
                        mark.item = item
                        mark.student = Student.objects.get(username=username)
                        mark.mark = markVal
                        mark.save()
                        mark_count += 1
                    except Exception as e:
                        return '<p><span style="color: red; font-weight: bold">ERROR:</span> There was a problem with the ' + sheet.name + ' sheet at cell ' + self._cell_name(nrow, ncol) + ': ' + str(e) + '</p>'
                    nrow += 1
                if not has_marks:
                    # nothing valid for this Item, so trash it
                    mark_count -= item.mark_set.count()
                    item.mark_set.all().delete()
                    item.delete() # we make 'em, we break 'em
                ncol += 1
            
        # make aggregates for this course
        #self._make_aggregates(course, marking_period)
        
        return 'OK! ' + str(mark_count) + ' marks imported.'
