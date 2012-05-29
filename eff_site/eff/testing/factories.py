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

import factory
from django.contrib.auth.models import User
from eff.models import UserProfile, Client, ProjectAssoc, TimeLog, AvgHours
from eff.models import Project, TimeLog, ExternalSource, Currency, Dump
from django.template.defaultfilters import slugify

from decimal import Decimal
from datetime import date, timedelta
import random


class UserFactory(factory.Factory):
    FACTORY_FOR = User

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user

    username = factory.Sequence(lambda n: 'test%s' % n)
    email = factory.LazyAttribute(lambda o: '%s@test.com' % o.username)
    password = factory.LazyAttribute(lambda o: '%s' % o.username)
    first_name = factory.LazyAttribute(lambda o: '%s' % o.username)
    last_name = factory.LazyAttribute(lambda o: '%s' % o.username)


class AdminFactory(factory.Factory):
    FACTORY_FOR = User

    username = 'admin'
    email = 'admin@test.com'
    password = 'admin'
    is_active = True
    is_superuser = True


class UserProfileFactory(factory.Factory):
    FACTORY_FOR = UserProfile

    user = factory.SubFactory(UserFactory)


class CurrencyFactory(factory.Factory):
    FACTORY_FOR = Currency

    ccy_code = 'USD'


class ExternalSourceFactory(factory.Factory):
    FACTORY_FOR = ExternalSource

    name = factory.Sequence(lambda n: 'source%s' % n)


class ClientFactory(factory.Factory):
    FACTORY_FOR = Client

    name = factory.Sequence(lambda n: 'Fake Client %s' % n)
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    address = factory.Sequence(lambda n: 'stTest%s' % n)
    city = factory.Sequence(lambda n: 'cityTest%s' % n)
    country = factory.Sequence(lambda n: 'countryTest%s' % n)
    billing_email_address = factory.LazyAttribute(lambda o: '%s@test.com' \
                                                  % o.slug)
    external_source = factory.SubFactory(ExternalSourceFactory)


class ProjectFactory(factory.Factory):
    FACTORY_FOR = Project

    name = factory.Sequence(lambda n: 'Fake Project %s' % n)
    billable = True
    client = factory.SubFactory(ClientFactory)
    billing_type = 'HOUR'


class ProjectAssocFactory(factory.Factory):
    FACTORY_FOR = ProjectAssoc

    project = factory.SubFactory(ProjectFactory)
    member = factory.SubFactory(UserProfileFactory)
    client_rate = Decimal(str(0.53))
    user_rate = Decimal(str(0.34))
    from_date = date.today() - timedelta(days=30)
    to_date = date.today()


class DumpFactory(factory.Factory):
    FACTORY_FOR = Dump

    date = date.today() - timedelta(days=random.choice(xrange(366)))
    creator = 'test123'
    source = factory.SubFactory(ExternalSourceFactory)


class TimeLogFactory(factory.Factory):
    FACTORY_FOR = TimeLog

    date = date.today() - timedelta(days=random.choice(xrange(366)))
    project = factory.SubFactory(ProjectFactory)
    task_name = factory.Sequence(lambda n: 'Task%s' % n)
    user = factory.SubFactory(UserFactory)
    hours_booked = Decimal('8.000')
    description = factory.Sequence(lambda n: 'Log %s' % n)
    dump = factory.SubFactory(DumpFactory)
