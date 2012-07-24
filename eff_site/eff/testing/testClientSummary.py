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

from django.contrib.auth.models import User
from django.db.models import signals
from eff._models.user_profile import create_profile_for_user
from django.test import TestCase
from unittest import TestSuite, makeSuite
from django.core.urlresolvers import reverse
from django.test.client import Client as TestClient
from urllib import urlencode
from decimal import Decimal
from eff.models import Billing
from factories import (ClientProfileFactory, ClientFactory, AdminFactory,
                       ExternalSourceFactory, UserFactory, BillingFactory,
                       CreditNoteFactory, PaymentFactory)
from datetime import date, timedelta


class HelperTest(TestCase):

    def setUp(self):

        # Disconnect signals so there's no problem to use UserProfileFactory
        signals.post_save.disconnect(
            dispatch_uid='eff._models.user_profile.create_profile_for_user',
            sender=User)

        # Create a external source
        self.ext_src = ExternalSourceFactory(name='DotprojectMachinalis')

        # Create 2 client user and 2 companies.
        self.company1 = ClientFactory(name='Fake Client 1',
                                 external_source=self.ext_src)
        user = UserFactory(username='client1')
        self.client1 = ClientProfileFactory(user=user,
                                          company=self.company1)
        user = UserFactory(username='client2')
        company2 = ClientFactory(name='Fake Client 2',
                                 external_source=self.ext_src)
        self.client2 = ClientProfileFactory(user=user,
                                          company=company2)

        # Create some commercial documents
        for company in [self.company1, company2]:
            BillingFactory(client=company, amount=1000, date=date(2012, 5, 3),
                           concept="Billing1 " + company.name,
                           expire_date=date(2012, 5, 30),
                           payment_date=date(2012, 5, 25))
            BillingFactory(client=company, amount=1200, date=date(2012, 5, 1),
                           concept="Billing2 " + company.name,
                           expire_date=date(2012, 5, 30),
                           payment_date=date(2012, 5, 25))
            CreditNoteFactory(client=company, amount=100, date=date(2012, 5, 4),
                              concept="CreditNote1 " + company.name)
            CreditNoteFactory(client=company, amount=200, date=date(2012, 5, 2),
                              concept="CreditNote2 " + company.name)
            PaymentFactory(client=company, amount=1500, date=date(2012, 5, 2),
                           concept="Payment1 " + company.name,
                           status="Notified")
            PaymentFactory(client=company, amount=1600, date=date(2012, 5, 7),
                           concept="Payment2 " + company.name,
                           status="Tracking")

        self.test_client = TestClient()

    def tearDown(self):
        # re connect signals
        signals.post_save.connect(
            create_profile_for_user, sender=User,
            dispatch_uid='eff._models.user_profile.create_profile_for_user')


