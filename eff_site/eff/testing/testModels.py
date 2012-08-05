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
from django.contrib.auth.models import User, Permission, Group
from django.core.exceptions import ValidationError
from django.core import mail

from eff.models import UserProfile, AvgHours, Project, TimeLog, ExternalSource
from eff.models import Wage, ClientHandles, Handle
from eff.models import Client as EffClient, Dump
from eff.views import Data
from factories import (ClientFactory, BillingFactory, CreditNoteFactory,
                       PaymentFactory, ExternalSourceFactory)

from eff_site.eff.forms import UserAdminForm

from unittest import TestSuite, makeSuite
from datetime import date, timedelta, datetime


class HelperTest(TestCase):

    def setUp(self):
        self.usr = User.objects.create_user(username='test1',
                                            email='test1@test.com',
                                            password='test1')
        self.usr.save()

        self.avg_hours_list = [AvgHours(date=date(2008, 03, 04), hours='5',
                                        user=self.usr),
                               AvgHours(date=date(2008, 03, 13), hours='0',
                                        user=self.usr),
                               AvgHours(date=date(2008, 03, 20), hours='4',
                                        user=self.usr),
                               AvgHours(date=date(2008, 03, 31), hours='5',
                                        user=self.usr),
                               AvgHours(date=date(2008, 04, 07), hours='4',
                                        user=self.usr),
                               AvgHours(date=date(2008, 04, 11), hours='5',
                                        user=self.usr),
                               AvgHours(date=date(2008, 04, 29), hours='6',
                                        user=self.usr), ]
        # save all data
        for x in self.avg_hours_list:
            x.save()

    def tearDown(self):
        for ah in AvgHours.objects.all():
            ah.delete()
        self.usr.delete()


class QueriesTest(HelperTest):

    def test_has_attributes(self):
        for attr in ('address', 'phone_number', 'personal_email',
                     'city', 'state', 'country'):
            self.assert_(hasattr(self.usr.get_profile(), attr))

    def test_avg_hours_for_0(self):
        self.assert_(hasattr(UserProfile, 'get_avg_hours_for'))
        valor = self.usr.get_profile().get_avg_hours_for(date(2008, 4, 21))
        self.assertEqual(valor, 5)

    def test_avg_hours_for_1(self):
        self.assert_(hasattr(UserProfile, 'get_avg_hours_for'))
        valor = self.usr.get_profile().get_avg_hours_for(date(2008, 2, 21))
        self.assertEqual(valor, 0)

    def test_num_loggable_hours_0(self):
        self.assert_(hasattr(UserProfile, 'num_loggable_hours'))
        valor = self.usr.get_profile().num_loggable_hours(date(2008, 4, 7),
                                                          date(2008, 4, 25))
        self.assertEqual(valor, 71)

    def test_num_loggable_hours_1(self):
        self.assert_(hasattr(UserProfile, 'num_loggable_hours'))
        valor = self.usr.get_profile().num_loggable_hours(date(2008, 3, 13),
                                                          date(2008, 3, 19))
        self.assertEqual(valor, 0)

    def test_num_loggable_hours_2(self):
        self.assert_(hasattr(UserProfile, 'num_loggable_hours'))
        valor = self.usr.get_profile().num_loggable_hours(date(2008, 3, 4),
                                                          date(2008, 4, 1))
        self.assertEqual(valor, 73)

    def test_num_loggable_hours_3(self):
        self.assert_(hasattr(UserProfile, 'num_loggable_hours'))
        valor = self.usr.get_profile().num_loggable_hours(date(2008, 1, 4),
                                                          date(2008, 4, 1))
        self.assertEqual(valor, 73)

    def test_has_get_absolute_url(self):
        self.assert_(hasattr(UserProfile, 'get_absolute_url'))

    def test_get_absolute_url(self):
        self.assertEqual(self.usr.get_profile().get_absolute_url(),
                         '/profiles/test1/')

    def test_add_avg_hours(self):
        self.assert_(hasattr(UserProfile, 'add_avg_hours'))
        ndate = date(2008, 05, 05)
        self.usr.get_profile().add_avg_hours(ndate, 8)
        self.assertEqual(self.usr.avghours_set.filter(date=ndate)[0].date,
                         ndate)

    def test_add_avg_hours_second_insert_error(self):
        ndate = date(2008, 05, 05)
        self.usr.get_profile().add_avg_hours(ndate, 8)
        self.assertRaises(ValidationError, self.usr.get_profile().add_avg_hours,
                        ndate, 6)

    def test_add_avg_hours_negative_integer_error(self):
        self.assertRaises(ValueError, self.usr.get_profile().add_avg_hours,
                          date(2008, 05, 05), -1)

    def test_update_avg_hour(self):
        self.assert_(hasattr(UserProfile, 'update_avg_hour'))
        udate = date(2008, 03, 04)
        self.usr.get_profile().update_avg_hour(udate, 1)
        self.assertEqual(self.usr.avghours_set.get(date=udate).hours, 1)

    def test_update_avg_hour_negative_value(self):
        self.assertRaises(ValueError, self.usr.get_profile().update_avg_hour,
                          date(2008, 03, 04), -5)

    def test_update_avg_hour_inexistent_avg_hour(self):
        self.assertRaises(ValueError, self.usr.get_profile().update_avg_hour,
                          date(2007, 01, 01), 6)


