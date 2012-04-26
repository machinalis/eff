#!/usr/bin/env python
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

import sys
import os

path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(1, path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'eff_site.settings'

from datetime import datetime
from tutos import fetch_all

from eff_site.eff.models import ExternalSource, Project, TimeLog, Client

if __name__ == '__main__':

    args = sys.argv[1:]

    if len(args) != 4:
        print ("Usage: $ tutos2eff.py <client-name> <source-name>"
               " <username> <password>")
        sys.exit(0)

    client_name, source_name, username, password = args

    try:
        source = ExternalSource.objects.get(name=source_name)
    except ExternalSource.DoesNotExist:
        print 'Source with name: %s does not exist' % source_name
        sys.exit(1)

    try:
        client = Client.objects.get(name=client_name)
    except ExternalSource.DoesNotExist:
        print 'Client with name: %s does not exist'
        sys.exit(1)

    author = source.username or 'Anonymous Coward'

    filename = "%s_%s_%s.csv" % (source.name, args[2], args[3], )
    filename = os.path.join("./", filename.replace(' ', '_'))
    _file = open(filename, 'w')

    fetch_all(source, client, author, None, None, _file)

    print 'done'
