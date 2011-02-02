# -*- coding: utf-8 -*-

import unittest
import doctest

import reports
from _models import log, client

from sitio.scripts import jira

from testing import testUtils
from testing import testModels

def suite():
    suite = unittest.TestSuite()
    suite.addTest(testUtils.suite())
    suite.addTest(testModels.suite())
    suite.addTest(doctest.DocTestSuite(jira))
    return suite