class PageTest(HelperTest):

    def setUp(self):
        super(PageTest, self).setUp()
        self.usr.user_permissions.add(Permission.objects.get(
            codename=u'view_billable'))
        self.usr.user_permissions.add(Permission.objects.get(
            codename=u'view_wage'))
        self.client = Client()

    def test_loggin(self):
        context = {
            'username': 'test1',
            'password': 'test1',
            'next': '/efi/semanaactual/'}
        response = self.client.post('/accounts/login/', context)
        self.assertEqual(response.status_code, 302)
        usr = User.objects.get(username='test1')
        self.assert_(usr.is_authenticated())

    def test_edit_profile(self):
        self.assert_(self.client.login(username='test1', password='test1'))
        context = {'address': 'Montevido 728', 'phone_number': '5557271', }
        response = self.client.post('/profiles/edit/', context)
        self.assertEqual(response.status_code, 302)
        usr = User.objects.get(username='test1')

        self.assertEqual(usr.get_profile().address, 'Montevido 728')
        self.assertEqual(usr.get_profile().phone_number, '5557271')

    def test_profile_details(self):
        self.assert_(self.client.login(username='test1', password='test1'))

        response = self.client.post('/profiles/test1/')
        self.assertEqual(response.status_code, 200)

        profile = response.context[0]['profile']
        usr = User.objects.get(username='test1')
        profile_from_db = usr.get_profile()

        self.assertEqual(usr.get_profile().address, profile.address)
        self.assertEqual(usr.get_profile().phone_number, profile.phone_number)

    def test_update_hours_requires_login(self):
        response = self.client.post('/updatehours/test1/')
        self.assertEqual(response.status_code, 302)

    def test_update_hours(self):
        post_data = {
            'wages-TOTAL_FORMS': '1',
            'wages-INITIAL_FORMS': '0',
            'wages-MAX_NUM_FORMS': '',

            'avghours-TOTAL_FORMS': '0',
            'avghours-INITIAL_FORMS': '0',
            'avghours-MAX_NUM_FORMS': '',

            'wages-0-date': '2012-05-17',
            'wages-0-amount_per_hour': '5',
        }
        self.assertTrue(self.client.login(username='test1', password='test1'))
        response = self.client.post('/updatehours/test1/', post_data)

        self.assertEqual(response.status_code, 200)

        usr = User.objects.get(username='test1')
        wage = Wage.objects.get(user=usr, date=date(2012, 5, 17))

        self.assertEqual(wage.amount_per_hour, 5)

    def test_update_hours_repeated_date(self):
        post_data = {
            'wages-TOTAL_FORMS': '0',
            'wages-INITIAL_FORMS': '0',
            'wages-MAX_NUM_FORMS': '',

            'avghours-TOTAL_FORMS': '1',
            'avghours-INITIAL_FORMS': '0',
            'avghours-MAX_NUM_FORMS': '',

            'avghours-0-date': '2008-03-31',
            'avghours-0-hours': '5',
        }
        self.assertTrue(self.client.login(username='test1', password='test1'))
        response = self.client.get('/updatehours/test1/')
        self.assertEqual(response.status_code, 200)

        response = response.client.post('/updatehours/test1/', post_data)
        self.assertEqual(response.status_code, 200)

        # List of avghours_form's errors
        list_errors = response.context['avghours_form'].errors
        self.assertNotEqual([], list_errors)

    def test_eff_query(self):
        context = {
            'from_date': '2008-04-13',
            'to_date': '2008-04-20'}

        self.assert_(self.client.login(username='test1', password='test1'))
        response = self.client.get('/efi/', context)
        self.assertEqual(response.status_code, 200)

        q = UserProfile.objects.all()
        xs = [Data(i, date(2008, 04, 13), date(2008, 04, 20)) for i in q]
        self.assertEqual(response.context[0]['object_list'], xs)

    def test_eff_query_actual_week_redirects(self):

        self.assert_(self.client.login(username='test1', password='test1'))
        response = self.client.get('/efi/semanaactual/', {})
        self.assertEqual(response.status_code, 302)

        # Esta es la unica forma que encontre de conocer a donde redirecciona.
        url = dict(response.items())['Location']
        i = url.index("/efi")
        url = url[i:]

        today = date.today()
        # last sunday
        from_date = today - timedelta(days=today.isoweekday() % 7)
        # next saturday
        to_date = from_date + timedelta(days=6)
        correct_url = "/efi/?from_date=%s&to_date=%s" % (from_date, to_date)

        self.assertEqual(url, correct_url)

    def test_successful_password_change(self):
        self.assert_(self.client.login(username='test1', password='test1'))
        context = {'user': self.usr.id,
                   'password': 'secret',
                   'password2': 'secret'}
        response = self.client.post('/efi/administration/users_password/',
            context)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        self.assert_(self.client.login(username='test1', password='secret'))

    def test_unsuccessful_password_change_do_not_match(self):
        self.assert_(self.client.login(username='test1', password='test1'))
        context = {'user': self.usr.id,
                   'password': 'secret',
                   'password2': 'secret2'}
        response = self.client.post('/efi/administration/users_password/',
            context)
        self.assertEqual(response.status_code, 200)
        self.assert_('Invalid Form' in response.context[0]['errors'])
        self.assert_('The two passwords do not match.' in \
            response.context[0]['form'].errors['__all__'])

    def test_unchanged_password(self):
        self.assert_(self.client.login(username='test1', password='test1'))
        context = {'user': self.usr.id,
                   'password': '',
                   'password2': ''}
        response = self.client.post('/efi/administration/users_password/',
            context)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        self.assert_(self.client.login(username='test1', password='test1'))

    def test_edit_profile_user_change(self):

        self.assert_(self.client.login(username='test1', password='test1'))

        context = {'address': 'Montevido 728', 'phone_number': '5557271',
                    'first_name': 'Test First Name',
                    'last_name': 'Test Last Name',
                    'city': 'Test City', 'state': 'Test State',
                    'country': 'Test Country',
                    'personal_email': 'dont@know.com'
                    }

        response = self.client.post('/profiles/edit/', context)
        self.assertEqual(response.status_code, 302)

        usr = User.objects.get(username='test1')

        self.assertEqual(usr.get_profile().address, 'Montevido 728')
        self.assertEqual(usr.get_profile().phone_number, '5557271')
        self.assertEqual(usr.get_profile().city, 'Test City')
        self.assertEqual(usr.get_profile().state, 'Test State')
        self.assertEqual(usr.get_profile().country, 'Test Country')
        self.assertEqual(usr.get_profile().personal_email, 'dont@know.com')
        self.assertEqual(usr.first_name, 'Test First Name')
        self.assertEqual(usr.last_name, 'Test Last Name')

    def test_successful_user_add(self):
        self.assert_(self.client.login(username='test1', password='test1'))
        context = {'username': 'test2',
                   'password': 'secret',
                   'password2': 'secret'}
        response = self.client.post('/efi/administration/add_user/', context)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        self.assert_(self.client.login(username='test2', password='secret'))

    def test_add_existing_user(self):
        self.assert_(self.client.login(username='test1', password='test1'))
        context = {'username': 'test2',
                   'password': 'secret',
                   'password2': 'secret'}
        response = self.client.post('/efi/administration/add_user/', context)
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/efi/administration/add_user/', context)
        self.assertEqual(response.status_code, 200)
        self.assert_('Invalid Form' in response.context[0]['errors'])
        self.assert_('User already exists.' in response.context[0]['form'].errors['__all__'])

    def test_add_user_getparm(self):
        self.assert_(self.client.login(username='test1', password='test1'))
        context = {'user': 'test2'}
        response = self.client.get('/efi/administration/add_user/', context)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[0]['form'].initial['username'],
            'test2')

    def test_client_report_access(self):
        from eff.models import Client as EffClient
        cli_name = "test client, test.client....;(*&^$#@"
        from django.template.defaultfilters import slugify
        source, is_done = ExternalSource.objects.get_or_create(name='Example')
        client = EffClient.objects.create(name=cli_name,
                                          slug=slugify(cli_name),
                                          external_source=source)
        context = {'from_date': '2010-01-01',
                   'to_date': '2010-07-10'}
        response = self.client.get('/efi/reporte_cliente/%s/' % (client.slug, ),
            context)
        self.assertEqual(response.status_code, 302)

    def test_edit_profile_access_and_redirect(self):
        self.assert_(self.client.login(username='test1', password='test1'))
        response = self.client.post('/efi/administration/users_profile/', {})
        self.assertEqual(response.status_code, 200)
        # Remove user view_billable permission to check redirection
        self.usr.user_permissions.remove(Permission.objects.get(
            codename=u'view_billable'))
        response = self.client.post('/efi/administration/users_profile/', {})
        self.assertEqual(response.status_code, 302)
        self.client.logout()

    #TODO: review this one. not sure why it doesn't update the user profile
    def test_successful_edit_profile(self):
        self.assert_(self.client.login(username='test1', password='test1'))

        context = {'user': self.usr.id,
                   'first_name': 'Test First Name',
                   'last_name': 'Test Last Name',
                   'personal_email': 'personal@email.com',
                   'address': 'Test Address 123',
                   'city': 'Test City',
                   'state': 'Test State',
                   'country': 'Test Country',
                   'phone_number': '12341234',
                   }

        response = self.client.post('/efi/administration/users_profile/',
            context)
        self.assertEqual(response.status_code, 200)
        usr = User.objects.get(username='test1')
        self.client.logout()

    def test_updatedb_perms(self):
        self.assert_(self.client.login(username='test1', password='test1'))
        response = self.client.get('/efi/update-db/', {})
        self.assertEqual(response.status_code, 200)
        # Remove user view_billable permission to check redirection
        self.usr.user_permissions.remove(Permission.objects.get(
            codename=u'view_billable'))
        response = self.client.get('/efi/update-db/', {})
        self.assertEqual(response.status_code, 302)
        self.client.logout()

    def test_user_report_perms(self):
        # A user with no perms
        usr = User.objects.create_user(username='test2',
                                       email='test2@test.com',
                                       password='test2')
        self.assert_(self.client.login(username='test1', password='test1'))

        context = {'from_date': '2010-06-30', 'to_date': '2010-06-30'}
        response = self.client.get('/efi/reporte/' + self.usr.username + '/',
            context)
        self.assertEqual(response.status_code, 200)
        context = {'from_date': '2010-06-30', 'to_date': '2010-06-30'}
        response = self.client.get('/efi/reporte/' + usr.username + '/',
            context)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        self.assert_(self.client.login(username='test2', password='test2'))
        response = self.client.get('/efi/reporte/' + usr.username + '/',
            context)
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/efi/reporte/' + self.usr.username + '/',
            context)
        self.assertEqual(response.status_code, 302)

        def _test_prev_next_button(self, url):
            url_start = url
            check = self.client.login(username="test1", password="test1")
            self.assertTrue(check)
            response = self.client.get(url_start)
            self.assertEqual(response.status_code, 200)
            query = PyQuery(response.content)

            # Test prev button
            a_prev = query('#prev>a')
            url_prev = a_prev.attr('href')
            response_prev = self.client.get(url_prev)
            self.assertEqual(response_prev.status_code, 200)

            # Test next button
            a_next = query('#prev>a')
            url_next = a_next.attr('href')
            response_next = self.client.get(url_next)
            self.assertEqual(response_next.status_code, 200)

        def test_include_navlinks_into_reporte_cliente(self):
            """
            Test
            view: eff_client_report
            template: reporte_cliente.html
             """
            self._test_prev_next_button('/efi/reporte_cliente/fake-client-1/'\
                '?from_date=2008-03-04&to_date=2008-04-29')

        def test_include_navlinks_into_eff_query(self):
            """
            Test
            view: eff
            template: eff_query.html
            """
            self._test_prev_next_button('/efi/?from_date=2008-03-04&'\
                'to_date=2008-04-29')

        def test_include_navlinks_into_eff_charts(self):
            """
            Test
            view: eff_chart
            template: profiles/eff_charts.html
            """
            self._test_prev_next_button('efi/chart/admin/?from_date=2008-03-04'\
                '&to_date=2008-04-29')

