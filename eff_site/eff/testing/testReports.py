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

from factories import *
from decimal import Decimal


class HelperTest(TestCase):

    def setUp(self):

        # Create 2 user profiles and 1 client.
        user1 = UserProfileFactory(username='user1')
        user2 = UserProfileFactory(username='user2')
        client = ClientFactory(name='client1')

        # Create 2 projects
        project1 = ProjectFactory(client=client)
        project2 = ProjectFactory(client=client)

        # Add projectassocs
        ProjectAssocFactory(project=project2, member=user1,
                            client_rate = Decimal('0.00'),
                            user_rate = Decimal('0.19'),
                            from_date = date.(2010, 9, 16),
                            to_date = date.(2010, 09, 30))
        ProjectAssocFactory(project=project1, member=user1,
                            client_rate = Decimal('0.80'),
                            user_rate = Decimal('0.50'),
                            from_date = date.(2010, 10, 01),
                            to_date = date.(2010, 12, 03))
        ProjectAssocFactory(project=project1, member=user1,
                            client_rate = Decimal('0.00'),
                            user_rate = Decimal('0.00'),
                            from_date = date.(2012, 01, 01),
                            to_date = date.(2012, 05, 08))
        ProjectAssocFactory(project=project2, member=user2,
                            client_rate = Decimal('0.00'),
                            user_rate = Decimal('0.19'),
                            from_date = date.(2010, 09, 16),
                            to_date = date.(2010, 09, 30))
        ProjectAssocFactory(project=project1, member=user2,
                            client_rate = Decimal('0.60'),
                            user_rate = Decimal('0.19'),
                            from_date = date.(2010, 10, 01),
                            to_date = date.(2010, 12, 03))

        # Add logs for users
        # 2 logs not contained by any projectassoc period.
        TimeLogFactory(user=user1, date=date(2012, 05, 10),
                       hours_booked = Decimal('10.0'), project=project1)
        TimeLogFactory(user=user1, date=date(2012, 05, 09),
                       hours_booked = Decimal('5.0'), project=project1)
        # A log in the limit (to_date) of a projectassoc
        TimeLogFactory(user=user1, date=date(2010, 09, 30),
                       hours_booked = Decimal('5.0'), project=project1)
        # More logs for each projectassoc period.
        # user1 hours: 45*8, user2 hours: 45*3.5
        for d in range(45):
            TimeLogFactory(user=user1, date=date(2010, 10, 01) + \
                           timedelta(days=d),
                           hours_booked = Decimal('8.0'), project=project1)
            TimeLogFactory(user=user1, date=date(2010, 10, 01) + \
                           timedelta(days=d),
                           hours_booked = Decimal('3.5'), project=project1)
        # hours: 8*5
        for d in range(8):
            TimeLogFactory(user=user1, date=date(2012, 01, 01) + \
                           timedelta(days=d),
                           hours_booked = Decimal('5.0'), project=project1)
        # user1 hours: 15*4.5, user2 hours: 15*6.5
        for d in range(15):
            TimeLogFactory(user=user1, date=date(2010, 9, 16) + \
                           timedelta(days=d),
                           hours_booked = Decimal('4.5'), project=project2)
            TimeLogFactory(user=user2, date=date(2010, 9, 16) + \
                           timedelta(days=d),
                           hours_booked = Decimal('6.5'), project=project2)
            
        
#class ClientReport(HelperTest):

class UserReport(HelperTest):
    
    def test_(self):
        # función a teastear: get_summary_per_project


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(ClientReportTest))
    suite.addTest(makeSuite(UserReportTest))
    return suite
