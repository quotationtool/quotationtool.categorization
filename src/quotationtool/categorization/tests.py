import unittest
import doctest
import zope.component
from zope.component.testing import setUp, tearDown, PlacelessSetup
from zope.schema import vocabulary
from zope.app.testing import placelesssetup
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope.configuration.xmlconfig import XMLConfig
from zope.site.folder import rootFolder
import zope.event
from zope.lifecycleevent import ObjectModifiedEvent
from zope.app.component import hooks

import quotationtool.categorization
from quotationtool.categorization import testing
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


def setUpFieldConfig(test):
    test.globs = {'root': placefulSetUp(True)} # placeful setup
    root = test.globs['root']
    setUpZCML(test)
    hooks.setSite(root)
    testing.generateCategorizableItemDescriptions(root)



def tearDownFieldConfig(test):
    placefulTearDown()
    tearDown(test)
    from zope.schema.vocabulary import _clear
    _clear()


def setUpRelationCatalog(test):
    import zc.relation
    cat = zc.relation.catalog.Catalog(testing.dump, testing.load)
    zope.component.provideUtility(cat, zc.relation.interfaces.ICatalog)
    def dummy(obj, catalog):
        return getattr(obj, 'ref', None)
    cat.addValueIndex(dummy, testing.dump, testing.load)


def setUpAttributionIndex(test):
    from z3c.indexer.interfaces import IIndex
    from z3c.indexer.index import SetIndex
    zope.component.provideUtility(SetIndex(), IIndex, name='attribution-set')


def setUpRelatedAttributionIndex(test):
    from z3c.indexer.interfaces import IIndex
    from z3c.indexer.index import SetIndex
    zope.component.provideUtility(SetIndex(), IIndex, name='related-attribution-set')


def setUpIntIds(test):
    from zope.intid import IntIds
    from zope.intid.interfaces import IIntIds
    from zope.keyreference.testing import SimpleKeyReference
    zope.component.provideAdapter(SimpleKeyReference)
    zope.component.provideUtility(IntIds(), IIntIds)


def setUpPlay(test):
    setUpZCML(test)
    setUpAttributionIndex(test)
    setUpIntIds(test)


def setUpWorkflowConfig(test):
    setUpZCML(test)
    setUpIntIds(test)
    test.globs['root'] = root = rootFolder()
    setUpIntIds(test)
    setUpAttributionIndex(test)
    setUpRelatedAttributionIndex(test)
    from quotationtool.workflow.testing import setUpIndices as setUpWorkflowIndices
    setUpWorkflowIndices(test)


def setUpRelatedAttribution(test):
    placelesssetup.setUp(test)
    setUpZCML(test)
    test.globs['root'] = root = rootFolder()
    setUpAttributionIndex(test)
    setUpIntIds(test)


def tearDownRelatedAttribution(test):
    placelesssetup.tearDown(test)


class SiteCreationTests(PlacelessSetup, unittest.TestCase):
    """ Test subscribers to INewQuotationtoolSiteEvent. We do that in
    this test where we only setup zcml and a root folder."""

    def setUp(self):
        super(SiteCreationTests, self).setUp()
        setUpZCML(self)
        self.root = rootFolder()

    def tearDown(self):
        tearDown(self)

    def test_CategorizableItemDescriptions(self):
        """ Test if container is created on a new site event."""
        from quotationtool.site.site import QuotationtoolSite
        self.root['quotationtool'] = site = QuotationtoolSite()
        self.assertTrue('categories' in site.keys())
        from quotationtool.categorization.categorizableitemdescription import CategorizableItemDescriptions
        self.assertTrue(isinstance(site['categorizableitems'], CategorizableItemDescriptions))
        from quotationtool.categorization.interfaces import ICategorizableItemDescriptions
        ut = zope.component.getUtility(
            ICategorizableItemDescriptions, 
            context = site)
        self.assertTrue(ut is site['categorizableitems'])

    def test_CategoriesContainer(self):
        """ Test if container is created on a new site event."""
        from quotationtool.site.site import QuotationtoolSite
        self.root['quotationtool'] = site = QuotationtoolSite()
        self.assertTrue('categories' in site.keys())
        from quotationtool.categorization.categoriescontainer import CategoriesContainer
        self.assertTrue(isinstance(site['categories'], CategoriesContainer))
        from quotationtool.categorization.interfaces import ICategoriesContainer
        ut = zope.component.getUtility(ICategoriesContainer, context = site)
        self.assertTrue(ut is site['categories'])

    def test_AttributionIndex(self):
        """ Test if container is created on a new site event."""
        from quotationtool.site.site import QuotationtoolSite
        self.root['quotationtool'] = site = QuotationtoolSite()
        from z3c.indexer.interfaces import IIndex
        idx = zope.component.queryUtility(IIndex, name='attribution-set', context=site)
        self.assertTrue(idx is not None)
        
    def test_RelatedAttributionIndex(self):
        """ Test if container is created on a new site event."""
        from quotationtool.site.site import QuotationtoolSite
        self.root['quotationtool'] = site = QuotationtoolSite()
        from z3c.indexer.interfaces import IIndex
        idx = zope.component.queryUtility(IIndex, name='related-attribution-set', context=site)
        self.assertTrue(idx is not None)
        


