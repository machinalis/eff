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

import csv
import sys

from StringIO import StringIO
from datetime import datetime

import mechanize

from dateutil.relativedelta import relativedelta
import calendar

class Jira(object):

    csv_header = ('timetrack_id','timetrack_parentid','timetrack_volume',
                  'timetrack_start','timetrack_end','timetrack_description',
                  'timetrack_cph','timetrack_vtime','timetrack_creation',
                  'person_id','person_loginname','person_isadmin',
                  'person_isdisabled','person_role','timetrack_projectcph',
                  'timetrack_costs','timetrack_state','project_name',
                  'project_departments','project_types',
                  'project_implementation','project_state','timetrack_origin')

    def __init__(self, url, username, password,
                 from_date=None, to_date=None, projects=None):
        self._url = url
        self._username = username
        self._password = password
        self._projects = projects
        self._from_date = from_date
        self._to_date = to_date

    def _calculate_date_range(self, from_date, to_date):
        """
        >>> from jira import Jira
        >>> url, username, password = "", "", ""  # Doesn't matter for this test
        >>> from datetime import datetime
        >>> f = datetime(2009, 9, 1)
        >>> t = datetime(2010, 10, 14)
        >>> j = Jira(url, username, password, f, t)
        >>> j._calculate_date_range(f, t)
        (datetime.datetime(2009, 9, 1, 0, 0), datetime.datetime(2010, 11, 1, 0, 0))

        >>> f = datetime(2009, 1, 12)
        >>> t = datetime(2010, 9, 1)
        >>> j._calculate_date_range(f, t)
        (datetime.datetime(2009, 1, 1, 0, 0), datetime.datetime(2010, 10, 1, 0, 0))


        >>> f = datetime(2009, 1, 10)
        >>> t = datetime(2011, 1, 4)
        >>> j._calculate_date_range(f, t)
        (datetime.datetime(2009, 1, 1, 0, 0), datetime.datetime(2011, 2, 1, 0, 0))

        >>> f = datetime(2009, 2, 10)
        >>> t = datetime(2010, 3, 15)
        >>> j._calculate_date_range(f, t)
        (datetime.datetime(2009, 2, 1, 0, 0), datetime.datetime(2010, 4, 1, 0, 0))
        """

        startdate = datetime(from_date.year, from_date.month, 1)
        rd = relativedelta(to_date, startdate)
        if rd.years > 0 or rd.months > 2:
            year, month = to_date.year, to_date.month,
            enddate = datetime(year, month, 1) + relativedelta(months=1)
        else:
            enddate = startdate + relativedelta(months=2)

        return (startdate, enddate) 


    def fetch_data(self):
        url, username, password = self._url, self._username, self._password
        
        br = mechanize.Browser()
        br.add_password(url, username, password)
        br.set_handle_robots(False)
        r = br.open(url)
        br.select_form(nr=0)

        startdate, enddate = self._calculate_date_range(self._from_date,
                                                        self._to_date)
        
        from_date = startdate.strftime("%Y%m%d%H%M%S")
        to_date = enddate.strftime("%Y%m%d%H%M%S")


        # values accepted are for example:
        # 20060101000000
        # 20070901000000
        # 20090601000000 
        br["startdate"] = (from_date,)
        br["enddate"] = (to_date,)
        r = br.submit()
        self._data = r.read()
 
    def set_dates(self, from_date, to_date):
        self._from_date = from_date
        self._to_date = to_date

    def _process_data(self):
        contents = self._data.decode('latin1').encode('utf-8')
        readable_csv = csv.reader(StringIO(contents))
        csv_headers = readable_csv.next()

        while True:
            try:
                line = dict(zip(csv_headers, readable_csv.next()))
                t_date = datetime.strptime(line['timetrack_vtime'],
                                           '%Y-%m-%d %H:%M:%S').date()
                if not line['project_name'].split():
                    continue
                project_external_id = line['project_name'].split()[0]
                t_proj = project_external_id
                
                if self._projects and (t_proj not in self._projects):
                    continue 

                t_line = (t_date, t_proj, line['person_loginname'],
                          float(line['timetrack_volume']),
                          line['project_types'], line['timetrack_description'])
                yield t_line
            except StopIteration:
                break

    def write_csv(self, writer=None):

        if not hasattr(self, '_data'):
            return None
        
        if writer:
            csv_writer = writer
        else:
            fd = open('tutos_output.csv', 'w')
            csv_writer = csv.writer(fd)
        
        for row in self._process_data():
            csv_writer.writerow(row)

def fetch_all(source, client, author, from_date, to_date, _file):   
    from sitio.eff.utils import EffCsvWriter

    if not (source.fetch_url and source.username and source.password):
        # This error is raised because the ExternalSource was created
        # without the relevant information needed to fetch the data
        raise ValueError("The source in the db is missing information")
    
    j = Jira(source.fetch_url, source.username, source.password,
             from_date, to_date)
    j.fetch_data()
    writer = EffCsvWriter(source, client, author, _file,
                          from_date=from_date,
                          to_date=to_date)
    j.write_csv(writer=writer)


if __name__ == '__main__':
    """
    This is just for testing
    """
    import doctest
    doctest.testmod()

    url, username, password = "", "", ""  # Put real data here to test.
    j = Jira(url, username, password, 
             datetime(2011, 1, 1), datetime(2011, 1, 31))
    j.fetch_data()
    j.write_csv()
