from constance import config
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext

import os
import requests
import re

from ecwsp.sis.models import Student
from ecwsp.sis.helper_functions import strip_unicode_to_ascii


@staff_member_required
def setup(request):
    if request.POST:
        sr = SchoolReach()
        result = sr.update_list()
        if result.status_code == 200:
            number_returned = result.text[result.text.find('recordCount')+12:result.text.find('recordCount')+16]
            messages.success(request, 'Success recordCount is %s' % number_returned)
        else:
            messages.error(request, '%s code recieved from server' % result.status_code)
    return render_to_response('schoolreach/setup.html', {
        'msg':'',
    }, RequestContext(request, {}),)

class SchoolReach:
    """ SchoolReach API integration
    """
    def update_list(self):
        """ We have to use a odd not quite soap based method. Using suds or
        other soap library will cause errors in some funcitons, probably
        Groupcast's fault. This xml was captured from intercepting
        xml sent by Groupcast's EZ data sync .NET app.
        """
        numbers = []
        exts = []
        fnames = []
        lnames = []
        emails = []
        m1s = []
        m2s = []
        m3s = []
        m4s = []
        m5s = []
        for student in Student.objects.filter(is_active=True):
            student_number = student.get_phone_number()
            if student_number:
                numbers += [student_number.number]
                exts += [student_number.ext]
                fnames += [student.first_name]
                lnames += [student.last_name]
                emails += [student.get_email]
                m1s += [student.year]
                m2s += [student.cache_cohort]
                if hasattr(student, 'studentworker') and student.studentworker:
                    m3s += [student.studentworker.day]
                else:
                    m3s += ['']
                m4s += ['Student']
                m5s += [student_number.type]
            ec = student.get_primary_emergency_contact()
            if ec:
                parent_numbers = []
                if ec.emergencycontactnumber_set.filter(type="H"):
                    parent_numbers += [ec.emergencycontactnumber_set.filter(type="H")[0]]
                if ec.emergencycontactnumber_set.filter(type="C"):
                    parent_numbers += [ec.emergencycontactnumber_set.filter(type="C")[0]]
                if ec.emergencycontactnumber_set.filter(type="W"):
                    parent_numbers += [ec.emergencycontactnumber_set.filter(type="W")[0]]
                if not parent_numbers and ec.emergencycontactnumber_set.all():
                    # Only include this is no phone types are set
                    parent_numbers +=[ec.emergencycontactnumber_set.all()[0]]
                for number in parent_numbers:
                    numbers += [number.number]
                    exts += [number.ext]
                    fnames += [ec.fname]
                    lnames += [ec.lname]
                    emails += ['']#[ec.email]
                    m1s += [student.year]
                    m2s += [student.cache_cohort]
                    if hasattr(student, 'studentworker') and student.studentworker:
                        m3s += [student.studentworker.day]
                    else:
                        m3s += ['']
                    m4s += [student]
                    m5s += [number.type]

        # Make data arrays into xml strings
        xml_numbers = ''
        for data_string in numbers:
            xml_numbers += '<num>%s</num>' % data_string
        xml_exts = ''
        for data_string in exts:
            if data_string == None:
                data_string = ''
            xml_exts += '<ext>%s</ext>' % re.sub("[^0-9]", "", data_string)
        xml_fnames= ''
        for data_string in fnames:
            xml_fnames += '<first>%s</first>' % strip_unicode_to_ascii(data_string)
        xml_lnames = ''
        for data_string in lnames:
            xml_lnames += '<last>%s</last>' % strip_unicode_to_ascii(data_string)
        xml_emails = ''
        for data_string in emails:
            xml_emails += '<email>%s</email>' % data_string
        xml_m1s = ''
        for data_string in m1s:
            xml_m1s += '<mField1>%s</mField1>' % strip_unicode_to_ascii(data_string)
        xml_m2s = ''
        for data_string in m2s:
            xml_m2s += '<mField2>%s</mField2>' % strip_unicode_to_ascii(data_string)
        xml_m3s = ''
        for data_string in m3s:
            xml_m3s += '<mField3>%s</mField3>' % strip_unicode_to_ascii(data_string)
        xml_m4s = ''
        for data_string in m4s:
            xml_m4s += '<mField4>%s</mField4>' % strip_unicode_to_ascii(data_string)
        xml_m5s = ''
        for data_string in m5s:
            xml_m5s += '<mField5>%s</mField5>' % strip_unicode_to_ascii(data_string)

        url = 'https://app.groupcast.com/WARP/GroupcastWARP.asmx?op=SetList&wsdl'
        xml_dict = {
            'userid': config.SCHOOLREACH_USERID,
            'pin': config.SCHOOLREACH_PIN,
            'list_id': config.SCHOOLREACH_LIST_ID,
            'xml_numbers': xml_numbers.replace("-", ""),
            'xml_exts': xml_exts,
            'xml_fnames': xml_fnames,
            'xml_lnames': xml_lnames,
            'xml_emails': xml_emails,
            'xml_m1s': xml_m1s,
            'xml_m2s': xml_m2s,
            'xml_m3s': xml_m3s,
            'xml_m4s': xml_m4s,
            'xml_m5s': xml_m5s,
        }
        xml = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body>
<setList2010 xmlns="https://app.groupcast.com/WARP/messages">
<appId>1</appId>
<verId>3.0.11</verId>
<userId>%(userid)s</userId>
<ownerPin>%(pin)s</ownerPin>
<affectedPin>%(pin)s</affectedPin>
<PhoneNumberArray>
%(xml_numbers)s
</PhoneNumberArray>
<Extension>
%(xml_exts)s
</Extension>
<FName>
%(xml_fnames)s
</FName>
<LName>
%(xml_lnames)s
</LName>
<EMail>
%(xml_emails)s
</EMail>
<MetaField1>
%(xml_m1s)s
</MetaField1>
<MetaField2>
%(xml_m2s)s
</MetaField2>
<MetaField3>
%(xml_m3s)s
</MetaField3>
<MetaField4>
%(xml_m4s)s
</MetaField4>
<MetaField5>
%(xml_m5s)s
</MetaField5>
<append>0</append>
<useShortCode>1</useShortCode>
<ListNumber>%(list_id)s</ListNumber>
<isIntl>0</isIntl></setList2010></soap:Body></soap:Envelope>""" % xml_dict
        header = {
            'SOAPAction': "app.GroupCast.com:setList2010In",
            'Content-Type': 'text/xml; charset=utf-8',
            'Expect': '100-continue',
            'Host': 'app.GroupCast.com',
        }
        result = requests.post(url, data=xml, headers=header)
        return result
