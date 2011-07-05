import os
import sys

# set your path here
# sys.path = [] + sys.path
from django.core.handlers.wsgi import WSGIHandler

os.environ['DJANGO_SETTINGS_MODULE'] = 'sitio.settings'
application = WSGIHandler()
