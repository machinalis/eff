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
from django.contrib.auth.models import User
from django.db.models import signals
from django.core.urlresolvers import reverse
from pyquery import PyQuery

from urllib import urlencode
from factories import (UserFactory, ClientProfileFactory, UserProfileFactory,
                       AdminFactory)


class HelperTest(TestCase):

    def setUp(self):

        # Disconnect signals so there's no problem to use UserProfileFactory
        signals.post_save.disconnect(
            dispatch_uid='eff._models.user_profile.create_profile_for_user',
            sender=User)

        self.test_client = TestClient()


class ClientProfileTest(HelperTest):

    def setUp(self):
        super(ClientProfileTest, self).setUp()

        # Create a Client User.
        self.client = UserFactory(username='client')
        self.up = ClientProfileFactory(user=self.client)
        self.test_client.login(username=self.client.username,
                               password=self.client.username)

    def test_login_redirects_to_client_home(self):
        self.test_client.logout()
        url = reverse('login')
        post_data = {'username': self.client.username,
                     'password': self.client.username}
        response = self.test_client.post(url, post_data, follow=True)
        home = response.redirect_chain[1]
        self.assertEqual(home, ('http://testserver/clients/home/', 302))

    def test_login_failure_shows_an_error_for_client(self):
        self.test_client.logout()
        url = reverse('login')
        post_data = {'username': self.client.username,
                     'password': 'NotApassWord'}
        response = self.test_client.post(url, post_data, follow=True)
        query = PyQuery(response.content)
        error = query('div p.error').text()
        error_msg = "Sorry, that's not a valid username or password"
        self.assertEqual(error, error_msg)


class UserProfileTest(HelperTest):

    def setUp(self):
        super(UserProfileTest, self).setUp()

        # Create a Default User.
        self.user = UserFactory(username='test')
        self.up = UserProfileFactory(user=self.user)
        self.test_client.login(username=self.user.username,
                               password=self.user.username)
        self.admin = AdminFactory(username='admin')

    def test_user_can_see_profile_details(self):
        url = reverse('profiles_detail',
                      kwargs={'username': self.user.username})
        response = self.test_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_can_only_see_own_profile(self):
        user = UserFactory(username='test2')
        url = reverse('profiles_detail',
                      kwargs={'username': user.username})
        response = self.test_client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_admin_user_can_see_all_profiles(self):
        self.test_client.login(username=self.admin.username,
                               password=self.admin.username)
        url = reverse('profiles_detail',
                      kwargs={'username': self.user.username})
        response = self.test_client.get(url)
        self.assertEqual(response.status_code, 200)
        client = ClientProfileFactory(user=UserFactory(username='client'))
        url = reverse('profiles_detail',
                      kwargs={'username': client.user.username})
        response = self.test_client.get(url)
        self.assertEqual(response.status_code, 200)


class ClientPermissionsTest(HelperTest):

    def setUp(self):
        super(ClientPermissionsTest, self).setUp()
        # Create a Client User.
        self.client = UserFactory(username='client')
        self.up = ClientProfileFactory(user=self.client)
        self.test_client.login(username=self.client.username,
                               password=self.client.username)

    def get_response(self, url_name, args=None, kwargs=None, data=None):
        if args:
            url = reverse(url_name, args=args)
        elif kwargs:
            url = reverse(url_name, kwargs=kwargs)
        else:
            url = reverse(url_name)

        if data:
            get_data = urlencode(data)
            url = '%s?%s' % (url, get_data)

        return self.test_client.get(url, follow=True)

    def test_client_can_access_eff_root(self):
        response = self.get_response('root')
        self.assertEqual(response.status_code, 200)

    def test_client_can_access_eff_login(self):
        response = self.get_response('login')
        self.assertEqual(response.status_code, 200)

    def test_client_can_access_clients_home(self):
        response = self.get_response('profiles_detail',
                                 kwargs={'username': 'client'})
        self.assertEqual(response.status_code, 200)

    def test_client_cant_access_eff_report(self):
        response = self.get_response('eff_report', args=['client'],
                                 data=[('from_date', '2010-01-01'),
                                       ('to_date', '2010-01-01')])
        self.assertEqual(response.status_code, 200)


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(ClientProfileTest))
    suite.addTest(makeSuite(UserProfileTest))
    suite.addTest(makeSuite(ClientPermissionsTest))
    return suite