class ClientSummaryTest(HelperTest):

    def setUp(self):
        super(ClientSummaryTest, self).setUp()

        self.test_client.login(username=self.client1.user.username,
                               password=self.client1.user.username)

    def test_get_summary_limit1(self):
        # Tests that summary is generated when from_date is equal to to_date.
        summary = self.company1.get_summary('2012-5-01', '2012-5-01')
        expected = ([{'concept': u'Billing2 Fake Client 1',
                      'date': date(2012, 5, 1),
                      'doc': Billing.objects.get(client=self.company1,
                                              concept='Billing2 Fake Client 1'),
                      'extra': {'Fecha de pago': date(2012, 5, 25),
                                'Fecha de vencimiento': date(2012, 5, 30)},
                      'income': Decimal('1200.00'),
                      'outcome': Decimal('0.00'),
                      'subtotal': Decimal('1200.00')}],
                    Decimal('1200.00'),
                    Decimal('0.00'),
                    Decimal('1200.00'))
        self.assertEqual(expected, summary)

    def test_get_summary_limit2(self):
        # Tests that summary is generated when from_date is equal to to_date.
        summary = self.company1.get_summary('2012-5-01', '2012-5-01')
        expected = ([{'concept': u'Billing2 Fake Client 1',
                      'date': date(2012, 5, 1),
                      'doc': Billing.objects.get(client=self.company1,
                                              concept='Billing2 Fake Client 1'),
                      'extra': {'Fecha de pago': date(2012, 5, 25),
                                'Fecha de vencimiento': date(2012, 5, 30)},
                      'income': Decimal('1200.00'),
                      'outcome': Decimal('0.00'),
                      'subtotal': Decimal('1200.00')}],
                    Decimal('1200.00'),
                    Decimal('0.00'),
                    Decimal('1200.00'))
        self.assertEqual(expected, summary)

    # def test_get_summary_per_project_all_hours1(self):
    #     # Tests that ALL documents are summarized.
    #     summary = self.company1.get_summary('2012-5-01', '2012-5-10')
    #     expected = ([{'concept': u'Billing2 Fake Client 1',
    #                   'date': date(2012, 5, 1),
    #                   'doc': <Billing: Fake Client 1, 1200.00, 2012-05-01>,
    #                   'extra': {'Fecha de pago': date(2012, 5, 25),
    #                             'Fecha de vencimiento': date(2012, 5, 30)},
    #                   'income': Decimal('1200.00'),
    #                   'outcome': Decimal('0.00'),
    #                   'subtotal': Decimal('1200.00')},
    #                  {'concept': u'CreditNote2 Fake Client 1',
    #                   'date': date(2012, 5, 2),
    #                   'doc': <CreditNote: Fake Client 1, 200.00, 2012-05-02>,
    #                   'extra': {},
    #                   'income': Decimal('0.00'),
    #                   'outcome': Decimal('200.00'),
    #                   'subtotal': Decimal('1000.00')},
    #                  {'concept': u'Payment1 Fake Client 1',
    #                   'date': date(2012, 5, 2),
    #                   'doc': <Payment: Fake Client 1, 1500.00, 2012-05-02>,
    #                   'extra': {'Estado': u'Notified'},
    #                   'income': Decimal('0.00'),
    #                   'outcome': Decimal('1500.00'),
    #                   'subtotal': Decimal('-500.00')},
    #                  {'concept': u'Billing1 Fake Client 1',
    #                   'date': date(2012, 5, 3),
    #                   'doc': <Billing: Fake Client 1, 1000.00, 2012-05-03>,
    #                   'extra': {'Fecha de pago': date(2012, 5, 25),
    #                             'Fecha de vencimiento': date(2012, 5, 30)},
    #                   'income': Decimal('1000.00'),
    #                   'outcome': Decimal('0.00'),
    #                   'subtotal': Decimal('500.00')},
    #                  {'concept': u'CreditNote1 Fake Client 1',
    #                   'date': date(2012, 5, 4),
    #                   'doc': <CreditNote: Fake Client 1, 100.00, 2012-05-04>,
    #                   'extra': {},
    #                   'income': Decimal('0.00'),
    #                   'outcome': Decimal('100.00'),
    #                   'subtotal': Decimal('400.00')},
    #                  {'concept': u'Payment2 Fake Client 1',
    #                   'date': date(2012, 5, 7),
    #                   'doc': <Payment: Fake Client 1, 1600.00, 2012-05-07>,
    #                   'extra': {'Estado': u'Tracking'},
    #                   'income': Decimal('0.00'),
    #                   'outcome': Decimal('1600.00'),
    #                   'subtotal': Decimal('-1200.00')}],
    #                 Decimal('2200.00'),
    #                 Decimal('3400.00'),
    #                 Decimal('-1200.00'))
    #     self.assertEqual(expected, list(report))


class ChartsTest(HelperTest):

    def setUp(self):
        super(ChartsTest, self).setUp()
        # Create an Admin User.
        self.admin = AdminFactory(username='admin')

        self.test_client = TestClient()
        self.test_client.login(username=self.admin.username,
                               password=self.admin.username)

    def test_admin_can_access_eff_charts(self):
        get_data = {'dates': '2010-09-01,2012-01-01'}
        get_data = urlencode(get_data)
        url = '%s?%s' % (reverse('eff_charts'), get_data)
        response = self.test_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_acumulative_graph(self):
        get_data = {'dates': '2010-09-01,2012-01-01', 'user1': 'checked',
                    'user2': 'checked', 'SumGraph.y': '5', 'SumGraph.x': '8'}
        get_data = urlencode(get_data)
        url = '%s?%s' % (reverse('eff_charts'), get_data)
        response = self.test_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_multiple_graphs(self):
        get_data = {'dates': '2010-09-01,2012-01-01', 'user1': 'checked',
                    'user2': 'checked', 'MultGraph.y': '5', 'MultGraph.x': '8'}
        get_data = urlencode(get_data)
        url = '%s?%s' % (reverse('eff_charts'), get_data)
        response = self.test_client.get(url)
        self.assertEqual(response.status_code, 200)


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(ClientSummaryTest))
    return suite
