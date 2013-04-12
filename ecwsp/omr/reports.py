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
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Sum

from ecwsp.sis.report import *
from ecwsp.sis.helper_functions import Struct
from ecwsp.administration.models import Template
from ecwsp.omr.models import AnswerInstance
from ecwsp.benchmarks.models import Benchmark

import xlwt
from ecwsp.sis.xl_report import XlReport
from openpyxl.cell import get_column_letter

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
        i = 6
        for ti in test.testinstance_set.annotate(earned=Sum('answerinstance__points_earned')):
            data.append([ti.student, ti.earned, "=B%s / $B$2" % i])
            i += 1
        
        report = XlReport(file_name="OMR Report")
        report.add_sheet(data, title="Summary", auto_width=True)
        # Detail sheets
        data_points = []
        data_answers = []
        data_abc = []
        row_points = ["Student"]
        row_answers = ["Student"]
        row_abc = ["Student"]
        for i,question in enumerate(test.question_set.all()):
            row_points.append("%s %s" % (question.order, strip_tags(question.question).strip()))
            row_answers.append("%s %s" % (question.order, strip_tags(question.question).strip()))
            row_abc.append("Question {0}".format(i+1))
        data_points.append(row_points)
        data_answers.append(row_answers)
        data_abc.append(row_abc)
        
        for test_instance in test.testinstance_set.all():
            row_points = []
            row_answers = []
            row_abc = []
            row_points.append(test_instance.student)
            row_answers.append(test_instance.student)
            row_abc.append(test_instance.student)
            for question in test.question_set.all():
                try:
                    answer = test_instance.answerinstance_set.get(question=question)
                    row_points.append(answer.points_earned)
                    row_answers.append(strip_tags(answer.answer).strip())
                    i = None
                    if question.type == "True/False":
                        row_abc += [answer.answer]
                    else:
                        for i,x in enumerate(question.answer_set.all()):
                            if x == answer.answer:
                                break
                        row_abc += [chr(65+i)]
                except ObjectDoesNotExist:
                    row_points += ['']
                    row_answers += ['']
                    row_abc += ['']
            data_points.append(row_points)
            data_answers.append(row_answers)
            data_abc.append(row_abc)
        
        report.add_sheet(data_points, title="Detail Points", auto_width=True)
        report.add_sheet(data_answers, title="Detail Answers", auto_width=True)
        report.add_sheet(data_abc, title="Answer Sheet", auto_width=True)
        
        # Benchmark sheet
        data = []
        row = ['Benchmark']
        row2 = ['Points Possible']
        benchmarks = Benchmark.objects.filter(question__test=test).distinct()
        for benchmark in benchmarks:
            row.append(benchmark)
            row.append('%')
            row2.append(test.question_set.filter(benchmarks=benchmark).aggregate(Sum('point_value'))['point_value__sum'])
            row2.append('')
        data.append(row)
        data.append(row2)
        i = 3 # 3 for third row on spreadsheet
        for test_instance in test.testinstance_set.all():
            row = [test_instance.student]
            a = 2 # the letter c or column c in spreadsheet
            for benchmark in Benchmark.objects.filter(question__test=test).distinct():
                row.append(test_instance.answerinstance_set.filter(
                    question__benchmarks=benchmark).aggregate(
                    Sum('points_earned'))['points_earned__sum'])
                row.append('={0}{1}/{0}$2'.format(get_column_letter(a), str(i)))
                a += 2 # skip ahead 2 columns
            i += 1
            data.append(row)
        report.add_sheet(data, title="Benchmark", auto_width=True)
        
        data = [['Benchmark', 'Name', 'Earned', 'Possible', 'Percent']]
        i = 2
        for benchmark in benchmarks:
            row = []
            row += [benchmark.number, benchmark.name]
            answer_data = AnswerInstance.objects.filter(
                question__test=test,
                question__benchmarks=benchmark).aggregate(
                    Sum('points_earned'),
                    Sum('points_possible'))
            row += [answer_data['points_earned__sum']]
            row += [answer_data['points_possible__sum']]
            row += ['=C{0}/D{0}'.format(str(i))]
            data += [row]
        report.add_sheet(data, title="Benchmarks for class", auto_width=True)
        
        return report.as_download()
        
    def download_student_results(self, test, format, template):
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
                    incorrect.right_answer = incorrect.question.answer_set.order_by('point_value').reverse()[0]
                except:
                    incorrect.right_answer = "No correct answer"
            
        data['test'] = test
        data['tests'] = test_instances
        
        filename = 'Student Results for ' + unicode(test)
        return pod_save(filename, "." + str(format), data, template)  

report = ReportManager()
