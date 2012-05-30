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
from datetime import date

from factories import UserProfileFactory, ProjectFactory, ClientFactory
from factories import ProjectAssocFactory, ExternalSourceFactory, DumpFactory
from factories import TimeLogFactory


class UserFollowPermsTest(TestCase):

    def create_timelogs_for_users(self, n, users_hours, start_date, project):
        # Generate n timelogs with specified hours for each user, from
        # start_date, for specified project
        for d in xrange(n):
            for user, user_hours in users_hours:
                TimeLogFactory(user=user, date=start_date + timedelta(days=d),
                               hours_booked=Decimal(str(user_hours)),
                               project=project)

    def setUp(self):

        self.test_client = TestClient()

        # Create some data for tests
        # A external source
        self.ext_src = ExternalSourceFactory(name='DotprojectMachinalis')
        # A dump
        DumpFactory(date=date(2012, 05, 30), source=self.ext_src)
        # A client
        client = ClientFactory(name='client', external_source=self.ext_src)
        # 2 projects
        project1 = ProjectFactory(name='Fake Project 1', client=client,
                                  external_id='FP1')
        project2 = ProjectFactory(name='Fake Project 2', client=client,
                                  external_id='FP2')
        # A 'watcher' UserProfile, the one who watches others and a projassoc.
        self.watcher = UserProfileFactory(username='watcher')
        ProjectAssocFactory(project=project1, member=self.watcher,
                            client_rate=Decimal('0.30'),
                            user_rate=Decimal('0.14'),
                            from_date=date(2012, 01, 01),
                            to_date=date(2012, 01, 31))

        self.watches = []
        # 5 'watched' UserProfiles, those watched by watcher
        # For each user add projassocs and some logs.
        for i in xrange(5):
            user = self.watches.append(
                UserProfileFactory(username='test' + str(i)))
            ProjectAssocFactory(project=project2, member=user,
                                client_rate=Decimal('0.00'),
                                user_rate=Decimal('0.19'),
                                from_date=date(2012, 01, 01),
                                to_date=date(2012, 01, 31))
def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(UserFollowPermsTest))
    return suite
