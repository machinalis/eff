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
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.auth.models import User
from django.db.models import get_app, get_models
from unittest import TestSuite, makeSuite
from eff.models import Project, Client as EffClient, ExternalSource
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


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(QueriesTest))
    return suite
