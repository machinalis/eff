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
from django.test.client import Client
from pyquery import PyQuery
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from unittest import TestSuite, makeSuite
from eff.models import Project, Client as EffClient, ExternalSource, UserProfile
from django.template.defaultfilters import slugify


class QueriesTest(TestCase):

    def setUp(self):
        self.test_client = Client()
        user = User.objects.create_superuser(username='admin',
                                     email='admin@test.com',
                                     password='admin')
        self.users = [user]
        self.clients = []
        self.projects = []

        # Expected order for users and projects
        self.ordered_users = ['---------', 'admin', 'test1', 'testa', 'testA',
            'testasd', 'testb', 'testB', 'testone', 'testtwo']
        self.ordered_projects = ['---------', 'Fake Client 1 - fake Project 1',
                                 'Fake Client 1 - Fake Project 1',
                                 'Fake Client 1 - Fake project 2',
                                 'Fake Client 1 - Fake Project 2',
                                 'Fake Client 3 - Fake Project 6',
                                 'Machinalis - demo',
                                 'Machinalis - Eff',
                                 'Yet Another Client - Fake Project 1',
                                 'Yet Another Client - Fake Project 10',
                                 'Yet Another Client - Fake Project II']

        # Add a superuser and some test users.
        for char in ['A', 'a', 'asd', 'one', 'two', '1', 'b', 'B']:
                user = User.objects.create_user(
                username='test' + char, email='test' + char + '@test.com',
                        password='test' + char)
                user.save()
                self.users.append(user)

        # Add some clients and projects.
        source, is_done = ExternalSource.objects.get_or_create(name='Example')
        for project_rep in self.ordered_projects[1:]:
            client_name, project_name = project_rep.split(' - ')
            client, is_done = EffClient.objects.get_or_create(name=client_name,
                                                     slug=slugify(client_name),
                                                     external_source=source)
            client.save()
            self.clients.append(client)
            project = Project.objects.create(name=project_name, client=client)
            project.save()
            self.projects.append(project)

        check = self.test_client.login(username='admin', password='admin')
        self.assertEqual(check, True)

    def check_ordered_users(self, url):
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        # Get users as they appear in the dropdown
        users = query("select#id_user option")
        if users:
            users = users.text().split()
            self.assertEqual(users, self.ordered_users)

    def check_ordered_projects(self, url):
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        # Get projects as they appear in the dropdown
        projects = query("select#id_project option")
        if projects:
            _projects = []
            for i in range(0, len(projects)):
                _projects.append(projects.eq(i).text())
            self.assertEqual(_projects, self.ordered_projects)

    def test_ordered_dropdowns_in_eff_avghours(self):
        url = reverse('admin:eff_avghours_add')
        self.check_ordered_users(url)

    def test_ordered_dropdowns_in_eff_timelog(self):
        url = reverse('admin:eff_timelog_add')
        self.check_ordered_users(url)
        self.check_ordered_projects(url)

    def test_ordered_dropdowns_in_eff_userprofile(self):
        url = reverse('admin:eff_userprofile_add')
        self.check_ordered_users(url)

    def test_ordered_dropdowns_in_eff_wage(self):
        url = reverse('admin:eff_wage_add')
        self.check_ordered_users(url)

    def test_ordered_dropdowns_in_eff_projectassoc(self):
        url = reverse('admin:eff_projectassoc_add')
        self.check_ordered_projects(url)

    def test_ordered_multiselect_in_eff_userprofile(self):
        url = reverse('admin:eff_userprofile_add')
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        # Get users as they appear in the multi select
        users = query("select#id_watches option")
        # Drop '--------', since it will not show that choice
        ordered_users = self.ordered_users[1:]
        if users:
            users = users.text().split()
            self.assertEqual(users, ordered_users)

    def test_users_to_follow_in_eff_userprofile_cant_follow_itself(self):
        test_user = UserProfile.objects.get(user__username='test1')
        url = reverse('admin:eff_userprofile_change', args=(test_user.id,))
        response = self.test_client.get(url)
        post_data = {'user': test_user.user.id, 'watches': [test_user.user.id],
                     'user_type': 'Default',
                     'clienthandles_set-TOTAL_FORMS': '3',
                     'clienthandles_set-INITIAL_FORMS': '0',
                     'clienthandles_set-MAX_NUM_FORMS': ''}
        response = self.test_client.post(url, post_data)
        error = "You are adding this user to watch himself, please don't"
        query = PyQuery(response.content)
        # Get the error
        error_msg = query("ul.errorlist").text()
        self.assertEqual(error_msg, error)

    def test_users_to_follow_in_eff_userprofile_cant_follow_admin_user(self):
        admin_user = UserProfile.objects.get(user__username='admin')
        test_user = UserProfile.objects.get(user__username='test1')
        url = reverse('admin:eff_userprofile_change', args=(test_user.id,))
        response = self.test_client.get(url)
        post_data = {'user': test_user.user.id, 'watches': [admin_user.user.id],
                     'user_type': UserProfile.KIND_OTHER,
                     'clienthandles_set-TOTAL_FORMS': '3',
                     'clienthandles_set-INITIAL_FORMS': '0',
                     'clienthandles_set-MAX_NUM_FORMS': ''}
        response = self.test_client.post(url, post_data)
        error = "Don't add admin here"
        query = PyQuery(response.content)
        # Get the error
        error_msg = query("ul.errorlist").text()
        self.assertEqual(error_msg, error)

    def test_billing_emails_shown_in_eff_client(self):
        client = EffClient.objects.get(name='Fake Client 1')
        url = reverse('admin:eff_client_change', args=(client.id,))
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        query = query('div#billingemail_set-group fieldset h2').text()
        self.assertEqual(query, 'Billing email addresses')

    def test_invalid_email_in_eff_billing_emails(self):
        client = EffClient.objects.get(name='Fake Client 1')
        url = reverse('admin:eff_billingemail_add')
        response = self.test_client.get(url)
        post_data = {'email_address': 'not_an_email@lala', 'send_as': 'to',
                   'client': client.id}
        response = self.test_client.post(url, post_data)
        error = "Enter a valid e-mail address."
        query = PyQuery(response.content)
        # Get the error
        error_msg = query("ul.errorlist").text()
        self.assertEqual(error_msg, error)

    def test_client_required_in_eff_billing_emails(self):
        url = reverse('admin:eff_billingemail_add')
        response = self.test_client.get(url)
        post_data = {'email_address': 'email@test.com', 'send_as': 'to'}
        response = self.test_client.post(url, post_data)
        error = "This field is required."
        query = PyQuery(response.content)
        # Get the error
        error_msg = query("ul.errorlist").text()
        self.assertEqual(error_msg, error)

    def test_send_as_correctly_shown_in_eff_billing_emails(self):
        url = reverse('admin:eff_billingemail_add')
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        query = query("select#id_send_as")
        self.assertEqual(query.text(), 'TO CC BCC')

    def test_password_set_in_user_add(self):
        url = reverse('admin:auth_user_add')
        response = self.test_client.get(url)
        post_data = {'username': 'newUser', 'password1': 'pass',
                     'password2': 'pass',
                     #'is_active': {'checked': 'check'},
                     'last_login_0': '2012-06-15',
                     'login_1': '16:29:51',
                     'date_joined_0': '2012-06-15',
                     'date_joined_1': '16:29:51',
                     'wage_set-TOTAL_FORMS': '3',
                     'wage_set-INITIAL_FORMS': '0',
                     'wage_set-MAX_NUM_FORMS': '',
                     'avghours_set-TOTAL_FORMS': '3',
                     'avghours_set-INITIAL_FORMS': '0',
                     'avghours_set-MAX_NUM_FORMS': ''}

        response = self.test_client.post(url, post_data)
        user = User.objects.get(username='newUser')
        # print user.is_active
        print response
        self.assertEqual(response.status_code, 200)
        check = self.test_client.login(username='newUser', password='pass')
        self.assertEqual(check, True)

    # def test_password_error_in_user_add(self):
    #     url = reverse('admin:auth_user_add')
    #     post_data = {'username': 'newUser', 'password1': 'pass',
    #                  'password2': 'pass'}
    #     response = self.test_client.post(url, post_data)
    #     self.assertEqual(response.status_code, 200)
    #     response = response.client.login(name='newUser', password='pass')
    #     self.assertEqual(response.status_code, 200)


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(QueriesTest))
    return suite
