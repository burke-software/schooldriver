
from django.test import TestCase
from django.test import Client
from django import template
from django.db.models import get_model

class Testmaker(TestCase):

    #fixtures = ["schedule_testmaker"]


    def test__129770082675(self):
        r = self.client.get('/', {})
        self.assertEqual(r.status_code, 302)
    def test_accountslogin_129770082719(self):
        r = self.client.get('/accounts/login/', {'next': '/', })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['site_name']), u'testserver')
        self.assertEqual(unicode(r.context[-1]['site']), u'testserver')
        self.assertEqual(unicode(r.context[-1]['form']), u'<tr><th><label for="id_username">Username:</label></th><td><input id="id_username" type="text" name="username" maxlength="30" /></td></tr>
<tr><th><label for="id_password">Password:</label></th><td><input type="password" name="password" id="id_password" /></td></tr>')
        self.assertEqual(unicode(r.context[-1]['next']), u'/')
    def test_staticimagesdjangomade124x25_greygif_129770082746(self):
        r = self.client.get('/static/images/djangomade124x25_grey.gif', {})
        self.assertEqual(r.status_code, 404)
    def test_faviconico_129770082755(self):
        r = self.client.get('/favicon.ico', {})
        self.assertEqual(r.status_code, 404)
    def test_accountslogin_129770083116(self):
        r = self.client.post('/accounts/login/', {'username': 'aa', 'csrfmiddlewaretoken': '3468ae7be584b59d9b8dcebff93078ee', 'password': 'aa', 'next': '/', })
    def test__129770083119(self):
        r = self.client.get('/', {})
        self.assertEqual(r.status_code, 302)
    def test_staticimagesheaderjpg_129770083124(self):
        r = self.client.get('/static/images/header.jpg', {})
        self.assertEqual(r.status_code, 200)
    def test_staticimagesgradient_lightjpg_129770083127(self):
        r = self.client.get('/static/images/gradient_light.jpg', {})
        self.assertEqual(r.status_code, 200)
    def test_staticimagesdjangomade124x25_greygif_129770083128(self):
        r = self.client.get('/static/images/djangomade124x25_grey.gif', {})
        self.assertEqual(r.status_code, 404)
    def test_faviconico_129770083133(self):
        r = self.client.get('/favicon.ico', {})
        self.assertEqual(r.status_code, 404)
    def test_admin_129770083701(self):
        r = self.client.get('/admin/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['app_path']), u'/admin/?test_client_true=yes')
        self.assertEqual(unicode(r.context[-1]['error_message']), u'')
        self.assertEqual(unicode(r.context[-1]['title']), u'Log in')
        self.assertEqual(unicode(r.context[-1]['root_path']), u'None')
    def test_staticjsjquery_15minjs_129770083783(self):
        r = self.client.get('/static/js/jquery-1.5.min.js', {})
        self.assertEqual(r.status_code, 200)
    def test_faviconico_129770083835(self):
        r = self.client.get('/favicon.ico', {})
        self.assertEqual(r.status_code, 404)
    def test_sisview_student_129770084238(self):
        r = self.client.get('/sis/view_student/', {})
        self.assertEqual(r.status_code, 302)
    def test_faviconico_129770084275(self):
        r = self.client.get('/favicon.ico', {})
        self.assertEqual(r.status_code, 404)
    def test_ajax_selectajax_lookupdstudent_129770084513(self):
        r = self.client.get('/ajax_select/ajax_lookup/dstudent', {'q': 'a', 'timestamp': '1297700845121', 'limit': '10', })
        self.assertEqual(r.status_code, 200)
    def test_staticstudent_picsakasha_abernathy70x65jpg_12977008460(self):
        r = self.client.get('/static/student_pics/Akasha_Abernathy.70x65.jpg', {})
        self.assertEqual(r.status_code, 404)
    def test_staticstudent_picsdiana_abreu70x65jpg_129770084604(self):
        r = self.client.get('/static/student_pics/Diana_Abreu.70x65.jpg', {})
        self.assertEqual(r.status_code, 404)
    def test_staticstudent_picsileanna_pic_270x65jpg_129770084607(self):
        r = self.client.get('/static/student_pics/Ileanna_pic_2.70x65.jpg', {})
        self.assertEqual(r.status_code, 404)
    def test_staticstudent_picsabreu_johsua70x65jpg_129770084608(self):
        r = self.client.get('/static/student_pics/Abreu_Johsua.70x65.jpg', {})
        self.assertEqual(r.status_code, 404)
    def test_staticimagesnoimagejpg_12977008461(self):
        r = self.client.get('/static/images/noimage.jpg', {})
        self.assertEqual(r.status_code, 200)
    def test_staticstudent_picsjacqueline_pic_370x65jpg_129770084612(self):
        r = self.client.get('/static/student_pics/Jacqueline_pic_3.70x65.jpg', {})
        self.assertEqual(r.status_code, 404)
    def test_staticstudent_picsbyron_pic_270x65jpg_129770084615(self):
        r = self.client.get('/static/student_pics/Byron_pic_2.70x65.jpg', {})
        self.assertEqual(r.status_code, 404)
    def test_staticstudent_picsshanice_pic_270x65jpg_129770084616(self):
        r = self.client.get('/static/student_pics/Shanice_pic_2.70x65.jpg', {})
        self.assertEqual(r.status_code, 404)
    def test_staticstudent_picscarlos_aguilo70x65jpg_129770084618(self):
        r = self.client.get('/static/student_pics/Carlos_Aguilo.70x65.jpg', {})
        self.assertEqual(r.status_code, 404)
    def test_staticstudent_picsedward_pic_370x65jpg_129770084619(self):
        r = self.client.get('/static/student_pics/Edward_pic_3.70x65.jpg', {})
        self.assertEqual(r.status_code, 404)
    def test_sisview_student_129770084782(self):
        r = self.client.post('/sis/view_student/', {'student_text': '', 'student': '264', })
    def test_faviconico_129770084919(self):
        r = self.client.get('/favicon.ico', {})
        self.assertEqual(r.status_code, 404)
