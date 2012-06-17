# sis/context_processors.py
from django.conf import settings

from ecwsp.administration.models import Configuration

def global_stuff(request):
    try:
        header_image = Configuration.objects.get_or_create(name="Header Logo")[0].file.url
    except:
        header_image = None
    school_name = Configuration.get_or_default('School Name', default="Unnamed School")
    school_color = Configuration.get_or_default('School Color', default="").value
    return {
        "header_image": header_image,
        "school_name": school_name,
        "settings": settings,
        "school_color": school_color,
    }