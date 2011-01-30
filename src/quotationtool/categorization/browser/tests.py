import unittest
import doctest
import zope.component.testing
import zope.component.eventtesting
from zope.schema import vocabulary
from zope.app.component.vocabulary import InterfacesVocabulary
from zope.app.testing.setup import placefulSetUp
from zope.site.site import LocalSiteManager
import zope.intid
from zope.keyreference.persistent import KeyReferenceToPersistent, connectionOfPersistent
from zope.keyreference.interfaces import IKeyReference
from persistent.interfaces import IPersistent
from ZODB.interfaces import IConnection

from quotationtool.categorization.weighteditemscontainer import updateWeightedItemsContainerOrder
from quotationtool.categorization.categorizableitemdescription import categorizableItemDescriptionVocabulary
from quotationtool.categorization.mode import modeVocabulary
from quotationtool.categorization.categorizableitemdescription import CategorizableItemDescriptions
from quotationtool.categorization.interfaces import ICategorizableItemDescriptions
from quotationtool.categorization.categoriescontainer import CategoriesContainer
from quotationtool.categorization.interfaces import ICategoriesContainer


def setUp(test):
    test.globs = {'root': placefulSetUp(True)}
    zope.component.eventtesting.setUp(test)
    zope.component.provideHandler(updateWeightedItemsContainerOrder)
    vocabulary.setVocabularyRegistry(vocabulary.VocabularyRegistry())
    vr = vocabulary.getVocabularyRegistry()
    vr.register('quotationtool.categorization.categorizableitemdescription',
                categorizableItemDescriptionVocabulary)
    vr.register('quotationtool.categorization.mode',
                modeVocabulary)
    vr.register('Interfaces',
                InterfacesVocabulary)

    root = test.globs['root']
    sm = root.getSiteManager()

    root['categorizableitems'] = categorizable_items = CategorizableItemDescriptions()
    sm.registerUtility(categorizable_items,
                       ICategorizableItemDescriptions)

##     root['categories'] = categories = CategoriesContainer()
##     sm.registerUtility(categories,
##                        ICategoriesContainer)
                       

def tearDown(test):
    zope.component.testing.tearDown(test)


import categoriescontainer, categoryset, category
import categorizableitemdescription
import attribution

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(categorizableitemdescription,
                             setUp = setUp,
                             tearDown = tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                             ),
        doctest.DocTestSuite(categoriescontainer,
                             setUp = setUp,
                             tearDown = tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                             ),
        doctest.DocTestSuite(categoryset,
                             setUp = setUp,
                             tearDown = tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                             ),
        doctest.DocTestSuite(category,
                             setUp = setUp,
                             tearDown = tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                             ),
        doctest.DocTestSuite(attribution,
                             setUp = setUp,
                             tearDown = tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                             ),
        ))
