#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(1, path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'sitio.settings'

from datetime import datetime
from dateutil.relativedelta import relativedelta

from sitio.eff.utils import EffCsvWriter, load_dump
from sitio.eff.models import ExternalSource, Project, TimeLog, Client
from sitio import settings

from config import EXT_SRC_ASSOC

def run():
    date_format = "%Y%m%d"
    args = sys.argv[1:]

    if not len(args) in (0, 3):
        print "Usage: $ fetchall.py <source-name> <from-date> <to-date>"
        sources_allowed = map(lambda e: e.name, ExternalSource.objects.all())
        sources_allowed.append(u'ALL')
        print "\tValues allowed for <source-name>: %s" % ' | '.join(sources_allowed)
        print "\tDate format: %s ; example: 20100819" % date_format
        sys.exit(0)

    if len(args)==3:
        source_name = args[0]
        from_date = datetime.strptime(args[1], date_format)
        to_date = datetime.strptime(args[2], date_format)
    else:
        source_name="ALL"
        today = datetime.today()
        to_date = datetime(today.year, today.month, today.day)
        from_date = datetime(to_date.year, to_date.month, 1) - relativedelta(months=1)
    
    if source_name=="ALL":
        sources = ExternalSource.objects.all()
    else:
        sources = ExternalSource.objects.filter(name=source_name)

    if not sources:
        print 'Source with name: %s does not exist' % source_name
        sys.exit(1)
    
    if not os.path.exists(settings.FETCH_EXTERNALS_CSV_DIR):
        os.makedirs(settings.FETCH_EXTERNALS_CSV_DIR)

    for source in sources:

        author = source.username or 'Eff Fetcher'

        src_clients = Client.objects.filter(external_source=source)

        src_mod_name = EXT_SRC_ASSOC[source.name]
        src_mod = __import__('sitio.scripts.%s' % src_mod_name, fromlist=['sitio.scripts'])

        for client in src_clients:

            filename = "%s_%s_%s_%s.csv" % (source.name, client.name, from_date.strftime("%Y%m%d"), 
                                            to_date.strftime("%Y%m%d"), )
            filename = os.path.join(settings.FETCH_EXTERNALS_CSV_DIR, filename.replace(' ', '_'))
            _file = open(filename, 'w')

            src_mod.fetch_all(source, client, author, from_date, to_date, _file)

            n_lines = len(open(filename).readlines())

            if n_lines <= 5:
                os.unlink(filename)
            else:
                eff_import = open(filename)
                load_res = load_dump(eff_import, is_api=True)
                eff_import.close()
                if source.name == 'DotprojectMachinalis':
                    os.unlink(filename)

if __name__ == '__main__':
    run()