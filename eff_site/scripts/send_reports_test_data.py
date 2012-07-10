# -*- coding: utf-8 *-*
# This script call a view of eff, this view send an email each user with
# receive report email in True, and not is a user client
import sys
import os

path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(1, path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'eff_site.settings'

import random
from datetime import date
from django.contrib.auth.models import User
from eff_site.eff.models import Project, Dump, TimeLog
from dateutil.relativedelta import relativedelta, MO


def generate_timelog_data():
    users = User.objects.all()
    projects = Project.objects.all()
    dumps = Dump.objects.all()
    current_date = date.today()
    previuos_date = current_date - relativedelta(weeks=+1)
    date_timelog = previuos_date - relativedelta(weekday=MO(-1))

    # Genera registros de Lunes a Viernes
    for day in range(0, 5):
        # Genera registros para 5 usuarios aleatorios
        for u in range(1, 6):
            user = random.choice(users)
            project = random.choice(projects)
            dump = random.choice(dumps)
            task_name = 'task %s' % day
            hours = round(random.random() * 10, 3)
            description = 'description %s do %s' % (user.username, task_name)
            timelog = TimeLog(
                date=date_timelog,
                project=project,
                task_name=task_name,
                user=user,
                hours_booked=hours,
                description=description,
                dump=dump)
            timelog.save()
        date_timelog = date_timelog + relativedelta(days=1)


if __name__ == '__main__':
    generate_timelog_data()
