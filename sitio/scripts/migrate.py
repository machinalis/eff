#!/usr/bin/env python
""" Creates the slug column for Client model and slugifies de client name
"""
import os, sys
import sqlite3

from django.template.defaultfilters import slugify

sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'sitio.settings'

from django.conf import settings

if not os.path.isfile(settings.DATABASE_NAME):
    db_name = os.path.join(os.path.dirname(__file__), '..', settings.DATABASE_NAME)
    settings.DATABASE_NAME=db_name
else:
    db_name = settings.DATABASE_NAME

conn = sqlite3.connect(db_name)

# Try client slugs migration
try:
    print "Migrating Client slugs...", 
    conn.execute('ALTER TABLE eff_client ADD COLUMN "slug" varchar(50)')
    from sitio.eff.models import Client
    for cli in Client.objects.all():
        cli.slug=slugify(cli.name)
        cli.save()
    print "DONE", 
except sqlite3.OperationalError as (message, ):
    if message == 'duplicate column name: slug':
        print "Client slugs already exists."

# Add state column to eff_client table
try:
    print "Adding state to Client...", 
    conn.execute('ALTER TABLE eff_client ADD COLUMN "state" varchar(100)')
    print "DONE", 
except sqlite3.OperationalError, message:
    if message == 'duplicate column name: state':
        print "Client state field already exists."

conn.close()
