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

from django.contrib.auth.models import User
from django.db.models import signals
from eff._models.user_profile import create_profile_for_user
from django.test import TestCase
from unittest import TestSuite, makeSuite

from factories import UserProfileFactory, ProjectFactory, ClientFactory
from factories import ProjectAssocFactory, ExternalSourceFactory, DumpFactory
from factories import TimeLogFactory
from decimal import Decimal
from eff.models import TimeLog

from datetime import date, timedelta


class HelperTest(TestCase):

    def create_timelogs_for_users(self, n, users_hours, start_date, project):
        # Generate n timelogs with specified hours for each user, from
        # start_date, for specified project
        for d in xrange(n):
            for user, user_hours in users_hours:
                TimeLogFactory(user=user, date=start_date + timedelta(days=d),
                               hours_booked=Decimal(str(user_hours)),
                               project=project)

    def setUp(self):

        # Disconnect signals so there's no problem to use UserProfileFactory
        signals.post_save.disconnect(
            dispatch_uid='eff._models.user_profile.create_profile_for_user',
            sender=User)

        # Create a external source
        self.ext_src = ExternalSourceFactory(name='DotprojectMachinalis')

        #Create a dump
        DumpFactory(date=date(2012, 05, 29), source=self.ext_src)

        # Create 2 user profiles and 1 client.
        self.user1 = UserProfileFactory(user__username='user1')
        self.user2 = UserProfileFactory(user__username='user2')
        self.client = ClientFactory(name='Yet Another Client',
                                    external_source=self.ext_src)

        # Create 2 projects
        project1 = ProjectFactory(name='Fake Project 42', client=self.client,
                                  external_id='FP42', start_date=date.today())
        project2 = ProjectFactory(name='Fake Project 10', client=self.client,
                                  external_id='FP10', start_date=date.today())

        # Add projectassocs
        ProjectAssocFactory(project=project1, member=self.user2,
                            client_rate=Decimal('0.30'),
                            user_rate=Decimal('0.14'),
                            from_date=date(2008, 01, 01),
                            to_date=None)
        ProjectAssocFactory(project=project2, member=self.user1,
                            client_rate=Decimal('0.00'),
                            user_rate=Decimal('0.19'),
                            from_date=date(2010, 9, 16),
                            to_date=date(2010, 9, 30))
        ProjectAssocFactory(project=project2, member=self.user2,
                            client_rate=Decimal('0.00'),
                            user_rate=Decimal('0.19'),
                            from_date=date(2010, 9, 16),
                            to_date=date(2010, 9, 30))
        ProjectAssocFactory(project=project1, member=self.user1,
                            client_rate=Decimal('0.80'),
                            user_rate=Decimal('0.50'),
                            from_date=date(2010, 10, 01),
                            to_date=date(2010, 12, 03))
        ProjectAssocFactory(project=project1, member=self.user2,
                            client_rate=Decimal('0.60'),
                            user_rate=Decimal('0.19'),
                            from_date=date(2010, 10, 01),
                            to_date=date(2010, 12, 03))
        ProjectAssocFactory(project=project1, member=self.user1,
                            client_rate=Decimal('0.00'),
                            user_rate=Decimal('0.00'),
                            from_date=date(2012, 01, 01),
                            to_date=date(2012, 05, 8))

        # Add logs for users
        # 2 logs not contained by any projectassoc period.
        TimeLogFactory(user=self.user1.user, date=date(2012, 05, 10),
                       hours_booked=Decimal('15.0'), project=project1)
        TimeLogFactory(user=self.user1.user, date=date(2010, 9, 30),
                       hours_booked=Decimal('5.0'), project=project1)

        # A log in the limit (to_date) of a projectassoc
        TimeLogFactory(user=self.user1.user, date=date(2010, 9, 30),
                       hours_booked=Decimal('3.5'), project=project2)

        # More logs for each projectassoc period.
        # project1 -> user1 hours: 45*8, user2 hours: 45*3.5
        self.create_timelogs_for_users(45, [(self.user1.user, 8.0),
                                            (self.user2.user, 3.5)
                                            ], date(2010, 10, 01), project1)

        # project1 -> user1 hours: 8*5
        self.create_timelogs_for_users(8, [(self.user1.user, 5.00)],
                                       date(2012, 01, 01), project1)

        # project2 -> user1 hours: 15*4.5, user2 hours: 15*6.5
        self.create_timelogs_for_users(15, [(self.user1.user, 4.5),
                                            (self.user2.user, 6.5)
                                            ], date(2010, 9, 16), project2)

        # project1 -> user2 hours: 15*4
        self.create_timelogs_for_users(15, [(self.user2.user, 4.0)],
                                       date(2008, 01, 01), project1)

    def tearDown(self):
        # re connect signals
        signals.post_save.connect(
            create_profile_for_user, sender=User,
            dispatch_uid='eff._models.user_profile.create_profile_for_user')


