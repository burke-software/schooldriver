from django.db.models import Q
from django.core import urlresolvers
from django.utils.html import escape
from ajax_select import LookupChannel
from ecwsp.sis.models import UserPreference
from ecwsp.volunteer_track.models import *
from ecwsp.administration.models import *

from datetime import date

class VolunteerLookup(object):
    def get_query(self,q,request):
        """ return a query set.  you also have access to request.user if needed """
        words = q.split()
        # if there is a space
        if (len(words) == 2):
            # search based on first or last name in either order with space in between.
            result = Volunteer.objects.filter(Q(Q(student__fname__istartswith=words[0]) & Q(student__lname__istartswith=words[1]) | Q(student__fname__istartswith=words[1]) & Q(student__lname__istartswith=words[0])))
        # if all one word (or technically more but this will fail)
        else:
            result = Volunteer.objects.filter(Q(student__fname__istartswith=q) | Q(student__lname__istartswith=q) | Q(student__username__icontains=q))
        pref = UserPreference.objects.get_or_create(user=request.user)[0]
        if pref.include_deleted_students:
            return result
        return result.filter(student__inactive=False)

    def format_result(self,volunteer):
        """ 
        the search results display in the dropdown menu.  may contain html and multiple-lines. will remove any |  
        Null's will break this, so check everything and replace it with something meaningful before return 
        """
        year = volunteer.student.year
        if not year: year = "Unknown year"
        image = volunteer.student.pic.url_70x65
        if not image: image = "/static/images/noimage.jpg"
        return "<table style=\"border-collapse: collapse;\"><tr><td><img style=\"height:30px;\" src=%s></td><td>%s %s<br/>%s</td></tr></table>" \
            % (image, volunteer.student.fname, volunteer.student.lname, year)

    def format_item(self,volunteer):
        """ the display of a currently selected object in the area below the search box. html is OK """
        year = volunteer.student.year
        if not year: year = "Unknown year"
        image = volunteer.student.pic.url_70x65
        if not image: image = "/static/images/noimage.jpg"
        return "<table style=\"border-collapse: collapse;\"><tr><td><img src=%s></td><td><a href=\"/admin/sis/student/%s/\" target=\"_blank\">%s %s</a><br/>%s</td></tr></table>" \
            % (image, volunteer.student.id, volunteer.student.fname, volunteer.student.lname, year)

    def get_objects(self,ids):
        """ given a list of ids, return the objects ordered as you would like them on the admin page.
            this is for displaying the currently selected items (in the case of a ManyToMany field)
        """
        return Volunteer.objects.filter(pk__in=ids).order_by('student__lname')
        

class SiteLookup(object):
    def get_query(self,q,request):
        """ return a query set. """
        words = q.split()
        # if there is a space
        if (len(words) == 2):
            # search based on first or last name in either order with space in between.
            result = Site.objects.filter(Q(Q(site_name__istartswith=words[0]) | Q(site_name__istartswith=words[1])))
        # if all one word (or technically more but this will fail)
        else:
            result = Site.objects.filter(Q(site_name__istartswith=q))
        return result
    
    def format_result(self,site):
        """ 
        the search results display in the dropdown menu.  may contain html and multiple-lines. will remove any |  
        Null's will break this, so check everything and replace it with something meaningful before return 
        """
        return "<table><tr><td>%s <br />%s <br />%s, %s %s</td></tr></table>" \
            % ( site.site_name, site.site_address, site.site_city, site.site_state, site.site_zip)

    def format_item(self,site):
        """ the display of a currently selected object in the area below the search box. html is OK """
        return "<table><tr><td>%s <br />%s <br />%s, %s %s</td></tr></table>" \
            % ( site.site_name, site.site_address, site.site_city, site.site_state, site.site_zip)
        
    def get_objects(self,ids):
        """ given a list of ids, return the objects ordered as you would like them on the admin page.
            this is for displaying the currently selected items (in the case of a ManyToMany field)
        """
        return Site.objects.filter(pk__in=ids).order_by('site_name')
        

class SiteSupervisorLookup(LookupChannel):
    model = SiteSupervisor

    def get_query(self,q,request):
        return SiteSupervisor.objects.filter(Q(name__icontains=q)).order_by('name')

    def get_result(self,obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.name

    def format_match(self,obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"<a href=\"/admin/volunteer_track/sitesupervisor/%s/\" target=\"_blank\">%s</a><div><i>%s %s</i></div>" % (obj.id, escape(obj.name),escape(obj.phone),escape(obj.email))