class CategoriesContainerTests(PlacelessSetup, unittest.TestCase):
    
    def setUp(self):
        super(CategoriesContainerTests, self).setUp()
        setUpZCML(self)
        self.root = rootFolder()
        testing.generateCategorizableItemDescriptions(self.root)
        testing.generateCategoriesContainer(self.root)
        setUpAttributionIndex(self)
        setUpRelatedAttributionIndex(self)
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


class AttributionTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(AttributionTests, self).setUp()
        setUpZCML(self)
        self.root = rootFolder()
        setUpIntIds(self)
        testing.generateCategorizableItemDescriptions(self.root)
        testing.generateCategoriesContainer(self.root)
        setUpAttributionIndex(self)
        setUpRelatedAttributionIndex(self)
        from quotationtool.categorization.interfaces import ICategoriesContainer
        self.categories = zope.component.getUtility(ICategoriesContainer, context=self.root)
        
    def tearDown(self):
        tearDown(self)

    def test_Attribution(self):
        from quotationtool.categorization.attribution import AttributionAnnotation
        attribution = AttributionAnnotation()
        attribution.set(('a', 'b', 'c', 'a0',))
        self.assertTrue(list(attribution.get()) == ['a', 'a0', 'b', 'c'])
        self.assertTrue(attribution.isAttributed('a0'))
        attribution.clear()
        self.assertTrue(list(attribution.get()) == [])
        attribution.attribute('A')
        self.assertTrue(attribution.isAttributed('A'))
        attribution.unattribute('A')
        self.assertTrue(not attribution.isAttributed('A'))

    def test_AttributionUpToDateWhenCategoryMoved(self):
        """ Test if the attribution is up to date if a category was
        removed."""
        self.root['c'] = catable = Categorizable()
        attribution = interfaces.IAttribution(catable)
        attribution.attribute('cat11')
        from zope.copypastemove.interfaces import IObjectMover
        mover = IObjectMover(self.categories['set1']['cat11'])
        mover.moveTo(self.categories['set2'])
        self.assertTrue(attribution.isAttributed('cat11'))

    def test_AttributionUpToDateWhenCategoryMovedAndRenamed(self):
        """ Test if the attribution is up to date if a category was
        removed."""
        self.root['c'] = catable = Categorizable()
        attribution = interfaces.IAttribution(catable)
        attribution.attribute('cat11')
        zope.event.notify(ObjectModifiedEvent(catable))
        from zope.copypastemove.interfaces import IObjectMover
        mover = IObjectMover(self.categories['set1']['cat11'])
        mover.moveTo(self.categories['set2'], new_name='moved')
        zope.event.notify(ObjectModifiedEvent(catable))
        self.assertTrue(not attribution.isAttributed('cat11'))
        self.assertTrue(attribution.isAttributed('moved'))

    def test_AttributionUpToDateWhenCategoryRemoved(self):
        """ Test if the indexer is up to date if a category was removed."""
        self.root['c'] = catable = Categorizable()
        attribution = interfaces.IAttribution(catable)
        attribution.attribute('cat11')
        zope.event.notify(ObjectModifiedEvent(catable))
        self.assertTrue(attribution.isAttributed('cat11'))
        set1 =  self.categories['set1']
        del set1['cat11']
        zope.event.notify(ObjectModifiedEvent(catable))
        self.assertTrue(not attribution.isAttributed('cat11'))

    def test_IfIndexed(self):
        """ Test if an attribution is indexed at all."""
        self.root['c'] = catable = Categorizable()
        attribution = interfaces.IAttribution(catable)
        attribution.attribute('cat21')
        zope.event.notify(ObjectModifiedEvent(catable))
        from z3c.indexer.query import AnyOf
        from z3c.indexer.search import SearchQuery
        query = SearchQuery(AnyOf('attribution-set', ('cat21',)))
        result = query.apply()
        self.assertTrue(len(result) == 1)
        attribution.unattribute('cat21')
        zope.event.notify(ObjectModifiedEvent(catable))
        query = SearchQuery(AnyOf('attribution-set', ('cat21',)))
        result = query.apply()
        self.assertTrue(len(result) == 0)

    def test_IfUnIndexed(self):
        """ Test if an attribution is indexed at all."""
        self.root['c'] = catable = Categorizable()
        attribution = interfaces.IAttribution(catable)
        attribution.attribute('cat22')
        del self.root['c']
        from z3c.indexer.query import AnyOf
        from z3c.indexer.search import SearchQuery
        query = SearchQuery(AnyOf('attribution-set', ('cat22',)))
        result = query.apply()
        self.assertTrue(len(result) == 0)

    def test_IndexedUpToDateWhenCategoryRemoved(self):
        """ Test if an attribution is indexed at all."""
        self.root['c'] = catable = Categorizable()
        attribution = interfaces.IAttribution(catable)
        attribution.attribute('cat22')
        del self.categories['set2']['cat22']
        from z3c.indexer.query import AnyOf
        from z3c.indexer.search import SearchQuery
        query = SearchQuery(AnyOf('attribution-set', ('cat22',)))
        result = query.apply()
        self.assertTrue(len(result) == 0)

    def test_IndexedUpToDateWhenCategoryMovedAndRenamed(self):
        """ Test if an attribution is indexed at all."""
        self.root['c'] = catable = Categorizable()
        attribution = interfaces.IAttribution(catable)
        attribution.attribute('cat11')
        zope.event.notify(ObjectModifiedEvent(catable))
        from zope.copypastemove.interfaces import IObjectMover
        mover = IObjectMover(self.categories['set1']['cat11'])
        mover.moveTo(self.categories['set2'], new_name='moved')
        zope.event.notify(ObjectModifiedEvent(catable))
        from z3c.indexer.query import AnyOf
        from z3c.indexer.search import SearchQuery
        query = SearchQuery(AnyOf('attribution-set', ('cat22',)))
        result = query.apply()
        self.assertTrue(len(result) == 0)
        query = SearchQuery(AnyOf('attribution-set', ('moved',)))
        result = query.apply()
        self.assertTrue(len(result) == 1)


