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


import unittest
import doctest

import reports
from _models import log, client

from eff_site.scripts import jira

from testing import testUtils
from testing import testModels
from testing import testAdmin, testReports

def suite():
    suite = unittest.TestSuite()
    suite.addTest(testUtils.suite())
    suite.addTest(testModels.suite())
    suite.addTest(testAdmin.suite())
    suite.addTest(testReports.suite())
    suite.addTest(doctest.DocTestSuite(jira))
    return suite




