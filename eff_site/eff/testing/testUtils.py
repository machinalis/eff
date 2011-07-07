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
from eff.utils import overtime_period, period

from unittest import TestSuite, makeSuite
from datetime import date

next_period = lambda d1, d2: period(d1, d2, lambda d1, d2: d1 + d2)
previous_period  = lambda d1, d2: period(d1, d2, lambda d1, d2: d1 - d2)

class TestNextPeriod(TestCase):

    # next

    def test_next_period_week(self):
        f_date = date(2008,5,11)
        t_date = date(2008,5,18)
        self.assertEqual(next_period(f_date, t_date), (date(2008,5,19), date(2008,5,26)))

    def test_next_period_week_1(self):
        f_date = date(2008,5,25)
        t_date = date(2008,6,1)
        self.assertEqual(next_period(f_date, t_date), (date(2008,6,2), date(2008,6,9)))

    def test_next_period_dos_weeks(self):
        f_date = date(2008,5,4)
        t_date = date(2008,5,17)
        self.assertEqual(next_period(f_date, t_date), (date(2008,5,18), date(2008,5,31)))

    def test_next_period_15_al_15(self):
        f_date = date(2008,5,15)
        t_date = date(2008,6,14)
        self.assertEqual(next_period(f_date, t_date), (date(2008,6,15), date(2008,7,15)))

    def test_next_period_week_fin_de_anio(self):
        f_date = date(2008,12,28)
        t_date = date(2009,1,4)
        self.assertEqual(next_period(f_date, t_date), (date(2009,1,5), date(2009,1,12)))

    def test_next_period_anio(self):
        f_date = date(2008,5,21)
        t_date = date(2009,5,20)
        self.assertEqual(next_period(f_date, t_date), (date(2009,5,21), date(2010,5,20)))

    def test_next_period_anio_1(self):
        f_date = date(2008,1,1)
        t_date = date(2008,12,31)
        self.assertEqual(next_period(f_date, t_date), (date(2009,1,1), date(2009,12,31)))

class TestPreviousPeriod(TestCase):

    # previous

    def test_previous_period_week(self):
        f_date = date(2008,5,11)
        t_date = date(2008,5,17)
        self.assertEqual(previous_period(f_date, t_date), (date(2008,5,4), date(2008,5,10)))

    def test_previous_period_week_1(self):
        f_date = date(2008,5,25)
        t_date = date(2008,6,1)
        self.assertEqual(previous_period(f_date, t_date), (date(2008,5,17), date(2008,5,24)))

    def test_previous_period_dos_weeks(self):
        f_date = date(2008,5,4)
        t_date = date(2008,5,18)
        self.assertEqual(previous_period(f_date, t_date), (date(2008,4,19), date(2008,5,3)))

    def test_previous_period_mes(self):
        f_date = date(2008,5,1)
        t_date = date(2008,5,31)
        self.assertEqual(previous_period(f_date, t_date), (date(2008,3,31), date(2008,4,30)))

    def test_previous_period_15_al_15(self):
        f_date = date(2008,5,15)
        t_date = date(2008,6,14)
        self.assertEqual(previous_period(f_date, t_date), (date(2008,4,14), date(2008,5,14)))

    def test_previous_period_week_fin_de_anio(self):
        f_date = date(2008,12,28)
        t_date = date(2009,1,4)
        self.assertEqual(previous_period(f_date, t_date), (date(2008,12,20), date(2008,12,27)))

    def test_previous_period_anio(self):
        f_date = date(2008,5,20)
        t_date = date(2009,5,20)
        self.assertEqual(previous_period(f_date, t_date), (date(2007,5,19), date(2008,5,19)))

    def test_previous_period_anio_1(self):
        f_date = date(2008,1,1)
        t_date = date(2008,12,31)
        self.assertEqual(previous_period(f_date, t_date), (date(2007,1,1), date(2007,12,31)))

class TestOvertimePeriod(TestCase):

    # overtime_period

    def test_overtime_period_before_end(self):
        a_date = date(2008,8,15)
        self.assertEqual(overtime_period(a_date), (date(2008,7,20), date(2008,8,16)))

    def test_overtime_period_while_ending(self):
        a_date = date(2008,8,16)
        self.assertEqual(overtime_period(a_date), (date(2008,7,20), date(2008,8,16)))

    def test_overtime_period_after_end(self):
        a_date = date(2008,8,17)
        self.assertEqual(overtime_period(a_date), (date(2008,8,17), date(2008,9,20)))

    def test_overtime_period_if_first_day_is_sunday(self):
        self.assertEqual(overtime_period(date(2008,6,14)), (date(2008,5,18), date(2008,6,14)))
        self.assertEqual(overtime_period(date(2008,6,15)), (date(2008,6,15), date(2008,7,19)))
        self.assertEqual(overtime_period(date(2008,6,22)), (date(2008,6,15), date(2008,7,19)))
        self.assertEqual(overtime_period(date(2008,7,19)), (date(2008,6,15), date(2008,7,19)))
        self.assertEqual(overtime_period(date(2008,7,20)), (date(2008,7,20), date(2008,8,16)))

def suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestNextPeriod))
    suite.addTest(makeSuite(TestPreviousPeriod))
    suite.addTest(makeSuite(TestOvertimePeriod))
    return suite
