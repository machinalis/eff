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

from zope.testbrowser.browser import Browser
from eff_site.eff.utils import EffCsvWriter


class Tutos(object):

    csv_header = ('project_id,log_id,log_parent_id,'
                  'date,hours,description,worker,state,'
                  'project_name, proyect_type, bogus\n')

    def __init__(self, url, username, password, projects=None):
        self._url = url
        self._username = username
        self._password = password
        self._projects = projects

    def fetch_data(self):
        url, username, password = self._url, self._username, self._password

        login_url = '/tutos/php/bookinginserter/login.php'
        showteamhours_url = '/tutos/php/bookinginserter/showteamhours.php'
        
        browser = Browser(url)

        browser.getControl(name='username').value = username
        browser.getControl(name='password').value = password
        browser.getForm(action=login_url).submit()

        browser.getLink(url='showteamhours.php').click()
        start_date_value = browser.getControl(name='startdate').options[0]
        browser.getControl(name='startdate').value = [start_date_value]
        end_date_value = browser.getControl(name='enddate').options[-1]
        browser.getControl(name='enddate').value = [end_date_value]
        browser.getForm(action=showteamhours_url).submit()

        self._from_date = start_date_value
        self._to_date  = end_date_value
        self._data = browser.contents

    def get_dates(self):
        if hasattr(self, '_from_date') and hasattr(self, '_to_date'):
            return self._from_date, self._to_date
        return None

    def _process_data(self):
        contents = self._data.decode('latin1').encode('utf-8')

        # Tutos doesn't escape quotes from the data that can contain 
        # quotes (such as the log description), so you can't read it as a csv :(
        # We made a case-by-case cleanup. Stupid, but effective.
        old = '"Set error:"is gereserveerd, niet met onderstreepteken zou mo"'
        new = '"Set error: is gereserveerd, niet met onderstreepteken zou mo"' 
        contents = contents.replace(old, new)

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

    if not (source.fetch_url and source.username and source.password):
        raise ValueError("The source in the db is missing information")

    tutos = Tutos(source.fetch_url, source.username, source.password)
    tutos.fetch_data()
    f, t = tutos.get_dates()

    from_date = datetime.strptime(f, "%Y%m%d%H%M%S")
    to_date = datetime.strptime(t, "%Y%m%d%H%M%S")
    
    writer = EffCsvWriter(source, client, author, _file,
                          from_date=from_date,
                          to_date=to_date)
    tutos.write_csv(writer=writer)


if __name__ == '__main__':
    """
    This is just for testing
    """
    
    args = sys.argv[1:]
    
    if len(args) != 3:
        print "Usage: $ tutos.py <url> <username> <password>"
        sys.exit(0)

    url, username, password = args
    tutos = Tutos(url, username, password)
    tutos.fetch_data()
    print tutos.get_dates()
    tutos.write_csv()
