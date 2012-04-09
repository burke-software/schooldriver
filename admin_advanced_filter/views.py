from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType

def show_filters(request, app, module):
    model_class = ContentType.objects.get(app_label=app, model=module).model_class()
    
    for field in model_class.model._meta.fields:
        pass
    
    return render_to_response(
        'admin_advanced_filter/show_filters.html', 
        {'msg': '',}, 
        RequestContext(request, {}),
    )
