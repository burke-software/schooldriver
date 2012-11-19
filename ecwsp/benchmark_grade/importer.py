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
                                                             points_possible=4)
                if categoryName == 'Standards':
                    #weakest = a.min(mark_description='Session')
                    weakest = a.min()
                    # A YTD for you if any of your standards are below 3.0
                    # except Hire4Ed gets a free pass
                    if weakest is not None and weakest < 3 and course.department.name != "Hire4Ed":
                        a.cached_value = 0 # better luck next time
                    else:
                        #a.cached_value = a.mean(mark_description='Session')
                        a.cached_value = a.mean()
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
        # now this has to be redone AGAIN to work with the Demonstration model
        #raise Exception('import_grades() under construction.')
        """ This is all completely hard-coded for the Twin Cities school. """
        mark_count = 0
        errors = []
        # as requested, drop all old marks before importing
        Aggregate.objects.filter(course=course, marking_period=marking_period).delete()
        Item.objects.filter(course=course, marking_period=marking_period).delete()

        # import all data from the Standards sheet
        # should probably discard "Session" columns and calculate ourselves
        # 20120821 jnm: really, we'll keep only "Session" and discard everything else
        # 20121114 jnm: NO, YOU FOOL!
        
        sheet = self.book.sheet_by_name('Standards')
        category = Category.objects.get(name='Standards')
        # 20120606 jnm: worksheets are now inconsistent. hidden formulas don't always start at column 105
        # 20120821 jnm: don't assume grades are contiguous. find the last Session column the hard way
        last_session_column = 0
        for ncol in range(4, sheet.ncols):
            if unicode(sheet.cell_value(4, ncol)).strip() == 'Session':
                last_session_column = ncol
        ncol = 4
        item = None
        item_has_marks = False
        while ncol <= last_session_column:
            standard_name = unicode(sheet.cell_value(3, ncol)).strip()
            if not item or len(standard_name):
                if item:
                   # it's not the first time through; see if there was anything valid for the Item that's just finished
                    if not item_has_marks:
                        mark_count -= item.mark_set.count()
                        item.mark_set.all().delete()
                        item.delete()
                # time for a new item!
                item = Item(name=standard_name,
                            course=course, marking_period=marking_period, category=category,
                            points_possible=4)
                item.save()
                item_has_marks = False
            demonstration_name = unicode(sheet.cell_value(4, ncol)).strip()
            if demonstration_name == 'Session':
                ncol += 1
                continue # sorry, we don't care about you
            demonstration_has_marks = False
            demonstration = Demonstration(name=demonstration_name, item=item)
            demonstration.save()
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
                    item_has_marks = True
                    demonstration_has_marks = True
                try:
                    mark = Mark()
                    mark.item = item
                    mark.demonstration = demonstration
                    try:
                        mark.student = Student.objects.get(username=username)
                    except Student.DoesNotExist:
                        if markVal == None:
                            # invalid student and no mark is okay; just skip it
                            nrow += 1
                            continue
                        else:
                            raise
                    mark.description = '___IMPORTED___'
                    mark.mark = markVal
                    mark.save()
                    mark_count += 1
                except Exception as e:
                    errors.append('<p><span style="color: red; font-weight: bold">ERROR</span> at sheet \'' + sheet.name + '\', cell ' + self._cell_name(nrow, ncol) + ', username \'' + username + '\': ' + str(e) + '</p>')
                nrow += 1
            if not demonstration_has_marks:
                # nothing valid for this Demonstration, so trash it
                mark_count -= demonstration.mark_set.count()
                demonstration.mark_set.all().delete()
                demonstration.delete() # we make 'em, we break 'em
            ncol += 1
        # check once more after the loop ends
        if not item_has_marks:
            mark_count -= item.mark_set.count()
            item.mark_set.all().delete()
            item.delete()

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
                    try:
                        mark.student = Student.objects.get(username=username)
                    except Student.DoesNotExist:
                        if markVal == None:
                            # invalid student and no mark is okay; just skip it
                            nrow += 1
                            continue
                        else:
                            raise
                    mark.mark = markVal
                    mark.save()
                    mark_count += 1
                except Exception as e:
                    errors.append('<p><span style="color: red; font-weight: bold">ERROR</span> at sheet \'' + sheet.name + '\', cell ' + self._cell_name(nrow, ncol) + ', username \'' + username + '\': ' + str(e) + '</p>')
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
                    try:
                        mark.student = Student.objects.get(username=username)
                    except Student.DoesNotExist:
                        if markVal == None:
                            # invalid student and no mark is okay; just skip it
                            nrow += 1
                            continue
                        else:
                            raise
                    mark.mark = markVal
                    mark.save()
                    mark_count += 1
                except Exception as e:
                    errors.append('<p><span style="color: red; font-weight: bold">ERROR</span> at sheet \'' + sheet.name + '\', cell ' + self._cell_name(nrow, ncol) + ', username \'' + username + '\': ' + str(e) + '</p>')
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
                        try:
                            mark.student = Student.objects.get(username=username)
                        except Student.DoesNotExist:
                            if markVal == None:
                                # invalid student and no mark is okay; just skip it
                                nrow += 1
                                continue
                            else:
                                raise
                        mark.mark = markVal
                        mark.save()
                        mark_count += 1
                    except Exception as e:
                        errors.append('<p><span style="color: red; font-weight: bold">ERROR</span> at sheet \'' + sheet.name + '\', cell ' + self._cell_name(nrow, ncol) + ', username \'' + username + '\': ' + str(e) + '</p>')
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
                        try:
                            mark.student = Student.objects.get(username=username)
                        except Student.DoesNotExist:
                            if markVal == None:
                                # invalid student and no mark is okay; just skip it
                                nrow += 1
                                continue
                            else:
                                raise
                        mark.mark = markVal
                        mark.save()
                        mark_count += 1
                    except Exception as e:
                        errors.append('<p><span style="color: red; font-weight: bold">ERROR</span> at sheet \'' + sheet.name + '\', cell ' + self._cell_name(nrow, ncol) + ', username \'' + username + '\': ' + str(e) + '</p>')
                    nrow += 1
                if not has_marks:
                    # nothing valid for this Item, so trash it
                    mark_count -= item.mark_set.count()
                    item.mark_set.all().delete()
                    item.delete() # we make 'em, we break 'em
                ncol += 1

        # YUCKY: Remove non-enrolled
        enrolled = course.get_enrolled_students(show_deleted=True)
        non_enrolled_count = 0
        for i in Item.objects.filter(course=course):
            delete_me = Mark.objects.filter(item=i).exclude(student__in=enrolled)
            non_enrolled_count += delete_me.count()
            delete_me.delete()

        # YUCKY: Fill holes
        filler_count = 0
        for s in enrolled:
            for i in Item.objects.filter(course=course):
                if i.demonstration_set.count():
                    for d in i.demonstration_set.all():
                        if not Mark.objects.filter(item=i, demonstration=d, student=s):
                            m = Mark(item=i, demonstration=d, student=s, description='___FILLER_AUTO___')
                            m.save()
                            filler_count += 1
                else:
                    if not Mark.objects.filter(item=i, student=s):
                        m = Mark(item=i, student=s, description='___FILLER_AUTO___')
                        m.save()
                        filler_count += 1


        # make aggregates for this course
        #self._make_aggregates(course, marking_period)
        
        output = '<p>{} marks were imported.</p>'.format(mark_count)
        if non_enrolled_count or filler_count:
            if non_enrolled_count:
                output += '<p>Ignored {} marks for students not enrolled in this course. This is okay.</p>'.format(non_enrolled_count)
            if filler_count:
                output += '<p>Added {} missing marks (set to None) to ensure one mark per student per item. This is okay.</p>'.format(filler_count)
        if len(errors):
            output += '<p>There were errors that may have prevented some data from importing!</p><ul style="font-size: smaller; list-style-type: disc; margin-left: 3em">'
            for e in errors:
                output += '<li>' + e + '</li>'
            output += '</ul>'
        return output
