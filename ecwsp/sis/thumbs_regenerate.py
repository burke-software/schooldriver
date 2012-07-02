#!/usr/bin/python

import sys
from django.core.management import setup_environ 

# Put the path for your Django installation here.
sys.path.append('/home/vinicius/web/erp/')

import settings
setup_environ(settings)
from main.thumbs import *
regenerate_thumbs()
