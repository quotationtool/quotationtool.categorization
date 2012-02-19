import unittest
import doctest
import zope.component
from zope.component.testing import setUp, tearDown, PlacelessSetup
from zope.schema import vocabulary
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope.configuration.xmlconfig import XMLConfig
from zope.site.folder import rootFolder
import zope.event

import quotationtool.categorization
from quotationtool.categorization import interfaces
from quotationtool.categorization.testing import Categorizable


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


def generateCategoriesContainer(root):
    from quotationtool.categorization.categoriescontainer import CategoriesContainer
    from quotationtool.categorization.interfaces import ICategoriesContainer
    root['categories'] = container = CategoriesContainer()
    zope.component.provideUtility(container, ICategoriesContainer)
    # set up some categories
    from quotationtool.categorization.categoryset import CategorySet
    from quotationtool.categorization.category import Category
    for i in range(3):
        container['set'+str(i+1)] = catset = CategorySet()
        for l in range(3):
            catset['cat'+str(i+1)+str(l+1)] = cat = Category()
    return container


def setUpAttributionIndex(test):
    from z3c.indexer.interfaces import IIndex
    from z3c.indexer.index import SetIndex
    zope.component.provideUtility(SetIndex(), IIndex, name='attribution-set')


def setUpIntIds(test):
    from quotationtool.categorization.testing import DummyIntIds
    from zope.intid.interfaces import IIntIds
    zope.component.provideUtility(DummyIntIds(), IIntIds)
    from testing import addIntIdSubscriber, removeIntIdSubscriber
    zope.component.provideHandler(addIntIdSubscriber)
    zope.component.provideHandler(removeIntIdSubscriber)


def setUpPlay(test):
    setUpZCML(test)
    #generateCategoriesContainer(self.root)
    setUpAttributionIndex(test)
    setUpIntIds(test)



class SiteCreationTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(SiteCreationTests, self).setUp()
        setUpZCML(self)
        import quotationtool.site
        XMLConfig('configure.zcml', quotationtool.site)


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


class CategoriesContainerTests(PlacelessSetup, unittest.TestCase):
    
    def setUp(self):
        super(CategoriesContainerTests, self).setUp()
        setUpZCML(self)
        self.root = rootFolder()
        generateCategoriesContainer(self.root)
        setUpAttributionIndex(self)
        setUpIntIds(self)
        from quotationtool.categorization.interfaces import ICategoriesContainer
        self.categories = zope.component.getUtility(ICategoriesContainer, context=self.root)
        
    def tearDown(self):
        tearDown(self)

    def test_CategoriesUpToDate(self):
        from quotationtool.categorization.category import Category
        self.root[u'cat1'] = cat1 = Category()
        self.assertTrue(self.categories.getCategory(u'cat1') is cat1)
        del self.root[u'cat1']
        self.assertTrue(self.categories.getCategory(u'cat1') == None)

    def test_CategoriesUpToDateWithEvents(self):
        from quotationtool.categorization.category import Category
        cat1 = Category()
        cat1.__name__ = u"cat1"
        from zope.lifecycleevent import ObjectAddedEvent, ObjectRemovedEvent
        zope.event.notify(ObjectAddedEvent(cat1))
        self.assertTrue(self.categories.getCategory(u'cat1') is cat1)
        zope.event.notify(ObjectRemovedEvent(cat1))
        self.assertTrue(self.categories.getCategory(u'cat1') == None)

    def test_CategoryMoved(self):
        from quotationtool.categorization.category import Category
        self.root[u'cat1'] = cat1 = Category()
        self.assertTrue(self.categories.getCategory(u'cat1') is cat1)
        self.root[u'moved1'] = self.root[u'cat1']
        del self.root[u'cat1']
        self.assertTrue(self.categories.getCategory(u'moved1') is cat1)
        self.assertTrue(self.categories.getCategory(u'cat1') == None)        

    def test_CreationOnNewSiteEvent(self):
        """ Test if container is created on a new site event."""
        from quotationtool.site.site import QuotationtoolSite
        self.root['quotationtool'] = site = QuotationtoolSite()
        self.assertTrue('categories' in site.keys())
        from quotationtool.categorization.categoriescontainer import CategoriesContainer
        self.assertTrue(isinstance(site['categories'], CategoriesContainer))
        from quotationtool.categorization.interfaces import ICategoriesContainer
        ut = zope.component.getUtility(ICategoriesContainer, context = site)
        self.assertTrue(ut is site['categories'])


class AttributionTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(AttributionTests, self).setUp()
        setUpZCML(self)
        self.root = rootFolder()
        generateCategoriesContainer(self.root)
        setUpAttributionIndex(self)
        setUpIntIds(self)
        from quotationtool.categorization.interfaces import ICategoriesContainer
        self.categories = zope.component.getUtility(ICategoriesContainer, context=self.root)
        self.root['catable'] = catable = Categorizable()
        attribution = interfaces.IAttribution(catable)
        attribution.attribute(cat11=1, cat12=1)
        
    def tearDown(self):
        tearDown(self)

    def test_Attribution(self):
        from quotationtool.categorization.attribution import AttributionAnnotation
        attribution = AttributionAnnotation()
        attribution.attribute(a=1, b=0, c=4, a0='a')
        self.assertTrue(list(attribution.attributions) == ['a', 'a0', 'c'])
        self.assertTrue(attribution.isAttributed('a0'))
        attribution.clear()
        self.assertTrue(list(attribution.attributions) == [])

    def test_IndexCreationOnNewSiteEvent(self):
        """ Test if container is created on a new site event."""
        from quotationtool.site.site import QuotationtoolSite
        self.root['quotationtool'] = site = QuotationtoolSite()
        from z3c.indexer.interfaces import IIndex
        idx = zope.component.queryUtility(IIndex, name='attribution-set', context=site)
        self.assertTrue(idx is not None)
        
    def test_IfIndexed(self):
        """ Test if an attribution is indexed at all."""
        from z3c.indexer.query import AnyOf
        from z3c.indexer.search import SearchQuery
        attribution = interfaces.IAttribution(self.root['catable'])
        attribution.attribute(cat11=1, cat21=1)
        query = SearchQuery(AnyOf('attribution-set', ('cat11',)))
        result = query.apply()
        self.assertTrue(len(result) == 1)

    def test_IndexUpToDateWhenCategoryMoved(self):
        """ Test if the indexer is up to date if a category was removed."""
        from zope.copypastemove.interfaces import IObjectMover
        mover = IObjectMover(self.categories['set1']['cat11'])
        mover.moveTo(self.categories['set2'])
        attribution = interfaces.IAttribution(self.root['catable'])
        self.assertTrue(attribution.isAttributed('cat11'))

    def test_IndexUpToDateWhenCategoryMovedAndRenamed(self):
        """ Test if the indexer is up to date if a category was removed."""
        from zope.copypastemove.interfaces import IObjectMover
        mover = IObjectMover(self.categories['set1']['cat11'])
        mover.moveTo(self.categories['set2'], new_name='moved')
        attribution = interfaces.IAttribution(self.root['catable'])
        #self.assertTrue(not attribution.isAttributed('cat11'))
        self.assertTrue(attribution.isAttributed('moved'))


class IndexerTests(PlacelessSetup, unittest.TestCase):
        
    def setUp(self):
        super(IndexerTests, self).setUp()
        setUpZCML(self)
        self.root = rootFolder()
        generateCategoriesContainer(self.root)
        setUpAttributionIndex(self)
        setUpIntIds(self)
        from quotationtool.categorization.interfaces import ICategoriesContainer
        self.categories = zope.component.getUtility(ICategoriesContainer, context=self.root)
        self.root['catable'] = catable = Categorizable()
        attribution = interfaces.IAttribution(catable)
        attribution.attribute(cat11=1, cat12=1)
        
    def tearDown(self):
        tearDown(self)

        
        

def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite('play.txt',
                                 setUp = setUpPlay,
                                 tearDown = tearDown,
                                 optionflags = doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                                 ),
            unittest.makeSuite(IndexerTests),
            unittest.makeSuite(SiteCreationTests),
            unittest.makeSuite(CategoriesContainerTests),
            unittest.makeSuite(AttributionTests),
            #doctest.DocTestSuite('quotationtool.categorization.datamanager',
            #                     setUp = setUpWithContext,
            #                     tearDown = tearDownContext,
            #                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            #                     ),
            #doctest.DocTestSuite('quotationtool.categorization.field',
            #                     setUp = setUpWithContext,
            #                     tearDown = tearDownContext,
            #                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            #                     ),
            #doctest.DocFileSuite('README.txt',
            #                     setUp = setUpWithContext,
            #                     tearDown = tearDownContext,
            #                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            #                     ),
           ))
