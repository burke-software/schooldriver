from ecwsp.work_study.models import StudentWorker as Student, Contact
from django.db.models import Q

class StudentLookup(object):

    def get_query(self,q,request):
        """ return a query set.  you also have access to request.user if needed """
        words = q.split()
        # if there is a space
        self.user = request.user
        if (len(words) == 2):
            # search based on first or last name in either order with space in between.
            result = Student.objects.filter(Q(Q(fname__istartswith=words[0]) & Q(lname__istartswith=words[1]) | Q(fname__istartswith=words[1]) & Q(lname__istartswith=words[0])))
        # if all one word (or technically more but this will fail)
        else:
            result = Student.objects.filter(Q(fname__istartswith=q) | Q(lname__istartswith=q) | Q(username__icontains=q))
        return result.filter(inactive=False)

    def format_result(self,student):
        """ 
        the search results display in the dropdown menu.  may contain html and multiple-lines. will remove any |  
        Null's will break this, so check everything and replace it with something meaningful before return 
        """
        year = student.year
        if not year: year = "Unknown year"
        try:
            cra = student.placement.cra
        except:
            cra = "No CRA"
        if not cra: cra = "No CRA"
        image = student.pic.url_70x65
        if not image: image = "/static/images/noimage.jpg"
        company = student.placement
        if not company: company = "No placement"
        return "<table style=\"border-collapse: collapse;\"><tr><td><img src=%s></td><td>%s %s<br/>%s<br/>%s<br/>%s</td></tr></table>" \
            % (image, student.fname, student.lname, year, cra, company)

    def format_item(self,student):
        """ the display of a currently selected object in the area below the search box. html is OK """
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
        txt = "<table style=\"border-collapse: collapse;\"><tr><td><img src=%s></td><td><a href=\"/sis/get_student/%s/\" target=\"_blank\">%s %s</a><br/>%s<br/>CRA: %s<br/>%s</td></tr></table>" \
             % (image, student.id, student.fname, student.lname, year, cra, company)
        return txt

    def get_objects(self,ids):
        """ given a list of ids, return the objects ordered as you would like them on the admin page.
            this is for displaying the currently selected items (in the case of a ManyToMany field)
        """
        return Student.objects.filter(pk__in=ids).order_by('lname')



class ContactLookup(object):
    def get_query(self,q,request):
        """ return a query set.  you also have access to request.user if needed """
        words = q.split()
        # if there is a space
        self.user = request.user
        if (len(words) == 2):
            # search based on first or last name in either order with space in between.
            result = Contact.objects.filter(Q(Q(fname__istartswith=words[0]) & Q(lname__istartswith=words[1]) | Q(fname__istartswith=words[1]) & Q(lname__istartswith=words[0])))
        # if all one word (or technically more but this will fail)
        else:
            result = Contact.objects.filter(Q(fname__istartswith=q) | Q(lname__istartswith=q))
        return result

    def format_result(self,contact):
        """ 
        the search results display in the dropdown menu.  may contain html and multiple-lines. will remove any |  
        Null's will break this, so check everything and replace it with something meaningful before return 
        """
        phone = contact.phone
        if not phone: phone = " "
        phone_cell = contact.phone_cell
        if not phone_cell: phone_cell = " "
        fax = contact.fax
        if not fax: fax = " "
        email = contact.email
        if not email: email = " "
        return "<table style=\"border-collapse: collapse;\"><tr><td>%s %s<br/>%s<br/>%s</td></tr></table>" \
            % (contact.fname, contact.lname, phone, phone_cell)


    def format_item(self,contact):
        """ the display of a currently selected object in the area below the search box. html is OK """
        phone = contact.phone
        if not phone: phone = " "
        phone_cell = contact.phone_cell
        if not phone_cell: phone_cell = " "
        fax = contact.fax
        if not fax: fax = " "
        email = contact.email
        if not email: email = " "
        return "<table style=\"border-collapse: collapse;\"><tr><td>%s %s<br/>Phone: %s<br/>Cell: %s</td></tr></table>" \
             % (contact.fname, contact.lname, phone, phone_cell)

    def get_objects(self,ids):
        """ given a list of ids, return the objects ordered as you would like them on the admin page.
            this is for displaying the currently selected items (in the case of a ManyToMany field)
        """
        return Contact.objects.filter(pk__in=ids).order_by('lname')