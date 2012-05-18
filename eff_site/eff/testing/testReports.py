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

import factories


class HelperTest(TestCase):

    def setUp(self):

        # Create 2 users and 1 client.
        UserFactory(username='user1')
        UserFactory(username='user2')
        ClientFactory(name='client1')


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(ClientReportTest))
    suite.addTest(makeSuite(UserReportTest))
    return suite
