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


from os import stat, remove, symlink
from os.path import basename
from datetime import date, datetime
from dateutil.relativedelta import relativedelta, SU, SA

import csv
import tempfile

from _models.project import Project, ProjectAssoc
from _models.log import TimeLog
from _models.external_source import ExternalSource
from _models.dump import Dump
from _models.user_profile import UserProfile
from _models.client import Client
from django.conf import settings
from django.utils.encoding import force_unicode
from decimal import Decimal


def previous_week(a_date):
    to_date = a_date - relativedelta(weekday=SA, weeks=1)  # last saturday
    # sunday before last saturday
    from_date = to_date - relativedelta(weekday=SU, weeks=1)
    return (from_date, to_date)


def week(a_date):
    to_date = a_date + relativedelta(weekday=SA)  # next saturday
    from_date = to_date - relativedelta(weekday=SU, weeks=1)  # last sunday
    return (from_date, to_date)


def month(a_date):
    from_date = date(a_date.year, a_date.month, 1)
    to_date = from_date + relativedelta(months=1) - relativedelta(days=1)
    return (from_date, to_date)


def period(start_date, end_date, op):
    """
        Calculates period between start_date and end_date using 'op'
    """
    rdelta = relativedelta(end_date, start_date) + relativedelta(days=1)
    from_date = op(start_date, rdelta)
    to_date = op(end_date, rdelta)
    assert(from_date <= to_date)
    return (from_date, to_date)


def third_sunday(a_date):
    return date(a_date.year, a_date.month, 1) + \
                relativedelta(weekday=SU, weeks=2)


def overtime_period(a_date):

    # is `a_date' prior to the day before of the third sunday in a_date's month?
    # if a_date.day <= third_sunday(a_date).day - 1:
    #     # go to month before a_date's month
    #     a_date = a_date - relativedelta(months=1)

    if a_date.day >= third_sunday(a_date).day:
        a_date = a_date + relativedelta(months=1)

    to_date = date(a_date.year, a_date.month, third_sunday(a_date).day - 1)

    from_date = to_date - relativedelta(months=1)
    from_date = date(from_date.year, from_date.month,
        third_sunday(from_date).day)

    assert(from_date < to_date)

    return (from_date, to_date)

INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
FATAL = "FATAL"


def debug(msg, *args, **kwargs):
    level = kwargs.get('level', INFO)
    if getattr(settings, 'DEBUG', True):
        print '%s: %s: %s' % (basename(__file__),
                              level,
                              args and (msg % args) or msg)


def force_symlink(src, dst):
    try:
        stat(dst)
    except OSError:
        pass
    else:
        remove(dst)
    debug("symlinking %s to %s", src, dst)
    symlink(src, dst)


class Data (object):
    """ This is a 'bag of data' just holds data and it's use inside the views.
    """

    def __init__(self, profile, from_date, to_date):
        self.username = profile.user.username
        self.name = profile.user.first_name or profile.user.username
        fancy_name = "%s %s" % (profile.user.first_name, profile.user.last_name)
        self.fancy_name = fancy_name.strip() and fancy_name or self.name
        self.url = profile.get_absolute_url()
        self.is_active = profile.is_active(from_date, to_date)
        self.worked_hours = profile.get_worked_hours(from_date, to_date)
        self.loggable_hours = profile.num_loggable_hours(from_date, to_date)
        self.billable_hours = profile.billable_hours(from_date, to_date)
        try:
            self.percentage_billable_hours =\
                profile.percentage_billable_hours(from_date, to_date)
        except ValueError:
            self.percentage_billable_hours = 0

        try:
            self.percentage_hours_worked =\
                profile.percentage_hours_worked(from_date, to_date)

        except ValueError:
            self.percentage_hours_worked = 0

        self.projects = profile.projects(from_date, to_date)

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.is_active == other.is_active and
            self.worked_hours == other.worked_hours and
            self.loggable_hours == other.loggable_hours and
            self.percentage_hours_worked == other.percentage_hours_worked and
            self.percentage_billable_hours == other.percentage_billable_hours \
            and self.billable_hours == other.billable_hours and
            self.username == other.username)

    def efficiency_class(self):
        if self.percentage_hours_worked < 70.:
            return 'bad'
        if self.percentage_hours_worked < 95.:
            return 'poor'
        if self.percentage_hours_worked > 100:
            return 'exceptional'
        return 'good'


