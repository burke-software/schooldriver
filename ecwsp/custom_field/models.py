from django.contrib.contenttypes.models import ContentType
from django.db import models

class CustomField(models.Model):
    """
    A field abstract -- it describe what the field is.  There are one of these
    for each custom field the user configures.
    """
    name = models.CharField(max_length=75)
    content_type = models.ForeignKey(ContentType)
    field_type = models.CharField(max_length=1, choices=(('t','Text'),('i','Integer'),('b','Boolean (checkbox)'),), default='t')
    
    def get_value_for_object(self,obj):
        return CustomFieldValue.objects.get_or_create(field=self,object_id=obj.id)[0]
    
    def __unicode__(self):
        return unicode(self.name)
        
    class Meta:
        unique_together = ('name','content_type')
    

class CustomFieldValue(models.Model):
    """
    A field instance -- contains the actual data.  There are many of these, for
    each value that corresponds to a CustomField for a given model.
    """
    field = models.ForeignKey(CustomField, related_name='instance')
    value = models.CharField(max_length=255,blank=True,null=True)
    object_id = models.PositiveIntegerField()
    #content_type = models.ForeignKey(ContentType)
    
    def __unicode__(self):
        return unicode(self.value)