class UserReportTest(HelperTest):

    def test_get_summary_per_project_limit1(self):
        # Tests that hours are reported when from_date is equal to to_date of
        # a projectassoc period.
        report = TimeLog.get_summary_per_project(self.user1, '2010-09-30',
                                                 '2010-10-02', True)
        expected = [
            (self.ext_src, u'Fake Project 10', True, Decimal('8.000'),
             Decimal('0.19')),
            (self.ext_src, u'Fake Project 42', True, Decimal('5.000'),
             Decimal('0')),
            (self.ext_src, u'Fake Project 42', True, Decimal('16.000'),
             Decimal('0.50'))
            ]
        self.assertEqual(expected, list(report))

    def test_get_summary_per_project_limit2(self):
        # Tests that hours are reported when from_date is equal to from_date of
        # a projectassoc period.
        report = TimeLog.get_summary_per_project(self.user1, '2010-09-16',
                                                 '2010-09-18', True)
        expected = [
            (self.ext_src, u'Fake Project 10', True, Decimal('13.500'),
             Decimal('0.19'))
            ]
        self.assertEqual(expected, list(report))

    def test_get_summary_per_project_limit3(self):
        # Tests that hours are reported when to_date is equal to from_date of
        # a projectassoc period.
        report = TimeLog.get_summary_per_project(self.user1, '2010-09-29',
                                                 '2010-10-01', True)
        expected = [
            (self.ext_src, u'Fake Project 10', True, Decimal('12.500'),
             Decimal('0.19')),
            (self.ext_src, u'Fake Project 42', True, Decimal('5.000'),
             Decimal('0.00')),
            (self.ext_src, u'Fake Project 42', True, Decimal('8.000'),
             Decimal('0.50'))
            ]
        self.assertEqual(expected, list(report))

    def test_get_summary_per_project_limit4(self):
        # Tests that hours are reported when to_date is equal to to_date of
        # a projectassoc period.
        report = TimeLog.get_summary_per_project(self.user1, '2010-09-28',
                                                 '2010-09-30', True)
        expected = [
            (self.ext_src, u'Fake Project 10', True, Decimal('17.000'),
             Decimal('0.19')),
            (self.ext_src, u'Fake Project 42', True, Decimal('5.000'),
             Decimal('0.00'))
            ]
        self.assertEqual(expected, list(report))

    def test_get_summary_per_project_all_hours1(self):
        # Tests that ALL hours are reported, including those with rate 0, that
        # is, hours logged within a projectassoc period with rate 0, and hours
        # logged in days not contained by any projectassoc period.
        report = TimeLog.get_summary_per_project(self.user1, '2008-01-01',
                                                 '2012-05-10', True)
        expected = [
            (self.ext_src, u'Fake Project 10', True, Decimal('71.000'),
             Decimal('0.19')),
            (self.ext_src, u'Fake Project 42', True, Decimal('60.000'),
             Decimal('0.00')),
            (self.ext_src, u'Fake Project 42', True, Decimal('360.000'),
             Decimal('0.50'))
            ]
        self.assertEqual(expected, list(report))

    def test_get_summary_per_project_all_hours2(self):
        # Same as previous test, plus tests all works fine with a projassoc
        # with to_date not set.
        report = TimeLog.get_summary_per_project(self.user2, '2008-01-01',
                                                 '2012-05-10', True)
        expected = [
            (self.ext_src, u'Fake Project 10', True, Decimal('97.500'),
             Decimal('0.19')),
            (self.ext_src, u'Fake Project 42', True, Decimal('60.000'),
             Decimal('0.14')),
            (self.ext_src, u'Fake Project 42', True, Decimal('157.500'),
             Decimal('0.19'))
            ]
        self.assertEqual(expected, list(report))


