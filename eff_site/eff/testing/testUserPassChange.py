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
import re

from factories import UserFactory


class HelperTest(TestCase):

    def setUp(self):

        self.test_client = TestClient()

        # Create a User.
        self.user = UserFactory(username='test', email='test@test.com')


class PasswordResetTest(HelperTest):

    def generate_password_reset_url(self):
        self.test_client.post(reverse('password_reset'),
                              {'email': 'test@test.com'})
        email_sent = mail.outbox[0]
        aux = re.search('(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)',
                        email_sent.body[100:])
        aux = aux.group(0)

        return '/accounts/reset/' + aux

    def test_password_reset1(self):
        response = self.test_client.get(reverse('login'))
        query = PyQuery(response.content)
        query = query("form a")
        href = query.attr('href')
        self.assertEqual(href, '/accounts/password_reset/')

    def test_password_reset2(self):
        self.test_client.post(reverse('password_reset'),
                              {'email': 'test@test.com'})
        # check user can still login
        check = self.test_client.login(username='test',
                                       password='test')
        self.assertEqual(check, True)

    def test_password_reset_email_subject(self):
        self.test_client.post(reverse('password_reset'),
                              {'email': 'test@test.com'})
        email_sent = mail.outbox[0]
        self.assertEqual(email_sent.subject,
                         'Password reset on example.com')

    def test_password_reset_email_from(self):
        self.test_client.post(reverse('password_reset'),
                              {'email': 'test@test.com'})
        email_sent = mail.outbox[0]
        self.assertEqual(email_sent.from_email, 'webmaster@localhost')

    def test_password_reset_email_to(self):
        self.test_client.post(reverse('password_reset'),
                              {'email': 'test@test.com'})
        email_sent = mail.outbox[0]
        self.assertEqual(email_sent.to, [u'test@test.com'])

    def test_password_reset_email_body(self):
        self.test_client.post(reverse('password_reset'),
                              {'email': 'test@test.com'})
        email_sent = mail.outbox[0]
        body = "\n\n\n\nYou\'re receiving this e-mail because you requested " +\
               "a password reset for your user account at example.com.\n\n\n" +\
               "Please go to the following page and choose a new password:" +\
               "\n\nhttp://example.com/accounts/reset/"
        aux = re.search('(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)',
                        email_sent.body[len(body) - 1:])
        body += aux.group(0) + "\n\nYour username, in case you\'ve forgotten" +\
                ": test\n\nThanks for using our site!\n\nThe example.com tea" +\
                "m\n\n\n"

        self.assertEqual(email_sent.body, body)

    def test_password_reset_redirect(self):
        response = self.test_client.post(reverse('password_reset'),
                                         {'email': 'test@test.com'},
                                         follow=True)
        self.assertEqual(response.redirect_chain[0],
                         ('http://testserver/accounts/password_reset/done/',
                          302))

    def test_password_reset_bad_email_error(self):
        response = self.test_client.post(reverse('password_reset'),
                                         {'email': 'badMail@test.com'})
        query = PyQuery(response.content)
        query = query('ul.errorlist')
        error = query.text()
        error_msg = "That e-mail address doesn't have an associated user " +\
                    "account. Are you sure you've registered?"
        self.assertEqual(error, error_msg)

    def test_password_reset_not_an_email_error(self):
        response = self.test_client.post(reverse('password_reset'),
                                         {'email': 'notAnEmail'})
        query = PyQuery(response.content)
        query = query('ul.errorlist')
        error = query.text()
        error_msg = "Enter a valid e-mail address."
        self.assertEqual(error, error_msg)

    def test_password_reset_done(self):
        response = self.test_client.get(reverse('password_reset_done'))
        self.assertEqual(response.status_code, 200)

    def test_password_reset_confirm_link_works(self):
        url = self.generate_password_reset_url()
        response = self.test_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_password_reset_confirm_link_already_used(self):
        url = self.generate_password_reset_url()
        response = self.test_client.post(url, {'new_password1': 'newpass',
                                               'new_password2': 'newpass'})
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        query = query('div p')
        msg = "Password reset unsuccessful The password reset link was " +\
              "invalid, possibly because it has already been used.  Please " +\
              "request a new password reset."
        self.assertEqual(query.text(), msg)

    def test_password_reset_confirm_different_passwords(self):
        url = self.generate_password_reset_url()
        response = self.test_client.post(url, {'new_password1': 'newpass',
                                               'new_password2': 'pass'})
        query = PyQuery(response.content)
        query = query('ul.errorlist')
        error = query.text()
        error_msg = "The two password fields didn't match."
        self.assertEqual(error, error_msg)

    def test_password_reset_complete(self):
        url = self.generate_password_reset_url()
        response = self.test_client.post(url, {'new_password1': 'newpass',
                                               'new_password2': 'newpass'},
                                         follow=True)
        query = PyQuery(response.content)
        query = query('div p:last').prevAll()
        msg = "Password reset complete Your password has been set.  You may " +\
              "go ahead and log in now."
        self.assertEqual(query.text(), msg)

    def test_password_reset_worked(self):
        url = self.generate_password_reset_url()
        self.test_client.post(url, {'new_password1': 'newpass',
                                    'new_password2': 'newpass'})
        check = self.test_client.login(username='test', password='newpass')
        self.assertEqual(check, True)


class PasswordChangeTest(HelperTest):

    def setUp(self):
        super(PasswordChangeTest, self).setUp()
        self.test_client.login(username='test', password='test')

    def test_password_change(self):
        response = self.test_client.get(reverse('password_change'))
        self.assertEqual(response.status_code, 200)

    def test_password_change_redirect(self):
        response = self.test_client.post(reverse('password_change'),
                                         {'old_password': 'test',
                                          'new_password1': 'newpass',
                                          'new_password2': 'newpass'},
                                         follow=True)
        self.assertEqual(response.redirect_chain[0],
                         ('http://testserver/accounts/change_password/done/',
                          302))

    def test_password_change_bad_old_password(self):
        response = self.test_client.post(reverse('password_change'),
                                         {'old_password': 'notmypass',
                                          'new_password1': 'newpass',
                                          'new_password2': 'newpass'})
        query = PyQuery(response.content)
        query = query('ul.errorlist')
        error = query.text()
        error_msg = "Your old password was entered incorrectly. " +\
                    "Please enter it again."
        self.assertEqual(error, error_msg)

    def test_password_change_bad_new_password(self):
        response = self.test_client.post(reverse('password_change'),
                                         {'old_password': 'test',
                                          'new_password1': 'newpass1',
                                          'new_password2': 'newpass2'})
        query = PyQuery(response.content)
        query = query('ul.errorlist')
        error = query.text()
        error_msg = "The two password fields didn't match."
        self.assertEqual(error, error_msg)

    def test_password_change_complete(self):
        response = self.test_client.post(reverse('password_change'),
                                         {'old_password': 'test',
                                          'new_password1': 'newpass2',
                                          'new_password2': 'newpass2'},
                                                      follow=True)
        query = PyQuery(response.content)
        query = query('div p')
        msg = "Password change successful Your password was changed."
        self.assertEqual(query.text(), msg)

    def test_password_change_worked(self):
        self.test_client.post(reverse('password_change'),
                              {'old_password': 'test',
                               'new_password1': 'newpass',
                               'new_password2': 'newpass'})
        self.test_client.logout()
        check = self.test_client.login(username='test', password='newpass')
        self.assertEqual(check, True)


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(PasswordChangeTest))
    suite.addTest(makeSuite(PasswordResetTest))
    return suite
