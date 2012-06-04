import os
import glob
import sys
from ecwsp.sis.models import *
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.conf import settings

class Command(BaseCommand):
    help = """
    Manually generate thumbnail pictures if it doesn't work for whatever reason from a media file.
    """
    option_list = BaseCommand.option_list + (
        make_option('--format', '-f', dest='format',),
    )
    
    def handle(self, *args, **options):
        from ecwsp.sis.thumbs import generate_thumb
        pictures = os.path.join(settings.MEDIA_ROOT,"student_pics/")
        if options['format']:
            format = options ['format']
        for infile in pictures:
            generate_thumb(infile, (70,65), format)
            generate_thumb(infile, (530,400), format)
    