class ClientReportTest(HelperTest):

    def test_get_client_summary_per_project_limit1(self):
        # Tests that hours are reported when from_date is equal to to_date of
        # a projectassoc period.
        report = TimeLog.get_client_summary_per_project(self.client,
                                                        date(2010, 9, 30),
                                                        date(2010, 10, 2),
                                                        True)
        expected = {u'FP42': [(u'user1', Decimal('5.000'), Decimal('0.00')),
                              (u'user1', Decimal('16.000'), Decimal('0.80')),
                              (u'user2', Decimal('7.000'), Decimal('0.60'))
                              ],
                    u'FP10': [(u'user1', Decimal('8.000'), Decimal('0.00')),
                              (u'user2', Decimal('6.500'), Decimal('0.00'))]
                    }

        self.assertEqual(expected, report)

    def test_get_client_summary_per_project_limit2(self):
        # Tests that hours are reported when from_date is equal to from_date of
        # a projectassoc period.
        report = TimeLog.get_client_summary_per_project(self.client,
                                                        date(2010, 9, 16),
                                                        date(2010, 9, 18),
                                                        True)
        expected = {u'FP10': [(u'user1', Decimal('13.500'), Decimal('0.00')),
                              (u'user2', Decimal('19.500'), Decimal('0.00'))]
                    }
        self.assertEqual(expected, report)

    def test_get_client_summary_per_project_limit3(self):
        # Tests that hours are reported when to_date is equal to from_date of
        # a projectassoc period.
        report = TimeLog.get_client_summary_per_project(self.client,
                                                        date(2010, 9, 29),
                                                        date(2010, 10, 1),
                                                        True)
        expected = {u'FP42': [(u'user1', Decimal('5.000'), Decimal('0.00')),
                              (u'user1', Decimal('8.000'), Decimal('0.80')),
                              (u'user2', Decimal('3.500'), Decimal('0.60'))],
                    u'FP10': [(u'user1', Decimal('12.500'), Decimal('0.00')),
                              (u'user2', Decimal('13.000'), Decimal('0.00'))]
                    }
        self.assertEqual(expected, report)

    def test_get_client_summary_per_project_limit4(self):
        # Tests that hours are reported when to_date is equal to to_date of
        # a projectassoc period.
        report = TimeLog.get_client_summary_per_project(self.client,
                                                        date(2010, 9, 28),
                                                        date(2010, 9, 30),
                                                        True)
        expected = {u'FP10': [(u'user1', Decimal('17.000'), Decimal('0.00')),
                              (u'user2', Decimal('19.500'), Decimal('0.00'))],
                    u'FP42': [(u'user1', Decimal('5.000'), Decimal('0.00'))]
                    }
        self.assertEqual(expected, report)

    def test_get_client_summary_per_project_all_hours1(self):
        # Tests that ALL hours are reported, including those with rate 0, that
        # is, hours logged within a projectassoc period with rate 0, and hours
        # logged in days not contained by any projectassoc period.
        report = TimeLog.get_client_summary_per_project(self.client,
                                                        date(2010, 9, 01),
                                                        date(2012, 5, 10),
                                                        True)
        expected = {u'FP42': [(u'user1', Decimal('60.000'), Decimal('0.00')),
                              (u'user1', Decimal('360.000'), Decimal('0.80')),
                              (u'user2', Decimal('157.500'), Decimal('0.60'))],
                    u'FP10': [(u'user1', Decimal('71.000'), Decimal('0.00')),
                              (u'user2', Decimal('97.500'), Decimal('0.00'))]
                    }
        self.assertEqual(expected, report)

    def test_get_client_summary_per_project_all_hours2(self):
        # Same as previous test, plus tests all works fine with a projassoc
        # with to_date not set.
        report = TimeLog.get_client_summary_per_project(self.client,
                                                        date(2008, 01, 01),
                                                        date(2012, 05, 10),
                                                        True)
        expected = {u'FP42': [(u'user1', Decimal('60.000'), Decimal('0.00')),
                              (u'user1', Decimal('360.000'), Decimal('0.80')),
                              (u'user2', Decimal('157.500'), Decimal('0.60')),
                              (u'user2', Decimal('60.000'), Decimal('0.30')),
                              ],
                    u'FP10': [(u'user1', Decimal('71.000'), Decimal('0.00')),
                              (u'user2', Decimal('97.500'), Decimal('0.00'))]
                    }
        self.assertEqual(expected, report)


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(UserReportTest))
    suite.addTest(makeSuite(ClientReportTest))
    return suite
