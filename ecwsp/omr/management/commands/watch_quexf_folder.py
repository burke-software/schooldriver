from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.conf import settings
import os, time

LOCK_EXPIRE = 60

class Command(BaseCommand):
    help = """
    Watch folder forever, looking for new files.
    Should be run every minute
    usage
    watch_quexf_folder /var/www/pdfs/
    """
    
    def watch_folder(self):
        before = dict ([(f, None) for f in os.listdir (path_to_watch)])
        i = 0
        while i < 11:
            after = dict ([(f, None) for f in os.listdir (path_to_watch)])
            added = [f for f in after if not f in before]
            if added: print "Added: ", ", ".join (added)
            before = after
            time.sleep (5)
            i += 1
    
    def handle(self, *args, **options):
        path_to_watch = args[0]
        lock_id = "lock-%s" % (settings.BASE_URL)
        acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
        release_lock = lambda: cache.delete(lock_id)
        if acquire_lock():
            try:
                self.watch_folder()
            finally:
                release_lock()
        