class DataTotal (Data):

    def __init__(self, wh, lh, bh):
        self.worked_hours = wh
        self.loggable_hours = lh
        self.billable_hours = bh
        if lh > 0:
            # Total of UserProfile.percentage_hours_worked()
            self.percentage_hours_worked = (wh / lh * 100).quantize(
                Decimal('.00'))

            # Total of UserProfile.percentage_billable_hours()
            self.percentage_billable_hours = (bh / lh * 100).quantize(
                Decimal('.00'))
        else:
            self.percentage_hours_worked = 0
            self.percentage_billable_hours = 0


class EffCsvWriter(object):
    """
    Helper class to generate Eff formatted csv files.

    The generated file will contain a header with the following format:\n
    # ExternalSource: <source_name>\n
    # Client: <client_name>\n
    # Author: <name>\n
    # From date: <date>\n
    # To date: <date>\n

    And each task log line with the following format:\n
    "<date>","<project_external_id>","<user_external_id>","<task_hours_booked>",
    "<task_name>","<task_description>"

    @cvar VALIDATE_ROWS: Determines if each row and its fields must be validated
    (size and type) before being writed to file
    """

    VALIDATE_ROWS = True

    def __init__(self, ext_src, client, author, _file, date_format="%Y-%m-%d",
                 from_date=None, to_date=None):
        """ Writes the header to the file and initializes de csv writer to be
        ready to write task logs.

        @param ext_src: external source for the csv file being generated
        @type ext_src: eff_site.eff.models.ExternalSource
        @param client: client for the csv file being generated
        @type client: eff_site.eff.models.Client
        @param author: author of the csv file being generated
        @type author: basestring
        @param _file: where Eff formated csv is saved
        @type _file: file object
        @param date_format:  date format (used in strftime) to be used
        to convert and write dates in the Eff formated csv
        @type date_format: basestring
        @param from_date: start date for the csv file being generated
        @type from_date: datetime.date
        @param to_date: end date for the csv file being generated
        @type to_date: datetime.date

        """
        self.ext_src = ext_src
        self.client = client
        self.author = author
        self.file = _file
        self.date_format = date_format
        self.from_date = from_date
        self.to_date = to_date

        if not self.to_date:
            self.to_date = date.today()

        csv_header = ("# ExternalSource: %s\r\n"
                      "# Client: %s\r\n"
                      "# Author: %s\r\n"
                      "# From date: %s\r\n"
                      "# To date: %s\r\n") % \
                      (self.ext_src.name,
                       self.client.name,
                       self.author,
                       self.from_date,
                       self.to_date, )

        self.file.write(csv_header.encode('utf-8'))
        if isinstance(self.file, file):
            self.file.close()
            self.writer = csv.writer(open(self.file.name, 'a'), delimiter=",",
                quoting=csv.QUOTE_ALL)
        else:
            self.writer = csv.writer(self.file, delimiter=",",
                quoting=csv.QUOTE_ALL)

    def _validate_row(self, row):
        """ Check that a row to be writed is a valid task log.

        @param row: the row that is about to be writed.
        @type row: list

        @return: "OK" on success, an error message describing the problem
        otherwise

        """
        if not hasattr(row, '__iter__'):
            return "Row must be a list or tuple"
        if len(row) != 6:
            return ("Row must contain 6 items: Date, Project,"
                    " User, Hours, Task Name, Task Description")
        if not isinstance(row[0], (date, datetime)):
            return "First row item must be a date"
        if not isinstance(row[1], (Project, basestring)):
            return "Second row item must be a project name or Project instance"
        if not isinstance(row[2], basestring):
            return "Third row item must be a string"
        if not hasattr(row[3], '__int__'):
            return "Fourth row item must be a number"
        if not isinstance(row[4], basestring):
            return "Fifth row item must be a string"
        if not isinstance(row[5], basestring):
            return "Sixth row item must be a string"
        return "OK"

    def write(self, row):
        """ Validates (if apply) and writes a row to the file.

        @param row: the task log row to be writed.
        @type row: list

        @raise Exception(validation_error_message): if the row to be writed
        is a not valid task log.

        """
        if self.VALIDATE_ROWS:
            validation_msg = self._validate_row(row)
            if validation_msg != "OK":
                remove(self.file.filename)
                raise Exception("Error writing %s to csv file: %s"
                                % (row, validation_msg, ))
        row = list(row)
        if isinstance(row[1], Project):
            row[1] = row[1].external_id

        if hasattr(row[0], 'date'):
            row[0] = row[0].date().strftime(self.date_format)
        elif isinstance(row[0], date):
            row[0] = row[0].strftime(self.date_format)

        # UTF-8 encoding
        def _encode(x):
            # This is used to encode all strings in utf8
            if isinstance(x, unicode):  # if it str, leave it as it is
                return x.encode('utf-8')
            return x

        erow = [_encode(x) for x in row]
        debug("Saving: %s", erow)
        self.writer.writerow(erow)

    writerow = write