class UserCreationTest(TestCase):

    def setUp(self):
        self.group_attachment = Group()
        self.group_attachment.name = 'attachments'
        self.group_attachment.save()

    def test_group_attachment_added_to_new_user(self):
        data = {'username': 'test_att',
                'password1': 'test_att',
                'password2': 'test_att',
                'email': 'test_att@test.com',
                'last_login': datetime.now(),
                'date_joined': datetime.now()}
        form = UserAdminForm(data)
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.save(), User)
        user = User.objects.get(username='test_att')
        self.assertEqual(self.group_attachment, user.groups.get(
                         name='attachments'))



class UserProfileCreationTest(TestCase):

    def test_user_profile_created_automatically(self):
        new_user = User.objects.create_user(username='test',
                                             email='test@except.com.ar',
                                             password='test1')
        try:
            profile = UserProfile.objects.get(user=new_user)
        except UserProfile.DoesNotExist:
            self.fail('No se creo el UserProfile')
        else:
            self.assert_(profile.id)


class UserProfileTest(TestCase):

    def setUp(self):
        self.user_machinalis = User.objects.create_user(username='user_default',
                                     email='user_default@except.com.ar',
                                     password='user_default')
        self.user_client = User.objects.create_user(username='user_client',
                                     email='user_client@except.com.ar',
                                     password='user_client')
        self.user_client.first_name = 'first'
        self.user_client.last_name = 'last'
        self.user_client.save()
        source, is_done = ExternalSource.objects.get_or_create(name='Example')
        self.company = EffClient(name='client_test', slug='client_test_slug',
                           address='test123', city='test123',
                           country='test123',
                           billing_email_address='test123@test.com',
                           external_source=source)
        self.company.save()
        try:
            profile = UserProfile.objects.get(user=self.user_client)
            profile.user_type = "Client"
            profile.company = self.company
            profile.job_position = "Job position 1"
            profile.save()
        except UserProfile.DoesNotExist:
            self.fail('No se creo el UserProfile')
        else:
            self.assert_(profile.id)

    def test_modifying_user_type_client_must_have_required_fields(self):
        try:
            profile = self.user_client.get_profile()
            profile.company = None
            self.assertRaises(ValidationError, profile.save())
        except UserProfile.DoesNotExist:
            self.fail('Do not have UserProfile')

    def test_modifying_not_client_dont_must_have_company_or_job_position(self):
        try:
            profile = self.user_machinalis.get_profile()
            profile.company = self.company
            profile.job_position = 'Job position 1'
            self.assertRaises(ValidationError, profile.save())
        except UserProfile.DoesNotExist:
            self.fail('Do not have UserProfile')

    def test_create_user_type_client(self):
        data = {'username': 'test1',
                'password1': 'test1',
                'password2': 'test1',
                'first_name': 'test1',
                'last_name': 'test1',
                'email': 'client@test.com',
                'is_client': True,
                'company': self.company.id,
                'last_login': datetime.now(),
                'date_joined': datetime.now()}
        form = UserAdminForm(data)
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.save(), User)

    def test_create_user_type_client_without_first_name(self):
        data = {'username': 'test1',
                'password': 'test1',
                'is_client': True,
                'company': self.company.id,
                'first_name': '',
                'last_name': 'test1',
                'last_login': datetime.now(),
                'date_joined': datetime.now()}
        form = UserAdminForm(data)
        self.assertFalse(form.is_valid())

    def test_create_user_type_client_without_last_name(self):
        data = {'username': 'test1',
                'password': 'test1',
                'is_client': True,
                'company': self.company.id,
                'first_name': 'test1',
                'last_name': '',
                'last_login': datetime.now(),
                'date_joined': datetime.now()}
        form = UserAdminForm(data)
        self.assertFalse(form.is_valid())

    def test_create_user_type_client_without_company(self):
        data = {'username': 'test1',
                'password': 'test1',
                'is_client': True,
                'company': '',
                'first_name': 'test1',
                'last_name': 'test1',
                'last_login': datetime.now(),
                'date_joined': datetime.now()}
        form = UserAdminForm(data)
        self.assertFalse(form.is_valid())

    def test_send_email_when_userprofile_basic_data_changed(self):
        client = Client()
        count_mails = len(mail.outbox)
        self.assertTrue(client.login(username='user_client',
            password='user_client'))
        response = client.get('/profiles/edit/')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        response = response.client.post("/profiles/edit/",
            {'job_position': 'Job position 2',
             'first_name': self.user_client.first_name,
             'last_name': self.user_client.last_name,
             'email': self.user_client.email,
             'handles-TOTAL_FORMS': '1',
             'handles-INITIAL_FORMS': '0',
             'handles-MAX_NUM_FORMS': ''})
        # Check that the response is 302 OK.
        self.assertEqual(response.status_code, 302)
        sent_email = False
        if count_mails < len(mail.outbox):
            sent_email = True
        self.assertTrue(sent_email)
        self.assertEqual(mail.outbox[-1].subject,
            'Client first last has change')

    def test_send_email_when_userprofile_handle_added(self):
        client = Client()
        handle = Handle(protocol='msn')
        handle.save()
        count_mails = len(mail.outbox)
        self.assertTrue(client.login(username='user_client',
            password='user_client'))
        response = client.get('/profiles/edit/')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        response = response.client.post("/profiles/edit/",
            {'handles-TOTAL_FORMS': '1',
             'handles-INITIAL_FORMS': '0',
             'handles-MAX_NUM_FORMS': '',

             'handles-0-address': 'La calle de mi casa',
             'handles-0-handle': handle.id
            })
        # Check that the response is 302 OK.
        self.assertEqual(response.status_code, 200)
        sent_email = False
        if count_mails < len(mail.outbox):
            sent_email = True
        self.assertTrue(sent_email)
        self.assertEqual(mail.outbox[-1].subject,
            'Client first last has change')

    def test_send_email_when_userprofile_handle_changed(self):
        client = Client()
        handle = Handle(protocol='msn')
        handle.save()
        clienthandle = ClientHandles(handle=handle,
            client=self.user_client.get_profile(), address='Mi casita')
        clienthandle.save()
        handle2 = Handle(protocol='facebook')
        handle2.save()
        count_mails = len(mail.outbox)
        self.assertTrue(client.login(username='user_client',
            password='user_client'))
        response = client.get('/profiles/edit/')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        response = response.client.post("/profiles/edit/",
            {'handles-TOTAL_FORMS': '1',
             'handles-INITIAL_FORMS': '0',
             'handles-MAX_NUM_FORMS': '',

             'handles-0-address': 'La calle de mi casa',
             'handles-0-handle': handle2.id
            })
        # Check that the response is 302 OK.
        self.assertEqual(response.status_code, 200)
        sent_email = False
        if count_mails < len(mail.outbox):
            sent_email = True
        self.assertTrue(sent_email)
        self.assertEqual(mail.outbox[-1].subject,
            'Client first last has change')

    def test_client_user_can_edit_his_profile_basic_data(self):
        client = Client()
        self.assertTrue(client.login(username='user_client',
            password='user_client'))
        response = client.get('/profiles/edit/')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        response = response.client.post("/profiles/edit/",
            {'first_name': 'pepe',
             'last_name': self.user_client.last_name,
             'email': self.user_client.email,
             'handles-TOTAL_FORMS': '1',
             'handles-INITIAL_FORMS': '0',
             'handles-MAX_NUM_FORMS': ''})
        # Check that the response is 302 OK.
        self.assertEqual(response.status_code, 302)
        user_client_changed = User.objects.get(username='user_client')
        self.assertEqual(user_client_changed.first_name, 'pepe')

    def test_client_user_can_add_handle_data(self):
        client = Client()
        handle = Handle(protocol='msn')
        handle.save()
        self.assertTrue(client.login(username='user_client',
            password='user_client'))
        response = client.get('/profiles/edit/')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        response = response.client.post("/profiles/edit/",
            {'handles-TOTAL_FORMS': '1',
             'handles-INITIAL_FORMS': '0',
             'handles-MAX_NUM_FORMS': '',

             'handles-0-address': 'La calle de mi casa',
             'handles-0-handle': handle.id
             })
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        u = User.objects.get(username='user_client')
        h = ClientHandles.objects.get(client=u.get_profile())
        self.assertEqual(h.address, 'La calle de mi casa')

    def test_client_user_can_edit_his_profile_handle_data(self):
        client = Client()
        handle = Handle(protocol='msn')
        handle.save()
        ch = ClientHandles(handle=handle, client=self.user_client.get_profile(),
            address='La calle de mi barrio')
        ch.save()
        self.assertTrue(client.login(username='user_client',
            password='user_client'))
        response = client.get('/profiles/edit/')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        response = response.client.post("/profiles/edit/",
            {'handles-TOTAL_FORMS': '2',
             'handles-INITIAL_FORMS': '1',
             'handles-MAX_NUM_FORMS': '',

             'handles-0-address': 'Otra calle',
             'handles-0-id': ch.id,
             'handles-0-handle': handle.id
             })
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        u = User.objects.get(username='user_client')
        h = ClientHandles.objects.get(client=u.get_profile())
        self.assertEqual(h.address, 'Otra calle')


