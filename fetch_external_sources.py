# -*- coding: utf-8 -*-
# Copyright 2009 - 2011 Machinalis: http://www.machinalis.com/
#
# This file is part of Eff.
#
# Eff is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eff is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Eff.  If not, see <http://www.gnu.org/licenses/>.


from os import environ, remove
environ['DJANGO_SETTINGS_MODULE'] = 'eff_site.settings'
import os.path

from eff_site.eff.models import TimeLog
from eff_site.eff.utils import debug
from eff_site import settings

from eff_site.scripts.fetch_all import run

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

