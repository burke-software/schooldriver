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

from ecwsp.sis.xlsReport import *
from ecwsp.omr.models import *

import xlwt

class ReportManager(object):
    def download_results(self, test):
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
        return report.finish()

report = ReportManager()