class ActiveTest(TestCase):

    def setUp(self):
        self.today = date.today()
        self.delta = timedelta(days=8)
        self.from_date = self.today - self.delta
        self.to_date = self.today + self.delta

        self.u = User.objects.create_user(username='ger',
                                          email='ger@german.com',
                                          password='ger')
        self.u.save()

        self.up = UserProfile.objects.get(user=self.u)
        self.up.address = 'direccion 123'
        self.up.phone_number = '1234567'
        self.up.save()

    def tearDown(self):
        for ah in self.u.avghours_set.all():
            ah.delete()
        self.up.delete()
        self.u.delete()

    def test_user_active(self):
        ah = AvgHours(date=self.today, hours=5, user=self.u)
        ah.save()
        self.assert_(hasattr(UserProfile, 'is_active'))
        self.assert_(self.u.get_profile().is_active(self.from_date,
            self.to_date))
        ah.delete()

    def test_user_not_active(self):
        self.assertFalse(self.u.get_profile().is_active(self.from_date,
            self.to_date))

    def test_user_active_partially(self):
        ah = AvgHours(date=self.today, hours=5, user=self.u)
        ah.save()

        avg = AvgHours(date=(self.today - timedelta(days=3)), hours=5,
            user=self.u)
        avg.save()
        self.assert_(self.u.get_profile().is_active(self.from_date,
        self.to_date))
        avg.delete()
        ah.delete()

    def test_user_active_partially_1(self):
        avg = AvgHours(date=(self.today - timedelta(days=10)), hours=5,
            user=self.u)
        avg.save()
        self.assert_(self.u.get_profile().is_active(self.from_date,
            self.to_date))
        avg.delete()

    def test_user_active_partially_2(self):
        ah = AvgHours(date=self.today, hours=5, user=self.u)
        avg = AvgHours(date=(self.today - timedelta(days=3)), hours=0,
            user=self.u)
        avg1 = AvgHours(date=(self.today + timedelta(days=4)), hours=0,
            user=self.u)
        ah.save()
        avg.save()
        avg1.save()
        self.assert_(self.u.get_profile().is_active(self.from_date,
            self.to_date))
        avg.delete()
        avg1.delete()
        ah.delete()

    def test_user_active_partially_3(self):
        avg_list = [
            AvgHours(date=(self.from_date - timedelta(days=10)), hours=5,
                user=self.u),
            AvgHours(date=(self.to_date + timedelta(days=1)), hours=5,
                user=self.u),
            AvgHours(date=self.from_date, hours=0, user=self.u),
            AvgHours(date=self.to_date, hours=0, user=self.u)]
        self.assertFalse(self.u.get_profile().is_active(self.from_date,
            self.to_date))


