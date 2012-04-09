from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext

def get_filters(request, app, module):
    model_class = ContentType.objects.get(app_label=app, model=module).model_class()
    fields = model_class._meta.fields
    
    return render_to_response(
        'admin_advanced_filter/get_filters.html', 
        {'fields': fields,}, 
        RequestContext(request, {}),
    )

def get_filter_field(request, ct, field_name):
    model_class = ContentType.objects.get(id=ct).model_class()
    return render_to_response(
        'admin_advanced_filter/get_filter_field.html', 
        {'fields': fields,}, 
        RequestContext(request, {}),
    )
