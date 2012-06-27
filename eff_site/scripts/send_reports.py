# -*- coding: utf-8 *-*
# This script call a view of eff, this view send an email each user with
# receive report email in True, and not is a user client
from datetime import datetime
import urllib2

DAY_OF_WEEK = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'}

# Set the day of a week to send emails
SEND_DAY = 2


# URL of eff_site instance
DOMAIN = 'http://localhost:8000'
EFF_URL = '/reporte/sendemails/'
URL = DOMAIN + EFF_URL


def send_emails():
    web = urllib2.urlopen(URL)


if __name__ == '__main__':
    current_date = datetime.today()
    current_day = current_date.weekday()
    if current_day == SEND_DAY:
        send_emails()
    else:
        print('Today is not %s' % DAY_OF_WEEK[SEND_DAY])
