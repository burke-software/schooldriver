from django.db.models import AutoField
from django.db import models
from django.core.exceptions import PermissionDenied
from django.contrib import admin

class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable

def copy_model_instance(obj):
    """ Django snippit 1040
    Create a copy of a model instance.
    Works in model inheritance case where instance.pk = None is not good enough, since the subclass instance refers to the parent_link's primary key during save.
    M2M relationships are currently not handled, i.e. they are not copied.
    """
    initial = dict([(f.name, getattr(obj, f.name))
                    for f in obj._meta.fields
                    if not isinstance(f, AutoField) and\
                       not f in obj._meta.parents.values()])
    return obj.__class__(**initial)

def log_admin_entry(request, obj, state, message=""):
    """
    Make a log entry in django admin.
    request: Django request - must have user. Will do nothing without user.
    obj: Any django object
    state: django.contrib.admin.models. ADDITION, DELETION, or CHANGE
    message: optional message for log
    """
    from django.contrib.admin.models import LogEntry
    from django.contrib.contenttypes.models import ContentType
    if request.user and hasattr(request.user,"pk"):
        LogEntry.objects.log_action(
            user_id         = request.user.pk, 
            content_type_id = ContentType.objects.get_for_model(obj).pk,
            object_id       = obj.pk,
            object_repr     = unicode(obj), 
            action_flag     = state,
            change_message  = message
        )

class Struct(object):
    def __unicode__(self):
        return ""

class CharNullField(models.CharField):
    description = "CharField that stores NULL but returns ''"
    def to_python(self, value):  #this is the value right out of the db, or an instance
       if isinstance(value, models.CharField): #if an instance, just return the instance
              return value 
       if value==None:   #if the db has a NULL (==None in Python)
              return ""  #convert it into the Django-friendly '' string
       else:
              return value #otherwise, return just the value
    def get_db_prep_value(self, value, *args, **kwargs):  #catches value right before sending to db
       if value=="":     #if Django tries to save '' string, send the db None (NULL)
            return None
       else:
            return super(CharNullField, self).get_db_prep_value(value, *args, **kwargs)
    
class ReadPermissionModelAdmin(admin.ModelAdmin):
    """ based on http://gremu.net/blog/2010/django-admin-read-only-permission/
    Admin model that allows users to read
    """
    def has_change_permission(self, request, obj=None):
        if getattr(request, 'readonly', False):
            return True
        return super(ReadPermissionModelAdmin, self).has_change_permission(request, obj)

    def changelist_view(self, request, extra_context=None):
        try:
            return super(ReadPermissionModelAdmin, self).changelist_view(
                request, extra_context=extra_context)
        except PermissionDenied:
            pass
        perm_name = '%s.view_%s' % (self.model._meta.app_label, unicode.lower(unicode(self.model._meta.object_name)))
        if request.method == 'POST' or not perm_name in request.user.get_all_permissions():
            # Only allow POST if export to xls and nothing evil
            # It's not all that secure, but we assume authenticated users aren't trying to hack things.
            if not (request.POST['action'] == 'export_simple_selected_objects' and len(request.POST) <= 4) :
                raise PermissionDenied
        request.readonly = True
        return super(ReadPermissionModelAdmin, self).changelist_view(
            request, extra_context=extra_context)

    def change_view(self, request, object_id, extra_context=None):
        try:
            return super(ReadPermissionModelAdmin, self).change_view(
                request, object_id, extra_context=extra_context)
        except PermissionDenied:
            pass
        if request.method == 'POST':
            raise PermissionDenied
        request.readonly = True
        return super(ReadPermissionModelAdmin, self).change_view(
            request, object_id, extra_context=extra_context)