def _date_fmts(date_str, fmts=None):
    """
    Attemps to convert a string formated date into datetime.datetime

    @param date_str: the datetime string
    @type date_str: basestring
    @param fmts: optional list of format strings
    (if None, by default, the following formats will be tried: '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S')
    @type fmts: list

    @raise ValueError: If it was not possible to convert the string for the
    given formats

    @return: datetime.datetime object corresponding to the string formated date

    """
    if not fmts:
        fmts = []
    fmts += ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']
    error = None
    for fmt in fmts:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError, e:
            error = e
    raise ValueError(error)


def validate_header(file_obj):
    """
    This function validates the header of the file which is going to be loaded.

    @param file_obj: file which header is going to be validated
    @type file_obj: file object

    @raise ValueError: When any of the header lines is incorrectly formated

    @return: A five element list containing the file header arguments:
    [str, str, str, datetime.datetime, datetime.datetime]

    """

    ERROR_FILE_HEADER = "Line %d in file header does not start with '#'"
    ERROR_BAD_FORMAT = "No ':' separating the arguments at line: %d"
    ERROR_NO_ARGUMENT = "No argument at line: %d"

    def _parse(line):
        if not line.startswith('#'):
            raise ValueError(ERROR_FILE_HEADER % idx)
        try:
            line_idx = line.index(':')
        except ValueError:
            raise ValueError(ERROR_BAD_FORMAT % idx)
        arg = line[line_idx:].lstrip(': ')
        if not arg:
            raise ValueError(ERROR_NO_ARGUMENT % idx)
        return arg

    args = [_parse(file_obj.readline().strip()) for _ in xrange(5)]

    return args[0:3] + [_date_fmts(x) for x in args[3:]]


