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
from pyquery import PyQuery
from factories import (ClientProfileFactory, ClientFactory, AdminFactory,
                       ExternalSourceFactory, UserFactory, BillingFactory,
                       CreditNoteFactory, PaymentFactory)
from datetime import date


class HelperTest(TestCase):

    def setUp(self):

        # Disconnect signals so there's no problem to use UserProfileFactory
        signals.post_save.disconnect(
            dispatch_uid='eff._models.user_profile.create_profile_for_user',
            sender=User)

        # Create a external source
        self.ext_src = ExternalSourceFactory(name='DotprojectMachinalis')

        # Create 2 client user and 2 companies.
        self.company = ClientFactory(name='Fake Client 1',
                                 external_source=self.ext_src)
        user = UserFactory(username='client1')
        self.client1 = ClientProfileFactory(user=user,
                                          company=self.company)
        user = UserFactory(username='client2')
        self.company2 = ClientFactory(name='Fake Client 2',
                                      external_source=self.ext_src)
        self.client2 = ClientProfileFactory(user=user,
                                            company=self.company2)

        # Create some commercial documents for company1
        self.billing = BillingFactory(client=self.company,
                                      amount=Decimal('1000'),
                                      date=date(2012, 5, 3),
                                      concept="Billing1 " + self.company.name,
                                      expire_date=date(2012, 5, 30),
                                      payment_date=date(2012, 5, 25))
        self.credit_note = CreditNoteFactory(client=self.company,
                                    amount=Decimal('100'),
                                    date=date(2012, 5, 4),
                                    concept="CreditNote1 " + self.company.name)
        self.payment = PaymentFactory(client=self.company,
                                      amount=Decimal('1500'),
                                      date=date(2012, 5, 2),
                                      concept="Payment1 " + self.company.name,
                                      status="Notified")

        # Create some commercial documents for company2
        BillingFactory(client=self.company2, amount=Decimal('1200'),
                       date=date(2012, 5, 1),
                       concept="Billing2 " + self.company.name,
                       expire_date=date(2012, 5, 30),
                       payment_date=date(2012, 5, 25))
        CreditNoteFactory(client=self.company2, amount=Decimal('200'),
                          date=date(2012, 5, 2),
                          concept="CreditNote2 " + self.company.name)
        PaymentFactory(client=self.company2, amount=Decimal('1600'),
                       date=date(2012, 5, 7),
                       concept="Payment2 " + self.company.name,
                       status="Tracking")
        self.test_client = TestClient()

    def tearDown(self):
        # re connect signals
        signals.post_save.connect(
            create_profile_for_user, sender=User,
            dispatch_uid='eff._models.user_profile.create_profile_for_user')


class CommercialDocumentTest(HelperTest):

    def test_billing_summary_data(self):
        extra = {}
        expected = {}
        extra['Fecha de vencimiento'] = date(2012, 5, 30)
        extra['Fecha de pago'] = date(2012, 5, 25)
        expected['date'] = date(2012, 5, 3)
        expected['concept'] = "Billing1 " + self.company.name
        expected['income'] = Decimal('1000')
        expected['outcome'] = Decimal('0.00')
        expected['subtotal'] = Decimal('1000')
        expected['extra'] = extra
        data = self.billing.get_data_for_summary()
        self.assertEqual(expected, data)

    def test_payment_summary_data(self):
        expected = {}
        expected['date'] = date(2012, 5, 2)
        expected['concept'] = "Payment1 " + self.company.name
        expected['income'] = Decimal('0.00')
        expected['outcome'] = Decimal('1500')
        expected['subtotal'] = Decimal('-1500')
        expected['extra'] = {'Estado': 'Notified'}
        data = self.payment.get_data_for_summary()
        self.assertEqual(expected, data)

    def test_credit_note_summary_data(self):
        expected = {}
        expected['date'] = date(2012, 5, 4)
        expected['concept'] = "CreditNote1 " + self.company.name
        expected['income'] = Decimal('0.00')
        expected['outcome'] = Decimal('100')
        expected['subtotal'] = Decimal('-100')
        expected['extra'] = {}
        data = self.credit_note.get_data_for_summary()
        self.assertEqual(expected, data)


