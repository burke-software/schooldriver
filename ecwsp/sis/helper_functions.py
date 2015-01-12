from django.db.models import AutoField
from django.db import models, connection
from django.core.exceptions import PermissionDenied
from django.contrib import admin
from django.conf import settings
from django.utils.encoding import smart_unicode
from functools import wraps
import unicodedata
from decimal import Decimal, ROUND_HALF_UP, getcontext
if settings.MULTI_TENANT:
    from tenant_schemas.utils import get_tenant_model, tenant_context

class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable


def get_current_tenant():
    """ Return current tenant
    Determine based on connection schema_name """
    schema_name = connection.schema_name
    connection.set_schema_to_public()
    tenant = get_tenant_model().objects.get(schema_name=schema_name)
    connection.set_tenant(tenant)
    return tenant


def all_tenants(f):
    """ Decorator. Check if multi tenant is enabled. If so
    run function f on each tenant
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if settings.MULTI_TENANT:
            for tenant in get_tenant_model().objects.exclude(schema_name="public"):
                with tenant_context(tenant):
                    f(*args, **kwargs)
        else:
            f(*args, **kwargs)
    return wrapper


def get_base_url():
    """ Get base url like http://www.example.com.
    Will determine if system is multi tenanted and return
    appropriate url.
    """
    if settings.MULTI_TENANT:
        tenant = get_current_tenant()
        return 'http://{}'.format(tenant.domain_url)
    return settings.BASE_URL

def round_as_decimal(num, decimal_places=2):
    """Round a number to a given precision and return as a Decimal

    Arguments:
    :param num: number
    :type num: int, float, decimal, or str
    :returns: Rounded Decimal
    :rtype: decimal.Decimal
    """
    precision = '1.{places}'.format(places='0' * decimal_places)
    try:
        return Decimal(str(num)).quantize(Decimal(precision), rounding=ROUND_HALF_UP)
    except:
        return num

def round_to_standard(num):
    """ Round to what our database supports
    which is a Decimal(5,2) or two decimal places.
    """
    return round_as_decimal(num, 2)

def strip_unicode_to_ascii(string):
    """ Returns a ascii string that doesn't contain utf8
    Don't use this unless you have to it remove data!
    You're probably rascist if you do use this.
    But nice for working with systems that can't deal with utf8
    """
    return unicodedata.normalize('NFKD', smart_unicode(string)).encode('ascii','ignore')

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
    if request.user and hasattr(request.user,"pk") and request.user.pk:
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
       if value=="" or value==None:     #if Django tries to save '' string, send the db None (NULL)
            return None
       else:
            return super(CharNullField, self).get_db_prep_value(value, *args, **kwargs)
