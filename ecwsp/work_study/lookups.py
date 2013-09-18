from ecwsp.work_study.models import StudentWorker as Student, Contact
from django.db.models import Q
from ajax_select import LookupChannel

class StudentLookup(LookupChannel):
    model = Student
    def get_query(self,q,request):
        qs = Student.objects.all()
        for word in q.split():
            qs = qs.filter(Q(last_name__icontains=word) | Q(first_name__icontains=word) | Q(username__istartswith=q))
        return qs.order_by('last_name')

    def format_match(self,student):
        year = student.year
        if not year: year = "Unknown year"
        try:
            cra = student.placement.cra
        except:
            cra = "No CRA"
        if not cra: cra = "No CRA"
        image = student.pic.url_70x65
        if not image: image = "/static/images/noimage.jpg"
        try:
            company = student.placement
            if not company: company = "No placement"
        except: company = "None"
        txt = '<img align="left" src="%s"/> %s %s <br/>%s<br/>%s' \
             % (image, student.first_name, student.last_name, year, company)
        return txt

    def format_item_display(self,student):
        year = student.year
        if not year: year = "Unknown year"
        try:
            cra = student.placement.cra
        except:
            cra = "No CRA"
        if not cra: cra = "No CRA"
        image = student.pic.url_70x65
        if not image: image = "/static/images/noimage.jpg"
        try:
            company = student.placement
            if not company: company = "No placement"
        except: company = "None"
        contact_number = ""
        if student.primary_contact:
            contact_number = student.primary_contact.phone
        txt = '<img align="left" src="%s"/> <a href=\"/sis/get_student/%s/\" target=\"_blank\">  %s %s</a><br/>%s<br/>CRA: %s<br/>%s<br/>%s %s' \
             % (image, student.id, student.first_name, student.last_name, year, cra, company, student.primary_contact, contact_number)
        return txt

    def get_objects(self,ids):
        return Student.objects.filter(pk__in=ids).order_by('last_name')



class ContactLookup(LookupChannel):
    model = Contact
    
    def get_query(self,q,request):
        qs = Contact.objects.all()
        for word in q.split():
            qs = qs.filter(Q(lname__icontains=word) | Q(fname__icontains=word) | Q(email__istartswith=q))
        return qs.order_by('lname')

    def format_match(self,obj):
        return self.format_item_display(obj)

    def format_item_display(self,contact):
        phone = contact.phone
        if not phone: phone = " "
        phone_cell = contact.phone_cell
        if not phone_cell: phone_cell = " "
        fax = contact.fax
        if not fax: fax = " "
        email = contact.email
        if not email: email = " "
        return "%s %s<br/>Phone: %s<br/>Cell: %s" \
             % (contact.fname, contact.lname, phone, phone_cell)

    def get_objects(self,ids):
        return Contact.objects.filter(pk__in=ids).order_by('lname')