#!/bin/bash
# export PYTHONPATH=$PYTHONPATH add paths here
# We run this script using a cron job, that runs every 30minutes
DJANGO_SETTINGS_MODULE=sitio.settings python ./fetch_external_sources.py
