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

from django.test import TestCase
from unittest import TestSuite, makeSuite
from django.test.client import Client as TestClient
from django.core.urlresolvers import reverse
from pyquery import PyQuery
from decimal import Decimal
from datetime import date, timedelta
from django.db.models import signals
from django.contrib.auth.models import User
from urllib import urlencode

from factories import UserProfileFactory, ProjectFactory, ClientFactory
from factories import ProjectAssocFactory, ExternalSourceFactory, DumpFactory
from factories import TimeLogFactory, AvgHoursFactory


class UserFollowPermsTest(TestCase):

    def setUp(self):

        # Disconnect signals so there's no problem to use UserProfileFactory
        signals.post_save.disconnect(
            dispatch_uid='eff._models.user_profile.create_profile_for_user',
            sender=User)

        self.test_client = TestClient()

        # Create some data for tests
        # A external source
        self.ext_src = ExternalSourceFactory(name='DotprojectMachinalis')
        # A dump
        dump = DumpFactory(date=date(2012, 05, 30), source=self.ext_src)
        # A client
        client = ClientFactory(name='client', external_source=self.ext_src)
        # 2 projects
        project1 = ProjectFactory(name='Fake Project 1', client=client,
                                  external_id='FP1')
        project2 = ProjectFactory(name='Fake Project 2', client=client,
                                  external_id='FP2')
        # A 'watcher' UserProfile, the one who watches others and a projassoc.
        self.watcher = UserProfileFactory(user__username='watcher')
        start_date = date(2012, 01, 01)
        end_date = date(2012, 01, 31)
        AvgHoursFactory(user=self.watcher.user, date=start_date,
                        hours=Decimal('8.00'))
        ProjectAssocFactory(project=project1, member=self.watcher,
                            client_rate=Decimal('0.50'),
                            user_rate=Decimal('0.20'),
                            from_date=start_date,
                            to_date=end_date)
        for d in xrange(5):
            TimeLogFactory(user=self.watcher.user, hours_booked=Decimal('2.00'),
                           date=start_date + timedelta(days=d),
                           project=project1, dump=dump)

        # 5 'watched' UserProfiles, those watched by watcher
        # For each user add projassocs, avghours and some logs.
        start_date = date(2012, 01, 01)
        end_date = date(2012, 01, 31)
        for i in xrange(5):
            user = UserProfileFactory(user__username='test' + str(i))
            self.watcher.watches.add(user.user)
            ProjectAssocFactory(project=project2, member=user,
                                client_rate=Decimal('0.25'),
                                user_rate=Decimal('0.10'), from_date=start_date,
                                to_date=end_date)
            AvgHoursFactory(user=user.user, date=start_date,
                            hours=Decimal('8.00'))
            # Generate some timelogs with specified hours for each user.
            for d in xrange(5):
                TimeLogFactory(user=user.user, hours_booked=Decimal('4.00'),
                               date=start_date + timedelta(days=d),
                               project=project2, dump=dump)

        self.test_client.login(username='watcher', password='watcher')

    def get_response(self, from_date, to_date):
        get_data = urlencode([('from_date', from_date),
                              ('to_date', to_date)])
        url = '%s?%s' % (reverse('eff'), get_data)
        return self.test_client.get(url)

    def test_eff_view_works(self):
        response = self.get_response('2012-01-01', '2012-01-31')
        self.assertEqual(response.status_code, 200)

    def test_followed_users_shows_correctly(self):
        response = self.get_response('2012-01-02', '2012-01-30')
        query = PyQuery(response.content)
        query = query('table#queryTable td.name').text()
        names = map(lambda u: u.username, self.watcher.watches.all())
        names.append('watcher')
        self.assertEqual(query.split(), names)


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(UserFollowPermsTest))
    return suite
