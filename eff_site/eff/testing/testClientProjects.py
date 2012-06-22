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
from django.db.models import signals
from eff._models.user_profile import create_profile_for_user
from django.contrib.auth.models import User


from factories import UserProfileFactory, ProjectFactory, ClientFactory
from factories import ProjectAssocFactory, ExternalSourceFactory, UserFactory
from factories import ClientProfileFactory


class HelperTest(TestCase):
    def setUp(self):
        # Disconnect signals so there's no problem to use UserProfileFactory
        signals.post_save.disconnect(
            dispatch_uid='eff._models.user_profile.create_profile_for_user',
            sender=User)

        self.test_client = TestClient()

        # Create some data for tests
        # An external source
        self.ext_src = ExternalSourceFactory(name='DotprojectMachinalis')

        # A company client
        client = ClientFactory(name='company', external_source=self.ext_src)
        # A Client User.
        self.client = UserFactory(username='client')
        self.up = ClientProfileFactory(user=self.client, company=client)
        self.test_client.login(username=self.client.username,
                               password=self.client.username)

        # 3 projects. 2 billiable (HOUR, FIXED), and 1 not billiable.
        project1 = ProjectFactory(name='FakeProject1', client=client,
                                  external_id='FP1', billable=True,
                                  billing_type='HOUR')
        ProjectFactory(name='FakeProject2', client=client, external_id='FP2',
                       billable=True, billing_type='FIXED')
        ProjectFactory(name='FakeProject3', client=client, external_id='FP3',
                       billable=False)
        self.b_projects = 'FakeProject1 FakeProject2'

        # 1 project not related to this client.
        ProjectFactory(name='Fake Project 4', external_id='FP4', billable=False)

        # Some members for project 1.
        start_date = date(2012, 01, 01)
        end_date = date(2012, 01, 31)
        for i in xrange(5):
            user = UserProfileFactory(user__username='test' + str(i))
            ProjectAssocFactory(project=project1, member=user,
                                client_rate=Decimal('0.25'),
                                user_rate=Decimal('0.10'), from_date=start_date,
                                to_date=end_date)

        # 1 user not related to any project
        UserProfileFactory(user__username='test' + str(i + 1))

    def tearDown(self):
        # reconnect signals
        signals.post_save.connect(
            create_profile_for_user, sender=User,
            dispatch_uid='eff._models.user_profile.create_profile_for_user')


class ClientProjectsTest(HelperTest):
    def test_projects_view_works(self):
        response = self.test_client.get(reverse('clients_projects'))
        self.assertEqual(response.status_code, 200)

    def test_not_billiable_projects_not_shown(self):
        response = self.test_client.get(reverse('clients_projects'))
        query = PyQuery(response.content)
        query = query('table#queryTable td.name').text()
        self.assertNotIn('FakeProject3', set(query.split()))

    def test_all_billiable_projects_shown(self):
        response = self.test_client.get(reverse('clients_projects'))
        query = PyQuery(response.content)
        query = query('table#queryTable td.name').text()
        self.assertEqual(set(('FakeProject1', 'FakeProject2')),
                         set(query.split()))

    def test_members_for_each_project_shown(self):
        response = self.test_client.get(reverse('clients_projects'))
        query = PyQuery(response.content)
        members = query('table#queryTable td.members').text()
        names = map(lambda i: 'test' + str(i), range(5))
        s_members = set(map(lambda n: n + ' ' + n + ' (' + n + ')', names))
        self.assertEqual(s_members, set(members.split(' | ')))

    def test_billing_types_for_each_project_shown(self):
        response = self.test_client.get(reverse('clients_projects'))
        query = PyQuery(response.content)
        query = query('table#queryTable td.type').text()
        self.assertEqual(set(('HOUR', 'FIXED')), set(query.split()))

    def test_no_projects_for_new_client(self):
        u_client = UserFactory(username='newClient')
        company = ClientFactory(name='newCompany', external_source=self.ext_src)
        ClientProfileFactory(user=u_client, company=company)
        self.test_client.login(username=u_client.username,
                               password=u_client.username)
        response = self.test_client.get(reverse('clients_projects'))
        query = PyQuery(response.content)
        msg = query('div p').text()
        self.assertEqual(msg, 'No projects found')


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(ClientProjectsTest))
    return suite
