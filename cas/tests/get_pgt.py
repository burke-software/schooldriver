# Run via bin/django shell --plain < get_pgt.py
# to pick up all the django environment
# Allows main test class to be independent of CAS implementation platform
# TODO: pass in iou - if cant take args write to file and read here
import atexit
from cas.models import PgtIOU

@atexit.register
def lookup_pgt():
    pgt = PgtIOU.objects.latest('created') 
    if pgt:
        print pgt.tgt
    else:
        print 'FAIL'


