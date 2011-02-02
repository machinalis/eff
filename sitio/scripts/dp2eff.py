#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(1, path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'sitio.settings'

from datetime import datetime
from dotproject import Machinalis

from sitio.eff.models import ExternalSource, Project, TimeLog, Client
from dotproject import fetch_all

if __name__ == '__main__':

    date_format = "%Y%m%d%H%M"
    args = sys.argv[1:]

    if len(args) != 4:
        print ("Usage: $ dp2eff.py <client-name> <source-name>"
               " <from-date> <to-date>")
        print "date format: %s" % date_format
        print "example: 201008190000"
        sys.exit(0)

    client_name, source_name = args[0:2]
    from_date = datetime.strptime(args[2], date_format)
    to_date = datetime.strptime(args[3], date_format)

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
    filename = os.path.join(source.csv_directory, filename.replace(' ', '_'))
    _file = open(filename, 'w')

    fetch_all(source, client, author, from_date, to_date, _file)

    print 'done'