class CategorizableItemDescriptionTests(placelesssetup.PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(CategorizableItemDescriptionTests, self).setUp()
        self.root = placefulSetUp(True)
        setUpZCML(self)

    def tearDown(self):
        placefulTearDown()
        super(CategorizableItemDescriptionTests, self).tearDown()

    def test_generation(self):
        """ We had some problems with placeful setup so this should be
        tested."""
        testing.generateCategorizableItemDescriptions(self.root)


        
class RelatedAttributionTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(AttributionTests, self).setUp()
        setUpZCML(self)
        self.root = rootFolder()
        setUpIntIds(self)
        testing.generateCategorizableItemDescriptions(self.root)
        testing.generateCategoriesContainer(self.root)
        setUpAttributionIndex(self)
        setUpRelatedAttributionIndex(self)
        setUpRelationCatalog(self)
        from quotationtool.categorization.interfaces import ICategoriesContainer
        self.categories = zope.component.getUtility(ICategoriesContainer, context=self.root)
        
    def tearDown(self):
        tearDown(self)


def test_suite():
    return unittest.TestSuite((
            doctest.DocTestSuite('quotationtool.categorization.field',
                                 setUp = setUpFieldConfig,
                                 tearDown = tearDownFieldConfig,
                                 optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                                 ),
            doctest.DocFileSuite('workflow.txt',
                                 setUp = setUpWorkflowConfig,
                                 tearDown = tearDown,
                                 optionflags = doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                                 ),
            doctest.DocFileSuite('relatedattribution.txt',
                                 setUp = setUpRelatedAttribution,
                                 tearDown = tearDownRelatedAttribution,
                                 optionflags = doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                                 ),
            doctest.DocFileSuite('play.txt',
                                 setUp = setUpPlay,
                                 tearDown = tearDown,
                                 optionflags = doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                                 ),
            unittest.makeSuite(AttributionTests),
            unittest.makeSuite(SiteCreationTests),
            unittest.makeSuite(CategoriesContainerTests),
            unittest.makeSuite(CategorizableItemDescriptionTests),
            #doctest.DocFileSuite('README.txt',
            #                     setUp = setUpWithContext,
            #                     tearDown = tearDownContext,
            #                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            #                     ),
           ))
