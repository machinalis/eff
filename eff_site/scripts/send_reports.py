# -*- coding: utf-8 *-*
# This script call a view of eff, this view send an email each user with
# receive report email in True, and not is a user client
import sys
import os

path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(1, path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'eff_site.settings'

from datetime import datetime, date
from eff_site.eff.models import UserProfile
from django.template.loader import render_to_string
from dateutil.relativedelta import relativedelta, MO


DAY_OF_WEEK = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'}

# Set the day of a week to send emails
SEND_DAY = 0


def hour_report_last_week():
    userprofiles = UserProfile.objects.filter(
            receive_report_email=True
        ).exclude(
            user_type=UserProfile.KIND_CLIENT
        )
    for userprofile in userprofiles:
        _send_report_by_email(userprofile, project=None)


def _send_report_by_email(userprofile, project):
    user = userprofile.user
    context_for_email = {}
    current_date = date.today()

    previuos_date = current_date - relativedelta(weeks=+1)
    from_date = previuos_date - relativedelta(weekday=MO(-1))
    to_date = previuos_date - relativedelta(weekday=6)

    context_for_email['user'] = user
    context_for_email['from_date'] = from_date
    context_for_email['to_date'] = to_date
    context_for_email['report'] = userprofile.report(from_date,
        to_date, project)

    # detailed total of hours between [from_date, to_date]
    total_hrs = 0
    for r in context_for_email['report']:
        total_hrs += r[3]
    context_for_email['total_hrs_detailed'] = total_hrs
    context_for_email['num_loggable_hours'] = userprofile.num_loggable_hours(
        from_date, to_date)

    subject = render_to_string('previous_week_report_subject.txt',
        context_for_email)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    message = render_to_string('previous_week_report_message.txt',
        context_for_email)
    user.email_user(subject, message)


if __name__ == '__main__':
    current_date = datetime.today()
    current_day = current_date.weekday()
    if current_day == SEND_DAY:
        hour_report_last_week()
    else:
        print('Today is not %s' % DAY_OF_WEEK[SEND_DAY])
