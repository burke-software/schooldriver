from django.conf import settings
import urllib, urllib2
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

def queXF(pdf,banding):
        register_openers()
        url = "http://localhost/trunk/admin/new.php"
        values = {'form':open(pdf, 'r'),
                  'bandingxml':open(banding, 'r')}
        data, headers = multipart_encode(values)
        headers['User-Agent'] = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        request = urllib2.Request(url, data, headers)
        request.unverifiable = True
        response = urllib2.urlopen(request)
        the_page = response.read()

#queXF()