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
from django.core import mail
from datetime import date
import re

from factories import UserFactory


class HelperTest(TestCase):

    def setUp(self):

        self.test_client = TestClient()

        # Create a UserProfile.
        self.user = UserFactory(username='test', email='test@test.com')


class PasswordResetTest(HelperTest):

    def check_users(self, url):
        check = self.test_client.login(username=self.user.username,
                                       password=self.user.password)
        self.assertEqual(check, True)

        response = self.test_client.get(url)
        query = PyQuery(response.content)
        # Get users as they appear in the dropdown
        users = query("select#id_user option")
        if users:
            users = users.text().split()
            self.assertEqual(users, self.ordered_users)
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        # Get users as they appear in the dropdown
        users = query("select#id_user option")

    def test_password_reset1(self):
        response = self.test_client.get(reverse('login'))
        query = PyQuery(response.content)
        query = query("form a")
        href = query.attr('href')
        self.assertEqual(href, '/accounts/password_reset/')

    def test_password_reset3(self):
        self.test_client.post(reverse('password_reset'),
                              {'email': 'test@test.com'})
        # check user can still login
        check = self.test_client.login(username='test',
                                       password='test')
        self.assertEqual(check, True)

    def test_password_reset_email_subject(self):
        self.test_client.post(reverse('password_reset'),
                              {'email': 'test@test.com'})
        self.assertEqual(mail.outbox[0].subject,
                         'Password reset on example.com')

    def test_password_reset_email_from(self):
        self.test_client.post(reverse('password_reset'),
                              {'email': 'test@test.com'})
        self.assertEqual(mail.outbox[0].from_email, 'webmaster@localhost')

    def test_password_reset_email_to(self):
        self.test_client.post(reverse('password_reset'),
                              {'email': 'test@test.com'})
        self.assertEqual(mail.outbox[0].to, [u'test@test.com'])

    def test_password_reset_email_body(self):
        self.test_client.post(reverse('password_reset'),
                              {'email': 'test@test.com'})
        body = "\n\n\n\nYou\'re receiving this e-mail because you requested " +\
               "a password reset for your user account at example.com.\n\n\n" +\
               "Please go to the following page and choose a new password:" +\
               "\n\nhttp://example.com/accounts/reset/"
        aux = re.search('(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)',
                        mail.outbox[0].body[len(body) - 1:])
        body += aux.group(0) + "\n\nYour username, in case you\'ve forgotten" +\
                ": test\n\nThanks for using our site!\n\nThe example.com tea" +\
                "m\n\n\n"

        self.assertEqual(mail.outbox[0].body, body)

    def test_password_reset_redirect(self):
        response = self.test_client.post(reverse('password_reset'),
                                         {'email': 'test@test.com'},
                                         follow=True)
        self.assertEqual(response.redirect_chain[0],
                         ('http://testserver/accounts/password_reset/done/',
                          302))

    def test_password_reset_bad_email(self):
        response = self.test_client.post(reverse('password_reset'),
                                         {'email': 'badMail@test.com'})
        query?
        self.assertEqual(response, ALGO)

    def test_password_reset_done(self):
        response = self.test_client.get(reverse('password_reset_done'))
        self.assertEqual(response.status_code, 200)


class PasswordChangeTest(HelperTest):

    def test_get_client_summary_per_project_limit1(self):
        pass


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(PasswordResetTest))
    suite.addTest(makeSuite(PasswordChangeTest))
    return suite
