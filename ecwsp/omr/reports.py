#   Copyright 2011 Burke Software and Consulting LLC
#   Author David M Burke <david@burkesoftware.com>
#   
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from django.utils.html import strip_tags
from django.db.models import F

from ecwsp.sis.xlsReport import *
from ecwsp.sis.report import *
from ecwsp.sis.helper_functions import Struct
from ecwsp.administration.models import Template
from ecwsp.omr.models import *

import xlwt

class ReportManager(object):
    def download_results(self, test):
        """ Create basic xls report for OMR. Includes summary and details """
        
        # Summary sheet
        data = [[test.name]]
        data.append(["Points Possible:", test.points_possible])
        data.append(["Results collected: %s" % (test.students_test_results,)])
        data.append(['Test average: %s' % (test.points_average,)])
        data.append([])
        data.append(['Student', 'Points Earned', 'Percentage'])
        i = 7
        for ti in test.testinstance_set.annotate(earned=Sum('answerinstance__points_earned')):
            data.append([ti.student, ti.earned, xlwt.Formula("B%s / $B$2" % i)])
            i += 1
        #xlwt.Formula("B2")
        report = xlsReport(data, fileName="OMR report.xls", heading="Summary", heading_top=False)
        
        # Detail sheets
        data_points = []
        data_answers = []
        row_points = ["Student"]
        row_answers = ["Student"]
        for question in test.question_set.all():
            row_points.append("%s %s" % (question.order, strip_tags(question.question).strip()))
            row_answers.append("%s %s" % (question.order, strip_tags(question.question).strip()))
        data_points.append(row_points)
        data_answers.append(row_answers)
        
        for test_instance in test.testinstance_set.all():
            row_points = []
            row_answers = []
            row_points.append(test_instance.student)
            row_answers.append(test_instance.student)
            for question in test.question_set.all():
                try:
                    answer = test_instance.answerinstance_set.get(question=question)
                    row_points.append(answer.points_earned)
                    row_answers.append(strip_tags(answer.answer).strip())
                except:
                    row_points.append('')
                    row_answers.append('')
            data_points.append(row_points)
            data_answers.append(row_answers)
        
        report.addSheet(data_points, heading="Detail Points", heading_top=False)
        report.addSheet(data_answers, heading="Detail Answers", heading_top=False)
        
        # Benchmark sheet
        data = []
        row = ['Benchmark']
        row2 = ['Points Possible']
        for benchmark in Benchmark.objects.filter(question__test=test).distinct():
            row.append(benchmark)
            row.append('%')
            row2.append(test.question_set.filter(benchmarks=benchmark).aggregate(Sum('point_value'))['point_value__sum'])
            row2.append('')
        data.append(row)
        data.append(row2)
        i = 3 # 3 for third row on spreadsheet
        for test_instance in test.testinstance_set.all():
            row = [test_instance.student]
            a = 98 # the letter c or column c in spreadsheet
            for benchmark in Benchmark.objects.filter(question__test=test).distinct():
                row.append(test_instance.answerinstance_set.filter(question__benchmarks=benchmark).aggregate(Sum('points_earned'))['points_earned__sum'])
                row.append(xlwt.Formula(chr(a)+str(i)+'/'+chr(a)+'$2'))
                a += 2 # skip ahead 2 columns
            i += 1
            data.append(row)
        report.addSheet(data, heading="Benchmark", heading_top=False)
        
        return report.finish()
        
    def download_student_results(self, test, format):
        """ Make appy based report showing results for each student """
        data = get_default_data()
        
        test_instances = test.testinstance_set.all()
        benchmarks = Benchmark.objects.filter(question__test=test)
        
        for benchmark in benchmarks:
            benchmark.points_possible = test.question_set.filter(benchmarks=benchmark).aggregate(Sum('point_value'))['point_value__sum']
        
        for test_instance in test_instances:
            benchmark_instances = []
            for benchmark in benchmarks:
                benchmark_instance = Struct()
                benchmark_instance.benchmark = benchmark
                benchmark_instance.points_possible = benchmark.points_possible
                benchmark_instance.points_earned = test_instance.answerinstance_set.filter(question__benchmarks=benchmark).aggregate(Sum('points_earned'))['points_earned__sum']
                benchmark_instances.append(benchmark_instance)
            test_instance.benchmarks = benchmark_instances
        
            test_instance.incorrects = test_instance.answerinstance_set.filter(points_earned__lt=F('points_possible'))
            for incorrect in test_instance.incorrects:
                try:
                    incorrect.right_answer = incorrect.question.answer_set.order_by('points_possible')[0]
                except:
                    incorrect.right_answer = "No correct answer"
            
        
        template = Template.objects.get_or_create(name="OMR Student Test Result")[0].file
        data['test'] = test
        data['tests'] = test_instances
        
        filename = 'Student Results for ' + unicode(test)
        return pod_save(filename, "." + str(format), data, template)  

report = ReportManager()