class ClientSummaryTest(HelperTest):

    def setUp(self):
        super(ClientSummaryTest, self).setUp()

        docs = [self.billing, self.credit_note,
                self.payment]
        self.dates = sorted([str(doc.date) for doc in docs])
        self.concepts = sorted([doc.concept for doc in docs])
        self.amounts = sorted([str(doc.amount) + '.00' for doc in docs])

        self.test_client.login(username=self.client1.user.username,
                               password=self.client1.user.username)

    def __get_url(self, from_date='2012-05-01', to_date='2012-05-10',
                  order_by=None):
        get_data = {'from_date': from_date, 'to_date': to_date}
        if order_by:
            get_data['order_by'] = order_by
        get_data = urlencode(get_data)

        # check if the user is an admin
        user_id = self.test_client.session['_auth_user_id']
        user = User.objects.get(id=user_id)
        if user.is_superuser:
            url = '%s?%s' % (reverse('eff_client_summary',
                                     args=['fake-client-1']), get_data)
        else:
            url = '%s?%s' % (reverse('client_summary'), get_data)

        return url

    def test_get_summary_limit(self):
        # Tests that summary is generated when from_date is equal to to_date.
        summary = self.company.get_summary('2012-5-03', '2012-5-03')
        expected = ([{'concept': u'Billing1 Fake Client 1',
                      'date': date(2012, 5, 3),
                      'doc': self.billing,
                      'extra': {'Fecha de pago': date(2012, 5, 25),
                                'Fecha de vencimiento': date(2012, 5, 30)},
                      'income': Decimal('1000.00'),
                      'outcome': Decimal('0.00'),
                      'subtotal': Decimal('1000.00')}],
                    Decimal('1000.00'),
                    Decimal('0.00'),
                    Decimal('1000.00'))
        self.assertEqual(expected, summary)

    def test_get_summary(self):
        # Tests that ALL documents are summarized.
        summary = self.company.get_summary('2012-5-01', '2012-5-10')
        expected = ([{'concept': u'Payment1 Fake Client 1',
                      'date': date(2012, 5, 2),
                      'doc': self.payment,
                      'extra': {'Estado': u'Notified'},
                      'income': Decimal('0.00'),
                      'outcome': Decimal('1500.00'),
                      'subtotal': Decimal('-1500.00')},
                     {'concept': u'Billing1 Fake Client 1',
                      'date': date(2012, 5, 3),
                      'doc': self.billing,
                      'extra': {'Fecha de pago': date(2012, 5, 25),
                                'Fecha de vencimiento': date(2012, 5, 30)},
                      'income': Decimal('1000.00'),
                      'outcome': Decimal('0.00'),
                      'subtotal': Decimal('-500.00')},
                     {'concept': u'CreditNote1 Fake Client 1',
                      'date': date(2012, 5, 4),
                      'doc': self.credit_note,
                      'extra': {},
                      'income': Decimal('0.00'),
                      'outcome': Decimal('100.00'),
                      'subtotal': Decimal('-600.00')},
                     ],
                    Decimal('1000.00'),
                    Decimal('1600.00'),
                    Decimal('-600.00'))
        self.assertEqual(summary, expected)

    def test_client_summary_view_works(self):
        url = self.__get_url()
        response = self.test_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_client_cant_see_other_client_summary(self):
        get_data = {'from_date': '2012-05-01', 'to_date': '2012-05-10'}
        get_data = urlencode(get_data)
        url = '%s?%s' % (reverse('eff_client_summary', args=['fake-client-2']),
                          get_data)
        response = self.test_client.get(url)
        self.assertRedirects(response,
                             '/accounts/login/')

    def test_client_can_only_see_his_documents(self):
        url = self.__get_url()
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        table = query('table').text()
        self.assertNotIn('Billing2', table)
        self.assertNotIn('Payment2', table)
        self.assertNotIn('CreditNote2', table)

    def test_dates_are_displayed_ascending_for_each_document(self):
        url = self.__get_url(order_by='date')
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        dates = query('#account-summary-table td.fecha').text()
        self.assertEqual(self.dates, list(dates.split()))

    def test_dates_are_displayed_descending_for_each_document(self):
        url = self.__get_url(order_by='-date')
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        dates = query('#account-summary-table td.fecha').text()
        self.assertEqual(sorted(self.dates, reverse=True), list(dates.split()))

    def test_concepts_are_displayed_ascending_for_each_document(self):
        url = self.__get_url(order_by='concept')
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        concepts = query('#account-summary-table td.descripcion')
        concepts = [concepts.eq(i).text() for i in xrange(0, len(concepts))]
        self.assertEqual(self.concepts, concepts)

    def test_concepts_are_displayed_descending_for_each_document(self):
        url = self.__get_url(order_by='-concept')
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        concepts = query('#account-summary-table td.descripcion')
        concepts = [concepts.eq(i).text() for i in xrange(0, len(concepts))]
        self.assertEqual(sorted(self.concepts, reverse=True), concepts)

    def test_amounts_are_displayed_ascending_for_each_document(self):
        url = self.__get_url(order_by='amount')
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        amounts = query('#account-summary-table td.money').text()
        self.assertEqual(self.amounts, list(amounts.split()))

    def test_amounts_are_displayed_descending_for_each_document(self):
        url = self.__get_url(order_by='-amount')
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        amounts = query('#account-summary-table td.money').text()
        self.assertEqual(sorted(self.amounts, reverse=True),
                         list(amounts.split()))

    def test_subtotals_are_displayed_for_each_document(self):
        url = self.__get_url(order_by='amount')
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        subtotals = query('#account-summary-table td.subtotal').text()
        expected = ['-100.00', '900.00', '-600.00']
        self.assertEqual(expected, list(subtotals.split()))

    def test_totals_are_displayed_for_each_document(self):
        url = self.__get_url(order_by='date')
        response = self.test_client.get(url)
        query = PyQuery(response.content)
        totals = query('#account-summary-table td.total').text()
        expected = ['1000.00', '1600.00', '-600.00']
        self.assertEqual(expected, list(totals.split()))


class AdminClientSummaryTest(ClientSummaryTest):

    def setUp(self):
        super(AdminClientSummaryTest, self).setUp()
        # Create an Admin User.
        self.admin = AdminFactory(username='admin')
        self.test_client = TestClient()
        check = self.test_client.login(username=self.admin.username,
                                       password=self.admin.username)
        self.assertEqual(check, True)

    def __get_url(self, from_date='2012-05-01', to_date='2012-05-10',
                  order_by=None):
        get_data = {'from_date': from_date, 'to_date': to_date}
        if order_by:
            get_data['order_by'] = order_by
        get_data = urlencode(get_data)
        return '%s?%s' % (reverse('eff_client_summary', args=['fake-client-1']),
                          get_data)

    def test_get_summary_limit(self):
        pass

    def test_get_summary(self):
        pass

    def test_client_cant_see_other_client_summary(self):
        pass

    def test_client_can_only_see_his_documents(self):
        pass


def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(CommercialDocumentTest))
    suite.addTest(makeSuite(ClientSummaryTest))
    suite.addTest(makeSuite(AdminClientSummaryTest))
    return suite
