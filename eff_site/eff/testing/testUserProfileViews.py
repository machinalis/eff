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
from eff._models.user_profile import create_profile_for_user
from django.core.urlresolvers import reverse
from pyquery import PyQuery

from urllib import urlencode
from factories import (UserFactory, ClientProfileFactory, UserProfileFactory,
                       AdminFactory, ClientFactory)


class HelperTest(TestCase):

    def setUp(self):

        # Disconnect signals so there's no problem to use UserProfileFactory
        signals.post_save.disconnect(
            dispatch_uid='eff._models.user_profile.create_profile_for_user',
            sender=User)

        self.test_client = TestClient()

    def tearDown(self):
        # re connect signals
        signals.post_save.connect(
            create_profile_for_user, sender=User,
            dispatch_uid='eff._models.user_profile.create_profile_for_user')


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

    def test_client_can_modify_email_in_profiles_edit(self):
        url = reverse('profiles_edit')
        response = self.test_client.get(url)
        self.assertEqual(response.status_code, 200)
        post_data = {'first_name': self.client.first_name,
                     'last_name': self.client.last_name,
                     'email': 'newEmail@test.com',
                     'handles-TOTAL_FORMS': '1',
                     'handles-INITIAL_FORMS': '0',
                     'handles-MAX_NUM_FORMS': ''}
        self.test_client.post(url, post_data, follow=True)
        client = User.objects.get(username=self.client.username)
        self.assertEqual(client.email, 'newEmail@test.com')

    def test_client_email_field_required_in_profiles_edit(self):
        url = reverse('profiles_edit')
        response = self.test_client.get(url)
        self.assertEqual(response.status_code, 200)
        post_data = {'first_name': self.client.first_name,
                     'last_name': self.client.last_name,
                     'email': '',
                     'handles-TOTAL_FORMS': '1',
                     'handles-INITIAL_FORMS': '0',
                     'handles-MAX_NUM_FORMS': ''}
        response = self.test_client.post(url, post_data)
        query = PyQuery(response.content)
        error = query('ul.errorlist').text()
        self.assertEqual(error, 'This field is required.')

    def test_client_email_must_be_unique_in_profiles_edit(self):
        # Create another Client User.
        client = UserFactory(username='client2', email='client2@test.com')
        ClientProfileFactory(user=client)
        url = reverse('profiles_edit')
        response = self.test_client.get(url)
        self.assertEqual(response.status_code, 200)
        post_data = {'first_name': self.client.first_name,
                     'last_name': self.client.last_name,
                     'email': 'client2@test.com',
                     'handles-TOTAL_FORMS': '1',
                     'handles-INITIAL_FORMS': '0',
                     'handles-MAX_NUM_FORMS': ''}
        response = self.test_client.post(url, post_data)
        query = PyQuery(response.content)
        error = query('ul.errorlist').text()
        self.assertEqual(error, 'Email address must be unique.')


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
        # A company client
        client = ClientFactory(name='company')
        # A Client User.
        self.client = UserFactory(username='client')
        self.up = ClientProfileFactory(user=self.client, company=client)
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

        return self.test_client.get(url)

    def test_client_can_access_eff_root(self):
        response = self.get_response('root')
        self.assertEqual(response.status_code, 302)

    def test_client_can_access_eff_login(self):
        response = self.get_response('login')
        self.assertEqual(response.status_code, 200)

    def test_client_can_logout(self):
        response = self.get_response('logout')
        self.assertEqual(response.status_code, 200)

    def test_client_can_access_clients_home(self):
        response = self.get_response('clients_home')
        self.assertEqual(response.status_code, 200)

    def test_client_can_access_clients_profiles_detail(self):
        response = self.get_response('profiles_detail',
                                 kwargs={'username': 'client'})
        self.assertEqual(response.status_code, 200)

    def test_client_can_access_profiles_edit(self):
        response = self.get_response('profiles_edit')
        self.assertEqual(response.status_code, 200)

    def test_client_can_access_password_reset(self):
        response = self.get_response('password_reset')
        self.assertEqual(response.status_code, 200)

    def test_client_can_access_password_reset_done(self):
        response = self.get_response('password_reset_done')
        self.assertEqual(response.status_code, 200)

    def test_client_can_access_password_reset_complete(self):
        response = self.get_response('password_reset_complete')
        self.assertEqual(response.status_code, 200)

    def test_client_can_access_password_change(self):
        response = self.get_response('password_change')
        self.assertEqual(response.status_code, 200)

    def test_client_can_access_password_change_done(self):
        response = self.get_response('password_change_done')
        self.assertEqual(response.status_code, 200)

    def test_client_can_access_eff_clients_projects(self):
        response = self.get_response('clients_projects')
        self.assertEqual(response.status_code, 200)

    def test_client_cant_access_checkperms(self):
        response = self.get_response('checkperms', args=['client'])
        self.assertRedirects(response,
                             '/accounts/login/?next=/checkperms/client/')

    def test_client_cant_access_update_hours(self):
        response = self.get_response('update_hours', args=['client'])
        self.assertRedirects(response,
                             '/accounts/login/?next=/updatehours/client/')

    def test_client_cant_access_eff(self):
        response = self.get_response('eff')
        self.assertRedirects(response,
                             'accounts/login/?next=/efi/')

    def test_client_cant_access_eff_previous_week(self):
        response = self.get_response('eff_previous_week')
        self.assertRedirects(response,
                             'accounts/login/?next=/efi/semanaanterior/')

    def test_client_cant_access_eff_current_week(self):
        response = self.get_response('eff_current_week')
        self.assertRedirects(response,
                             'accounts/login/?next=/efi/semanaactual/')

    def test_client_cant_access_eff_current_month(self):
        response = self.get_response('eff_current_month')
        self.assertRedirects(response,
                             'accounts/login/?next=/efi/mesactual/')

    def test_client_cant_access_eff_report(self):
        response = self.get_response('eff_report', args=['client'])
        self.assertRedirects(response,
                             'accounts/login/?next=/efi/reporte/client/')

    def test_client_cant_access_eff_last_month(self):
        response = self.get_response('eff_last_month')
        self.assertRedirects(response,
                             'accounts/login/?next=/efi/mespasado/')

    def test_client_cant_access_eff_extra_hours(self):
        response = self.get_response('eff_extra_hours')
        self.assertRedirects(response,
                             'accounts/login/?next=/efi/horasextras/')

    def test_client_cant_access_eff_next(self):
        response = self.get_response('eff_next')
        self.assertRedirects(response,
                             'accounts/login/?next=/efi/next/')

    def test_client_cant_access_eff_prev(self):
        response = self.get_response('eff_prev')
        self.assertRedirects(response,
                             'accounts/login/?next=/efi/prev/')

    def test_client_cant_access_eff_chart(self):
        response = self.get_response('eff_chart', args=['client'])
        self.assertRedirects(response,
                             'accounts/login/?next=/efi/chart/client/')

    def test_client_cant_access_eff_charts(self):
        response = self.get_response('eff_charts')
        self.assertRedirects(response,
                             'accounts/login/?next=/efi/charts/')

    def test_client_cant_access_eff_update_db(self):
        response = self.get_response('eff_update_db')
        self.assertRedirects(response,
                             'accounts/login/?next=/efi/update-db/')

    def test_client_cant_access_eff_administration(self):
        response = self.get_response('eff_administration')
        self.assertRedirects(response,
                    'accounts/login/?next=/efi/administration/users_password/')

    def test_client_cant_access_eff_admin_change_profile(self):
        response = self.get_response('eff_admin_change_profile')
        self.assertRedirects(response,
                    'accounts/login/?next=/efi/administration/users_profile/')

    def test_client_cant_access_eff_admin_add_user(self):
        response = self.get_response('eff_admin_add_user')
        self.assertRedirects(response,
                            'accounts/login/?next=/efi/administration/add_user/')

    def test_client_cant_access_eff_client_reports_admin(self):
        response = self.get_response('eff_client_reports_admin')
        self.assertRedirects(response, ('accounts/login/?next=/efi/'
                                        'administration/client_reports/'))

    def test_client_cant_access_eff_fixed_price_client_reports(self):
        response = self.get_response('eff_fixed_price_client_reports')
        self.assertRedirects(response, ('/accounts/login/?next=/efi/'
                                        'administration/'
                                        'fixed_price_client_reports/'))

    def test_client_cant_access_eff_dump_csv_upload(self):
        response = self.get_response('eff_dump_csv_upload')
        self.assertRedirects(response, ('accounts/login/?next=/efi/'
                                        'administration/'
                                        'dump-csv-upload/'))

    def test_client_cant_access_eff_client_report(self):
        ClientFactory(name='FakeClient')
        response = self.get_response('eff_client_report', args=['FakeClient'])
        self.assertRedirects(response, ('accounts/login/?next=/efi/'
                                        'reporte_cliente/FakeClient/'))

    def test_client_cant_access_eff_admin_users_association(self):
        response = self.get_response('eff_admin_users_association')
        self.assertRedirects(response,
                'accounts/login/?next=/efi/administration/users_association/')


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(ClientProfileTest))
    suite.addTest(makeSuite(UserProfileTest))
    suite.addTest(makeSuite(ClientPermissionsTest))
    return suite
