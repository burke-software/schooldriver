from ecwsp.sis.models import *
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

class Command(BaseCommand):
    help = """
    Add user to student or faculty. Great for syncing with other programs or ldap
    options
    -u username
    -f fname
    -l lname
    -t teacher (True or False)
    -s student (True or False)
    """
    option_list = BaseCommand.option_list + (
        make_option('--username', '-u', dest='user',),
        make_option('--firstname', '-f', dest='fname',),
        make_option('--lastname', '-l', dest='lname',),
        make_option('--teacher', '-t', dest='teacher',),
        make_option('--student', '-s', dest='student',),
    )
    
    def handle(self, *args, **options):
        if options['student']:
            s = Student(
                username=options['user'],
                fname=options['fname'],
                lname=options['lname'],
                )
            s.save()
            print 'Create student %s' % (s,)
        elif options['teacher']:
            s = Faculty(
                username=options['user'],
                fname=options['fname'],
                lname=options['lname'],
                teacher=True,
                )
            s.save()
            print 'Create teacher %s' % (s,)
        else:
            s = Faculty(
                username=options['user'],
                fname=options['fname'],
                lname=options['lname'],
                )
            s.save()
            print 'Create faculty %s' % (s,)
