# -*- coding: utf-8 -*-

from os import environ, remove
environ['DJANGO_SETTINGS_MODULE'] = 'sitio.settings'
import os.path

from sitio.eff.models import TimeLog
from sitio.eff.utils import debug
from sitio import settings

from sitio.scripts.fetch_all import run

def do_all():
    if not os.path.exists(settings.LOCK_FILE):
        open(settings.LOCK_FILE, 'w').close()
        debug("created lock")

        try:
            run()
        finally:
            debug("removed lock")
            remove(settings.LOCK_FILE)
    else:
        debug("lock exists, did nothing")

    if os.path.exists(settings.FLAG_FILE): remove(settings.FLAG_FILE)

if __name__ == '__main__':
    do_all()

