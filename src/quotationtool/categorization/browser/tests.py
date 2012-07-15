import unittest
import doctest
from zope.component.testing import setUp, tearDown, PlacelessSetup
from zope.testing.cleanup import cleanUp
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope.configuration.xmlconfig import XMLConfig
from zope.component import hooks

import quotationtool.categorization

from quotationtool.categorization import testing
from quotationtool.categorization.browser import datamanager


def setUpDataManager(test):
    tearDownPlaces(test)
    test.globs = {'root': placefulSetUp(True)} # placeful setup
    root = test.globs['root']
    hooks.setSite(root)
    testing.generateCategorizableItemDescriptions(root)
    XMLConfig('configure.zcml', quotationtool.categorization)()


def tearDownPlaces(test):
    placefulTearDown()
    from zope.schema.vocabulary import _clear
    _clear()


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(datamanager,
                             setUp = setUpDataManager,
                             tearDown = tearDownPlaces,
                             optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                             ),
        ))
