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
from datetime import date, timedelta
from django.db.models import signals
from eff._models.user_profile import create_profile_for_user
from django.contrib.auth.models import User
from urllib import urlencode


from factories import UserProfileFactory, ProjectFactory, ClientFactory
from factories import ProjectAssocFactory, ExternalSourceFactory, DumpFactory
from factories import TimeLogFactory, AvgHoursFactory, AdminFactory


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
        # A dump
        dump = DumpFactory(date=date(2012, 05, 30), source=self.ext_src)
        # A client
        client = ClientFactory(name='client', external_source=self.ext_src)
        # 2 projects
        project1 = ProjectFactory(name='Fake Project 1', client=client,
                                  external_id='FP1', start_date=date.today())
        project2 = ProjectFactory(name='Fake Project 2', client=client,
                                  external_id='FP2', start_date=date.today())
        # A 'watcher' UserProfile, the one who watches others and a projassoc.
        self.watcher = UserProfileFactory(user__username='watcher')
        start_date = date(2012, 01, 01)
        end_date = date(2012, 01, 31)
        AvgHoursFactory(user=self.watcher.user, date=start_date,
                        hours=Decimal('8.00'))
        ProjectAssocFactory(project=project1, member=self.watcher,
                            client_rate=Decimal('0.50'),
                            user_rate=Decimal('0.20'),
                            from_date=start_date,
                            to_date=end_date)
        for d in xrange(5):
            TimeLogFactory(user=self.watcher.user, hours_booked=Decimal('2.00'),
                           date=start_date + timedelta(days=d),
                           project=project1, dump=dump)

        # 5 'watched' UserProfiles, those watched by watcher
        # For each user add projassocs, avghours and some logs.
        start_date = date(2012, 01, 01)
        end_date = date(2012, 01, 31)
        for i in xrange(5):
            user = UserProfileFactory(user__username='test' + str(i))
            self.watcher.watches.add(user.user)
            ProjectAssocFactory(project=project2, member=user,
                                client_rate=Decimal('0.25'),
                                user_rate=Decimal('0.10'), from_date=start_date,
                                to_date=end_date)
            AvgHoursFactory(user=user.user, date=start_date,
                            hours=Decimal('8.00'))
            # Generate some timelogs with specified hours for each user.
            for d in xrange(5):
                TimeLogFactory(user=user.user, hours_booked=Decimal('4.00'),
                               date=start_date + timedelta(days=d),
                               project=project2, dump=dump)

        # An user not followed.
        self.no_perms_user = UserProfileFactory(user__username='notFollowed')
        # Generate associated data for no_perms_user user.
        ProjectAssocFactory(project=project2, member=self.no_perms_user,
                            client_rate=Decimal('0.25'),
                            user_rate=Decimal('0.10'), from_date=start_date,
                            to_date=end_date)
        AvgHoursFactory(user=self.no_perms_user.user, date=start_date,
                        hours=Decimal('8.00'))
        for d in xrange(5):
            TimeLogFactory(user=self.no_perms_user.user,
                           hours_booked=Decimal('4.00'),
                           date=start_date + timedelta(days=d),
                           project=project2, dump=dump)

    def get_response(self, view='eff', args=None, from_date='2012-01-01',
                     to_date='2012-01-31', export=None, detailed=False):

        get_data = urlencode([('from_date', from_date),
                              ('to_date', to_date)])

        if not args:
            url = '%s?%s' % (reverse(view), get_data)
        else:
            url = '%s?%s' % (reverse(view, args=args), get_data)
            if export:
                url += '&export=%s' % export
            if detailed:
                url += '&detailed'

        return self.test_client.get(url)

    def tearDown(self):
        # reconnect signals
        signals.post_save.connect(
            create_profile_for_user, sender=User,
            dispatch_uid='eff._models.user_profile.create_profile_for_user')


class UserFollowingOthersTest(HelperTest):
    def setUp(self):
        super(UserFollowingOthersTest, self).setUp()

        self.test_client.login(username='watcher', password='watcher')

    def test_eff_view_works(self):
        response = self.get_response()
        self.assertEqual(response.status_code, 200)

    def test_followed_users_shows_correctly(self):
        response = self.get_response()
        query = PyQuery(response.content)
        query = query('table#queryTable td.name').text()
        names = map(lambda u: u.username, self.watcher.watches.all())
        names.append('watcher')
        self.assertEqual(set(query.split()), set(names))

    def test_follower_can_access_report_for_users_being_followed(self):
        user = self.watcher.watches.all()[0]
        response = self.get_response(view='eff_report', args=[user.username])
        self.assertEqual(response.status_code, 200)

    def test_follower_has_detailed_report_options_for_himself(self):
        response = self.get_response(view='eff_report',
                                     args=[self.watcher.user.username])
        query = PyQuery(response.content)
        query = query('div#detailed-report a')
        self.assertIn('ODT', query.text())
        self.assertIn('CSV', query.text())

    def test_follower_has_detailed_report_options_for_followed_users(self):
        user = self.watcher.watches.all()[0]
        response = self.get_response(view='eff_report', args=[user.username])
        query = PyQuery(response.content)
        query = query('div#detailed-report a')
        self.assertIn('ODT', query.text())
        self.assertIn('CSV', query.text())

    def test_follower_can_see_detailed_report_for_users_being_followed(self):
        user = self.watcher.watches.all()[0]
        response = self.get_response(view='eff_report', args=[user.username],
                                     export='odt', detailed=True)
        self.assertEqual(response.status_code, 200)
        response = self.get_response(view='eff_report', args=[user.username],
                                     export='csv', detailed=True)
        self.assertEqual(response.status_code, 200)

    def test_follower_cant_see_report_for_user_not_being_followed(self):
        response = self.get_response(view='eff_report',
                                     args=[self.no_perms_user.user.username])
        self.assertEqual(response.status_code, 302)
        response = self.get_response(view='eff_report',
                                     args=[self.no_perms_user.user.username])
        self.assertEqual(response.status_code, 302)

    def test_follower_cant_report_for_user_not_being_followed(self):
        response = self.get_response(view='eff_report',
                                     args=[self.no_perms_user.user.username],
                                     export='odt', detailed=True)
        self.assertEqual(response.status_code, 302)
        response = self.get_response(view='eff_report',
                                     args=[self.no_perms_user.user.username],
                                     export='csv', detailed=True)
        self.assertEqual(response.status_code, 302)

    def test_follower_cant_report_with_money_for_users_being_followed(self):
        user = self.watcher.watches.all()[0]
        response = self.get_response(view='eff_report', args=[user.username],
                                     export='odt')
        self.assertEqual(response.status_code, 302)
        response = self.get_response(view='eff_report', args=[user.username],
                                     export='csv')
        self.assertEqual(response.status_code, 302)