class ExternalSourceTest(TestCase):

    def setUp(self):
        self.item = ExternalSource()

    def test_has_name(self):
        for i in ['name', 'fetch_url', 'username', 'password', 'csv_directory',
            'csv_filename']:
            self.assert_(hasattr(self.item, i))


class ProjectsTest(TestCase):

    def setUp(self):
        source, is_done = ExternalSource.objects.get_or_create(name='Example')
        client = EffClient(name='client_test', slug='client_test_slug',
                           address='test123', city='test123',
                           country='test123',
                           billing_email_address='test123@test.com',
                           external_source=source)
        client.save()
        self.project = Project(name='projecto_test', billable=False,
            client=client, start_date=date.today())
        self.project.save()

    def tearDown(self):
        self.project.delete()

    def test_has_attributes(self):
        for attr in ('name', 'billable', 'external_id', 'members',
                     'billing_type', 'fixed_price', 'get_external_source'):
            self.assert_(hasattr(self.project, attr))


class TimeLogsAttributesTest(TestCase):

    def setUp(self):
        source, is_done = ExternalSource.objects.get_or_create(name='Example')
        client = EffClient.objects.create(
            name='client_test',
            slug='client_test_slug',
            address='test123',
            city='test123',
            country='test123',
            billing_email_address='test123@test.com',
            external_source=source)
        project = Project.objects.create(name='projecto_test',
                                         billable=False,
                                         client=client,
                                         start_date=date.today())
        usr = User.objects.create(username='test1',
                                  email='test1@test.com',
                                  password='test1')
        dump = Dump.objects.create(date=date.today(), creator='test123')
        self.log = TimeLog(date=date.today(), project=project, user=usr,
            hours_booked=0.0, dump=dump)

    def test_has_attributes(self):
        for attr in ('date', 'project', 'task_name', 'user',
                     'hours_booked', 'description', 'dump'):
            self.assert_(hasattr(self.log, attr))


