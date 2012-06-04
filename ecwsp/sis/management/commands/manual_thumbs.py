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
        students = Student.objects.filter(pic__isnull=False)
        if options['format']:
            format = options ['format']
        else:
            format = 'jpeg'
        for student in students:
            if student.pic != '':
                generate_thumb(student.pic, (70,65), format)
                generate_thumb(student.pic, (530,400), format)
        #path = os.path.join(settings.MEDIA_ROOT,'student_pics/')
        #pictures = glob.glob(os.path.join(path,'*.jpg'))
        #
        
        #for infile in pictures:
        #    print infile
        #    #file = os.open(infile, os.O_RDWR)
        #    generate_thumb(infile, (70,65), format)
        #    generate_thumb(infile, (530,400), format)
        #    #os.close(infile)
    
