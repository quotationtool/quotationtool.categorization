import unittest
import doctest
import zope.component
from zope.component.testing import setUp, tearDown, PlacelessSetup
from zope.schema import vocabulary
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope.configuration.xmlconfig import XMLConfig

import quotationtool.categorization


def setUpZCML(test):
    """
        >>> import quotationtool.categorization
        >>> from zope.configuration.xmlconfig import XMLConfig
        >>> XMLConfig('configure.zcml', quotationtool.categorization)()

    """
    setUp(test)
    XMLConfig('configure.zcml', quotationtool.categorization)()


def setUpWithContext(test):
    from zope.componentvocabulary.vocabulary import InterfacesVocabulary
    from quotationtool.categorization.weighteditemscontainer import updateWeightedItemsContainerOrder
    from quotationtool.categorization.categorizableitemdescription import CategorizableItemDescriptions, categorizableItemDescriptionVocabulary
    from quotationtool.categorization.interfaces import ICategorizableItemDescriptions
    from quotationtool.categorization.mode import modeVocabulary

    test.globs = {'root': placefulSetUp(True)} # placeful setup
    vocabulary.setVocabularyRegistry(vocabulary.VocabularyRegistry())
    vr = vocabulary.getVocabularyRegistry()
    vr.register('quotationtool.categorization.mode',
                modeVocabulary)
    vr.register('quotationtool.categorization.categorizableitemdescription',
                categorizableItemDescriptionVocabulary)
    vr.register('Interfaces',
                InterfacesVocabulary)

    root = test.globs['root']
    root['descriptions'] = CategorizableItemDescriptions()
    sm = root.getSiteManager()
    sm.registerUtility(root['descriptions'],
                       ICategorizableItemDescriptions)
    

def setUpWithContextOFF(test):
    setUpZCML(test)
    # placeful setup
    test.globs = {'root': placefulSetUp(True)}
    root = test.globs['root']
    # create and register an utility for categorizable item descriptions
    from quotationtool.categorization.categorizableitemdescription import CategorizableItemDescriptions
    from quotationtool.categorization.interfaces import ICategorizableItemDescriptions
    descriptions = CategorizableItemDescriptions()
    zope.component.provideUtility(descriptions,
                                  ICategorizableItemDescriptions)

def tearDownContext(test):
    placefulTearDown()
    tearDown(test)

class SiteCreationTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(SiteCreationTests, self).setUp()
        setUpZCML(self)
        import quotationtool.site
        XMLConfig('configure.zcml', quotationtool.site)

    def test_CategoriesContainer(self):
        """ Test if container is created on a new site event."""
        from quotationtool.site.site import QuotationtoolSite
        from zope.container.btree import BTreeContainer
        root = BTreeContainer()
        root['quotationtool'] = site = QuotationtoolSite()
        self.assertTrue('categories' in site.keys())
        from quotationtool.categorization.categoriescontainer import CategoriesContainer
        self.assertTrue(isinstance(site['categories'], CategoriesContainer))
        from quotationtool.categorization.interfaces import ICategoriesContainer
        ut = zope.component.getUtility(
            ICategoriesContainer, 
            context = site)
        self.assertTrue(ut is site['categories'])

    def test_CategorizableItemDescriptions(self):
        """ Test if container is created on a new site event."""
        from quotationtool.site.site import QuotationtoolSite
        from zope.container.btree import BTreeContainer
        root = BTreeContainer()
        root['quotationtool'] = site = QuotationtoolSite()
        self.assertTrue('categories' in site.keys())
        from quotationtool.categorization.categorizableitemdescription import CategorizableItemDescriptions
        self.assertTrue(isinstance(site['categorizableitems'], CategorizableItemDescriptions))
        from quotationtool.categorization.interfaces import ICategorizableItemDescriptions
        ut = zope.component.getUtility(
            ICategorizableItemDescriptions, 
            context = site)
        self.assertTrue(ut is site['categorizableitems'])


def test_suite():
    return unittest.TestSuite((
            doctest.DocTestSuite(setUp = setUp, tearDown = tearDown),
            doctest.DocTestSuite('quotationtool.categorization.datamanager',
                                 setUp = setUpWithContext,
                                 tearDown = tearDownContext,
                                 optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                                 ),
            doctest.DocTestSuite('quotationtool.categorization.field',
                                 setUp = setUpWithContext,
                                 tearDown = tearDownContext,
                                 optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                                 ),
            doctest.DocFileSuite('README.txt',
                                 setUp = setUpWithContext,
                                 tearDown = tearDownContext,
                                 optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                                 ),
            unittest.makeSuite(SiteCreationTests),
            ))