class CommercialDocumentsTest(TestCase):
    def setUp(self):
        # Create some data for tests
        # An external source
        ext_src = ExternalSourceFactory(name='DotprojectMachinalis')
        # A client
        client = ClientFactory(name='client', external_source=ext_src)
        # Some commercial documents
        self.billing = BillingFactory(client=client)
        self.cnote = CreditNoteFactory(client=client)
        self.payment = PaymentFactory(client=client)

    def test_billing_has_attributes(self):
        for attr in ('client', 'amount', 'date', 'concept', 'expire_date',
                     'payment_date'):
            self.assert_(hasattr(self.billing, attr))

    def test_payment_has_attributes(self):
        for attr in ('client', 'amount', 'date', 'concept', 'status'):
            self.assert_(hasattr(self.payment, attr))

    def test_credit_note_has_attributes(self):
        for attr in ('client', 'amount', 'date', 'concept'):
            self.assert_(hasattr(self.cnote, attr))


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(QueriesTest))
    suite.addTest(makeSuite(PageTest))
    suite.addTest(makeSuite(UserProfileCreationTest))
    suite.addTest(makeSuite(UserCreationTest))
    suite.addTest(makeSuite(ActiveTest))
    suite.addTest(makeSuite(ExternalSourceTest))
    suite.addTest(makeSuite(ProjectsTest))
    suite.addTest(makeSuite(TimeLogsAttributesTest))
    suite.addTest(makeSuite(UserProfileTest))
    suite.addTest(makeSuite(CommercialDocumentsTest))
    return suite
