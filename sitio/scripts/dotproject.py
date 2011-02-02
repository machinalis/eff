# -*- coding: utf-8 -*-
from datetime import datetime
import MySQLdb

from sitio.eff.utils import EffCsvWriter
from django.conf import settings


class DotProject(object):
    _connection = None
    _cursor = None

    def __init__(self):
        if self._connection is None:
            type(self).start_db_connection()

    @classmethod
    def start_db_connection(cls):
        cls._connection = MySQLdb.connect(db=cls.DB,
                                          user=cls.DB_USER,
                                          passwd=cls.PASSWD,
                                          host=cls.HOST,
                                          port=cls.PORT,
                                          charset=cls.CHARSET)
        cls._cursor = cls._connection.cursor()

    @classmethod
    def get_logs(cls, client, from_date, to_date):
        # The "between X and Y" of mysql is very picky,
        # at least in dates, if Y is Year-month-day-00:00,
        # then it will not pick up logs that were made on
        # _day_
        to_date = to_date.replace(hour=23,minute=59,second=59,microsecond=0)
        from_date = str(from_date)
        to_date = str(to_date)
        cls._cursor.execute("SELECT task_log_date, project_short_name, "
                            "users.user_username, task_log_hours, "
                            "task_log_name, task_log_description "
                            "FROM task_log, users, tasks, projects, companies "
                            "WHERE task_log_date BETWEEN %s AND %s "
                            "AND task_log.task_log_creator=users.user_id "
                            "AND tasks.task_project=projects.project_id "
                            "AND tasks.task_id = task_log.task_log_task "
                            "AND companies.company_name=%s "
                            "AND companies.company_id = projects.project_company",
                            (from_date, to_date, client))
        return cls._cursor.fetchall()
    

class DotProjectSource(DotProject):
    """
    This defines the data needed to access the dotproject database.
    You need to configure this from settings.py or creating a
    local_settings.py if you want to use it (First you
    need to create an ExternalSource with name Dotproject or whatever
    is configured in scripts/config.py)
    """
    DB = settings.DOTPROJECT_DB_NAME
    DB_USER = settings.DOTPROJECT_DB_USER
    PASSWD = settings.DOTPROJECT_DB_PASSWD
    HOST = settings.DOTPROJECT_DB_HOST
    PORT = settings.DOTPROJECT_DB_PORT
    CHARSET = settings.DOTPROJECT_DB_CHARSET


def fetch_all(source, client, author, from_date, to_date, _file):

    writer = EffCsvWriter(source, client, author, _file,
                          from_date=from_date,
                          to_date=to_date)

    for row in DotProjectSource().get_logs(client.external_id,
                                           from_date,
                                           to_date):
        writer.write(row)