def load_dump(file_obj, date_format=None,
              create_logins=True,
              create_projects=True,
              create_project_assocs=True,
              is_api=False):
    """
    Load Dumps for file into the database.

    Preconditions
    =============
    - The file must be structured as one generated by
        L{EffCsvWriter<eff_site.eff.utils.EffCsvWriter>}.
    - The client name included in the file header must exist in the system.
    - The external source name included in the file header must exist in the
        system.

    Description
    ===========
    Before uploading the logs to the system all the existing logs for the given
    external source and client between given dates are deleted. Next a Dump
    object for this upload is created, and all eff logs in the csv file are
    imported to the system with the corresponding date, project, user,
    hours booked, task name and description.

    In case that the create_logins flag is enabled and function call does not
    come from an API call (is_api flag disabled), then all logs which includes
    non existant users are saved to a temp file and the path to it is included
    in the returned tuple.

    In case that the create_projects flag is enabled and there are logs with
    project external id's not found on the system, then these projects are
    created with minimal assumptions about it. The project associations between
    the log user and the recently created project is also created.
    If create_projects is not enabled then a list with non existant projects
    external id's is included in the returned tuple. Also the corresponding
    user-project associations for these logs are returned in a list.

    If create_project_assocs is enabled and there are logs which user-project
    association does not exist, then they are created. If the flag is disabled,
    these associations are included in a list in the returning tuple.

    On any case that a log is not imported (for any of the above mentioned
    reasons), the log is included in a list contained in the returning tuple.


    @param file_obj: from where the records are going to be read
    @type file_obj: file object
    @param date_format: represents the date form (used in strptime)
    to read the date from the date column of the records
    @type date_format: basestring
    @param create_logins: optional argument to determine if non existant
    user external logins should be created
    @type create_logins: bool
    @param create_projects: optional argument to determine if non existant
    projects should be created
    @type create_projects: bool
    @param create_project_assocs: optional argument to determine if non existant
    project-user associations should be created
    @type create_project_assocs: bool
    @param is_api: determines if the function call comes from a view
        (set to False)
    or should be treated as an API call (set to True)
    @type is_api: bool

    @return: Tuple with four elements:
    list of rows not imported, set of external logins not found,
    set of projects not created, set of project associations not created.
    If apply (is_api==False and create_logins==True) the tuple contains a
    fifth element which is the path to the temp file where not imported rows
    are stored.

    """

    ext_src, client, author, from_date, to_date = validate_header(file_obj)

    # If the csv was created with EffCsvWriter,
    # the following objects _should_ exist
    client = Client.objects.get(name=client)
    external_source = ExternalSource.objects.get(name=ext_src)

    # Load all userprofiles so when do not hit the data base
    # in each iteration of the for loop.
    userprofile_dict = dict([(external_id.login, up)
                             for up in UserProfile.objects.all()
                             for external_id in
                             up.externalid_set.filter(source=external_source)
                             ])

    projects_dict = dict([(p.external_id, p)
                          for p in Project.objects.filter(client__name=client)])

    reader = csv.reader(file_obj)

    TimeLog.objects.filter(dump__source=external_source,
                           date__gte=from_date,
                           date__lte=to_date,
                           project__client=client).delete()
    dump = Dump.objects.create(date=date.today(),
                               creator=author,
                               source=external_source)

    # Define a partial function so when don't branch in the loop
    if date_format:
        _partial_date_fmts = lambda x: _date_fmts(x, [date_format])
    else:
        _partial_date_fmts = lambda x: _date_fmts(x)

    n_rows, n_users, n_projects, n_project_assocs = [], set(), set(), set()
    a_rows = []
    for row in reader:
        if not row:
            continue

        lgn = force_unicode(row[2])
        userprofile = userprofile_dict.get(lgn, None)
        if not userprofile:
            #if create_logins or is_api:
            n_users.add(row[2])
            n_rows.append(row)
            a_rows.append(row)
            continue
        user = userprofile.user

        d = _partial_date_fmts(row[0])

        t_proj = projects_dict.get(row[1], None)
        if not t_proj:
            if create_projects:
                t_proj = Project.objects.create(name=row[1],
                                                external_id=row[1],
                                                client=client,
                                                start_date=d)

                passoc = ProjectAssoc.objects.filter(project=t_proj,
                    member=user.get_profile())
                if not passoc:
                    ProjectAssoc.objects.create(project=t_proj,
                                                member=user.get_profile(),
                                                client_rate=0.0,
                                                user_rate=0.0,
                                                from_date=d)

                projects_dict[row[1]] = t_proj
            else:
                n_projects.add(row[1])
                n_project_assocs.add((row[1], user.get_profile()))
                n_rows.append(row)
                continue
        else:
            passoc = ProjectAssoc.objects.filter(project=t_proj,
                member=user.get_profile())
            if not passoc:
                if create_project_assocs:
                    ProjectAssoc.objects.create(project=t_proj,
                                                member=user.get_profile(),
                                                client_rate=0.0,
                                                user_rate=0.0,
                                                from_date=d)
                else:
                    n_project_assocs.add((t_proj.external_id,
                        user.get_profile()))
                    n_rows.append(row)
                    continue

        tl_dict = {'date': d,
                   'project': t_proj,
                   'task_name': row[4],
                   'user': user,
                   'hours_booked': row[3],
                   'description': row[5],
                   'dump': dump
                   }
        TimeLog.objects.create(**tl_dict)

    r_list = [n_rows, n_users, n_projects, n_project_assocs]

    if not is_api and create_logins:
        temp_path = None
        if a_rows:
            temp_path = tempfile.mktemp()
            temp_file = open(temp_path, 'w')

            temp_writer = EffCsvWriter(external_source, client, author,
                temp_file, from_date=from_date, to_date=to_date)

            for row in a_rows:
                row[0] = datetime.strptime(row[0], '%Y-%m-%d')
                row[3] = row[3]
                temp_writer.write(row)

        r_list.append(temp_path)

    return tuple(r_list)
