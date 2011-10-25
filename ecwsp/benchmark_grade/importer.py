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
    @transaction.commit_on_success
    def import_grades(self, course, marking_period):
        # as requested, drop all old marks before importing
        Aggregate.objects.filter(singleCourse=course).delete()
        for oldItem in Item.objects.filter(course=course):
            Mark.objects.filter(item=oldItem).delete()
            oldItem.delete()
        # the sheet is protected; let's not worry about being tolerant of whitespace, capitalization, etc.
        sheet = self.book.sheet_by_name(u'SUMMARY')
        # some error handling here?
        x = 0
        # find the header
        while x < sheet.nrows and sheet.cell(x, 0).value != u'Last Name':
            x += 1
        header = sheet.row(x)
        x += 1
        while x < sheet.nrows:
            try: # burkeh!
                # to do: check that kiddie is actually enrolled in the course
                username = str(sheet.cell(x, 1).value).strip()
                # some username cells below the last student have number:0.0 instead of text:u''
                if len(username) == 0 or str(sheet.cell(x, 1)) == 'number:0.0':
                    x += 1
                    continue
                y = 2
                while y < sheet.ncols:
                    '''
                    0  text:u'Last Name'
                    1  text:u'First Name'
                    2  text:u'Standards'
                    3  text:u'Engagement'
                    4  text:u'Organization'
                    5  text:u'Daily Practice'
                    6- Individual Standards
                    '''
#                    print >> sys.stderr, "Looking at (" + str(x), ", " + str(y) + "): " + unicode(sheet.cell(x, y))
                    mark = str(sheet.cell(x, y).value).strip()
                    # formulas that evaluate to nothing unpredictably return text:u'' or number:0.0
                    if len(mark) == 0:
                        y += 1
                        continue
                    # a standard would never appear as zero, so these are empty cells.
                    # who knows about the other categories?
                    if (y == 2 or y >= 6) and str(sheet.cell(x, y)) == 'number:0.0':
#                        print >> sys.stderr, "Discarding impossible zero value in Standards column " + str(y)
                        y += 1
                        continue
#                    print >> sys.stderr, username + " got a " + mark + " on " + header[y].value
                    # there should be a model for these types of substitutions.
                    if mark == "YTD":
                        mark = 0
                    else:
                        mark = Decimal(mark)
                    category = name = scale = None
                    # really, 2-5 should be aggregates, but this is all hackery anyway.
                    if y == 2:
                        category = name = "Standards"
                        scale = Scale.objects.get(name="Four-Oh with YTD")
                    if y == 3:
                        category = name = "Engagement"
                        scale = Scale.objects.get(name="Four-Oh")
                    if y == 4:
                        category = name = "Organization"
                        scale = Scale.objects.get(name="Four-Oh")
                    if y == 5:
                        if course.department is not None and course.department.name == "Hire4Ed":
                            category = name = "Precision & Accuracy"
                            scale = Scale.objects.get(name="Four-Oh")
                        else:
                            category = name = "Daily Practice"
                            scale = Scale.objects.get(name="Percent")
                            # 0 <= % <= 1 formatting seems undetectable by xlrd
                            # https://secure.simplistix.co.uk/svn/xlrd/trunk/xlrd/doc/xlrd.html#formatting.Format.type-attribute
                            mark *= 100 # BADNESS
                    if y >= 6:
                        category = "Standards"
                        name = str(header[y].value).strip()
                        scale = Scale.objects.get(name="Four-Oh with YTD")
                        itemModel, itemCreated = Item.objects.get_or_create(name=name,
                                                                            course=course,
                                                                            category=Category.objects.get(name=category),
                                                                            scale=scale)
                        markModel, markCreated = Mark.objects.get_or_create(item=itemModel,
                                                                            student=Student.objects.get(username=username))
                        markModel.mark = mark
                        itemModel.save()
                        markModel.save()
                        self.log_and_commit(itemModel, addition=itemCreated)
                        self.log_and_commit(markModel, addition=markModel)
                    else:
                        aggModel, aggCreated = Aggregate.objects.get_or_create(name=name,
                                                                               scale=scale,
                                                                               singleStudent=Student.objects.get(username=username),
                                                                               singleCourse=course,
                                                                               singleCategory=Category.objects.get(name=category))
                        aggModel.manualMark = mark
                        aggModel.save()
                        self.log_and_commit(aggModel, addition=aggCreated)
                    y += 1
            except:
                print >> sys.stderr, str(sys.exc_info())
            x += 1
        '''
        sheet = self.book.sheet_by_name(marking_period.name)
        x = 0
        header = sheet.row(x)
        x += 2 # skip second row
        while x < sheet.nrows:
            try:
                row = sheet.row(x)
                items = zip(header, row)
                created = False
                model = None
                grade = None
                comment = ""
                del_comments = False
                for (name, value) in items:
                    is_ok, name, value = self.sanitize_item(name, value)
                    if is_ok:
                        if name == "username":
                            student = Student.objects.get(username=value)
                            model, created = Grade.objects.get_or_create(student=student, course=course, marking_period=marking_period, final=True)
                        elif name == "final grade %" or name == 'marking period grade (%)':
                            grade = value
                        elif name == "comment code" or name == "comment codes" or name == "comment\ncodes":
                            value = unicode.lower(unicode(value))
                            for cc in value.split(','):
                                try:
                                    comment += unicode(GradeComment.objects.get(id=int(float(str(cc)))).comment) + " "
                                except:
                                    comment += unicode(cc) + " IS NOT VALID COMMENT CODE! "
                            value = unicode.lower(value)
                            if value.strip() == "none":
                                del_comments = True
                        elif name == "comment":
                            comment = unicode(value) + " "
                            if value.strip() == "none":
                                del_comments = True
                if model and grade:
                    model.set_grade(grade)
                    model.save()
                    self.log_and_commit(model, addition=False)
                if model and comment:
                    model.comment = comment
                    model.save()
                if model and del_comments:
                    model.comment = ""
                    model.save()
            except:
                print >> sys.stderr, str(sys.exc_info())
            x += 1
            '''