class UserWithPermissionsTest(HelperTest):
    def setUp(self):
        super(UserWithPermissionsTest, self).setUp()

        # Create an admin.
        self.admin = AdminFactory(username='admin')
        UserProfileFactory(user=self.admin)

        self.test_client.login(username='admin', password='admin')

    def test_user_with_permisions_follows_everyone(self):
        response = self.get_response()
        query = PyQuery(response.content)
        query = query('table#queryTable td.name').text()
        names = map(lambda u: u.username, (list(self.watcher.watches.all()) +
                                           [self.no_perms_user.user]))
        names.append('watcher')
        self.assertEqual(set(query.split()), set(names))

    def test_user_with_permisions_can_see_detailed_report_for_everyone(self):
        user = self.no_perms_user.user
        response = self.get_response(view='eff_report', args=[user.username],
                                     export='odt', detailed=True)
        self.assertEqual(response.status_code, 200)
        response = self.get_response(view='eff_report', args=[user.username],
                                     export='csv', detailed=True)
        self.assertEqual(response.status_code, 200)

    def test_user_with_permisions_can_see_report_with_money_for_everyone(self):
        user = self.no_perms_user.user
        response = self.get_response(view='eff_report', args=[user.username],
                                     export='odt')
        self.assertEqual(response.status_code, 200)
        response = self.get_response(view='eff_report', args=[user.username],
                                     export='csv')
        self.assertEqual(response.status_code, 200)

    def test_user_with_permisions_has_detailed_report_options(self):
        user = self.no_perms_user.user
        response = self.get_response(view='eff_report', args=[user.username])
        query = PyQuery(response.content)
        query = query('div#detailed-report a')
        self.assertIn('ODT', query.text())
        self.assertIn('CSV', query.text())

    def test_user_with_permisions_has_money_report_options(self):
        user = self.no_perms_user.user
        response = self.get_response(view='eff_report', args=[user.username])
        query = PyQuery(response.content)
        query = query('table#project-report-table a')
        self.assertIn('ODT', query.text())
        self.assertIn('CSV', query.text())


class UserWithoutPermissionsTest(HelperTest):
    def setUp(self):
        super(UserWithoutPermissionsTest, self).setUp()

        self.test_client.login(username='notFollowed', password='notFollowed')

    def test_can_only_see_himself(self):
        response = self.get_response()
        query = PyQuery(response.content)
        query = query('table#queryTable td.name').text()
        name = '%s %s' % (self.no_perms_user.user.first_name,
                          self.no_perms_user.user.last_name)
        self.assertEqual(query, name)

    def test_can_see_his_report(self):
        response = self.get_response(view='eff_report',
                                     args=[self.no_perms_user.user.username])
        self.assertEqual(response.status_code, 200)

    def test_cant_see_report_for_others(self):
        user = self.watcher.watches.all()[0]
        response = self.get_response(view='eff_report', args=[user.username])
        self.assertEqual(response.status_code, 302)

    def test_has_detailed_report_options(self):
        response = self.get_response(view='eff_report',
                                     args=[self.no_perms_user.user.username])
        query = PyQuery(response.content)
        query = query('div#detailed-report a')
        self.assertIn('ODT', query.text())
        self.assertIn('CSV', query.text())

    def test_cant_report_for_others(self):
        user = self.watcher.watches.all()[0]
        response = self.get_response(view='eff_report',
                                     args=[user.username],
                                     export='odt', detailed=True)
        self.assertEqual(response.status_code, 302)
        response = self.get_response(view='eff_report',
                                     args=[user.username],
                                     export='csv', detailed=True)
        self.assertEqual(response.status_code, 302)

    def test_cant_report_with_money_for_himself(self):
        response = self.get_response(view='eff_report',
                                     args=[self.no_perms_user.user.username],
                                     export='odt')
        self.assertEqual(response.status_code, 302)
        response = self.get_response(view='eff_report',
                                     args=[self.no_perms_user.user.username],
                                     export='csv')
        self.assertEqual(response.status_code, 302)

    def test_cant_report_with_money_for_others(self):
        user = self.watcher.watches.all()[0]
        response = self.get_response(view='eff_report', args=[user.username],
                                     export='odt')
        self.assertEqual(response.status_code, 302)
        response = self.get_response(view='eff_report', args=[user.username],
                                     export='csv')
        self.assertEqual(response.status_code, 302)


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(UserFollowingOthersTest))
    suite.addTest(makeSuite(UserWithPermissionsTest))
    suite.addTest(makeSuite(UserWithoutPermissionsTest))
    return suite
