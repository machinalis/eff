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

from django.db import models
from customfields import MoneyField


class ComercialDocumentBase(models.Model):
    client = models.ForeignKey('Client')
    date = models.DateField()
    concept = models.TextField()
    amount = MoneyField()

    class Meta:
        app_label = 'eff'
        ordering = ['client', '-date']

    def __unicode__(self):
        return u'%s, -%s, %s' % (self.client, self.amount, self.date)


class Billing(ComercialDocumentBase):
    expire_date = models.DateField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    #Billing._meta.get_field('date').verbose_name = 'Send date'

    class Meta:
        app_label = 'eff'
        ordering = ['client', '-date']

    def __unicode__(self):
        return u'%s, %s, %s' % (self.client, self.amount, self.date)


class CreditNote(ComercialDocumentBase):
    pass

    class Meta:
        app_label = 'eff'
        ordering = ['client', '-date']


class Payment(ComercialDocumentBase):
    NOTIFIED = 'Notified'
    TRACKING = 'Tracking'
    CONFIRMED = 'Confirmed'
    STATUS_CHOICES = (
        ('Notified', NOTIFIED),
        ('Tracking', TRACKING),
        ('Confirmed', CONFIRMED),
    )
    status = models.CharField(max_length=20, default=NOTIFIED,
                              choices=STATUS_CHOICES)

    class Meta:
        app_label = 'eff'
        ordering = ['client', '-date']
