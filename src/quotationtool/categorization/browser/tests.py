import unittest
import doctest
import zope.component
import zope.interface
from zope.component.testing import setUp, tearDown, PlacelessSetup
from zope.app.testing import placelesssetup
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope.configuration.xmlconfig import XMLConfig
from zope.app.component import hooks
import z3c.form.interfaces
import zope.publisher.browser
from zope.security.testing import Principal

from quotationtool.skin.interfaces import IQuotationtoolBrowserLayer

import quotationtool.categorization

from quotationtool.categorization import testing, interfaces
from quotationtool.categorization.browser import datamanager
from quotationtool.categorization.workflow import classifySubscriber


def setUpZCML(test):
    setUp(test)
    XMLConfig('configure.zcml', quotationtool.categorization)()


def setUpDataManager(test):
    tearDownPlaces(test)
    test.globs = {'root': placefulSetUp(True)} # placeful setup
    root = test.globs['root']
    setUpZCML(test)
    hooks.setSite(root)
    testing.generateCategorizableItemDescriptions(root)
    from zope.security.management import newInteraction
    interaction = newInteraction()

def tearDownPlaces(test):
    placefulTearDown()
    from zope.schema.vocabulary import _clear
    _clear()


class TestRequest(zope.publisher.browser.TestRequest):
    # we have to implement the layer interface which the templates and
    # layout are registered for. See the skin.txt file in the
    # zope.publisher.browser module.
    zope.interface.implements(
        z3c.form.interfaces.IFormLayer,
        IQuotationtoolBrowserLayer)

    principal = Principal('testing')


class AttributionTests(placelesssetup.PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(AttributionTests, self).setUp()
        self.root = placefulSetUp(True)
        setUpZCML(self)
        hooks.setSite(self.root)
        # we need a transaction
        from zope.security.management import newInteraction
        interaction = newInteraction()
        testing.generateCategorizableItemDescriptions(self.root)
        testing.generateCategoriesContainer(self.root)
        testing.setUpIntIds(self)
        testing.setUpIndices(self)
        testing.setUpRelationCatalog(self)
        from quotationtool.workflow import testing as workflowtesting
        workflowtesting.setUpWorkLists(self.root)
        workflowtesting.setUpIndices(self)
        from quotationtool.workflow.interfaces import IWorkList
        self.editor_items = zope.component.getUtility(IWorkList, name='editor', context=self.root)
        self.contributor_items = zope.component.getUtility(IWorkList, name='contributor', context=self.root)
        # create item and its intid
        from quotationtool.workflow.interfaces import IHasWorkflowHistory
        zope.interface.classImplements(testing.Categorizable, IHasWorkflowHistory)
        self.root['item'] = item = testing.Categorizable()
        from zope.intid.interfaces import IIntIds
        self.intids = zope.component.getUtility(IIntIds, context=self.root)
        self.intids.register(self.root['item'])
        
    def tearDown(self):
        super(AttributionTests, self).tearDown()
        tearDown(self)
        placefulTearDown()

    def test_IfWorkItemPresent(self):
        # create work item
        classifySubscriber(self.root['item'], None)
        self.assertTrue(len(self.editor_items.values()) == 1)

    def test_DisplayForm(self):
        from quotationtool.categorization.browser import attribution
        #classifySubscriber(self.root['item'], None)
        pagelet = attribution.DisplayForm(self.root['item'], TestRequest())
        pagelet.update()
        self.assertTrue(isinstance(pagelet.render(), unicode))
        self.assertTrue(len(pagelet.widgets.values()) > 0)
        for cat in self.root['categories'].keys():
            self.assertTrue(cat in pagelet.widgets.keys())

    def test_DisplayFormWidgetValue(self):
        from quotationtool.categorization.browser import attribution
        attr = interfaces.IAttribution(self.root['item'])
        attr.set(['cat12'])
        pagelet = attribution.DisplayForm(self.root['item'], TestRequest())
        pagelet.update()
        self.assertTrue(pagelet.widgets['set1'].value == ['cat12'])
        self.assertTrue(u"checked=\"checked\"" in pagelet.render())

    def test_WorkItem(self):
        from quotationtool.categorization.browser import attribution
        classifySubscriber(self.root['item'], None)
        pagelet = attribution.EditorBranchForm(
            self.editor_items.pop(), TestRequest())
        pagelet.update()
        self.assertTrue(isinstance(pagelet.attribution.getCategorizableItem(), testing.Categorizable))
        for cat in self.root['categories'].keys():
            self.assertTrue(cat in pagelet.attribution.widgets.keys())
        self.assertTrue(isinstance(pagelet.render(), unicode))
        
    def test_FinishedEditorItem(self):
        from quotationtool.categorization.browser import attribution
        classifySubscriber(self.root['item'], None)
        request = TestRequest(form={
                'attribution.widgets.set1': u'cat13',
                'attribution.widgets.set2': u'cat23',
                'attribution.widgets.set3': u'cat33',
                'form.widgets.workflow-message': u'OK?',
                'form.buttons.finish': u"Finish"})
        pagelet = attribution.EditorBranchForm(
            self.editor_items.pop(), request)
        pagelet.update()
        self.assertTrue(interfaces.IAttribution(self.root['item']).isAttributed('cat13'))
        self.assertTrue(interfaces.IAttribution(self.root['item']).isAttributed('cat23'))
        self.assertTrue(interfaces.IAttribution(self.root['item']).isAttributed('cat33'))
        self.assertTrue(not interfaces.IAttribution(self.root['item']).isAttributed('cat11'))
        self.assertTrue(len(self.editor_items.values()) == 0)

    def test_PostponedEditorItem(self):
        from quotationtool.categorization.browser import attribution
        classifySubscriber(self.root['item'], None)
        request = TestRequest(form={
                'attribution.widgets.set1': u'cat13',
                'attribution.widgets.set2': u'cat23',
                'attribution.widgets.set3': u'cat33',
                'form.widgets.workflow-message': u'OK?',
                'form.buttons.postpone': u"Postpone"})
        pagelet = attribution.EditorBranchForm(self.editor_items.pop(), request)
        pagelet.update()
        self.assertTrue(len(self.editor_items.values()) == 1)
        next = self.editor_items.pop()
        self.assertTrue(next.object_.isAttributed('cat13'))
        self.assertTrue(next.object_.isAttributed('cat23'))
        self.assertTrue(next.object_.isAttributed('cat33'))
        # but not saved to item:
        self.assertTrue(not interfaces.IAttribution(self.root['item']).isAttributed('cat13'))

    def test_FinishedContributorItem(self):
        from quotationtool.categorization.browser import attribution
        classifySubscriber(self.root['item'], None)
        request = TestRequest(form={
                'attribution.widgets.set1': u'cat13',
                'attribution.widgets.set2': u'cat23',
                'attribution.widgets.set3': u'cat33',
                'form.widgets.workflow-message': u'OK?',
                'form.buttons.finish': u"Finish"})
        pagelet = attribution.ContributorBranchForm(
            self.contributor_items.pop(), request)
        pagelet.update()
        # not saved on database item
        self.assertTrue(not interfaces.IAttribution(self.root['item']).isAttributed('cat13'))
        self.assertTrue(len(self.contributor_items.values()) == 0)
        # but on on workitem
        next = self.editor_items.pop()
        self.assertTrue(next.object_.isAttributed('cat13'))
        
    def test_EditorialReviewItem(self):
        from quotationtool.categorization.browser import attribution
        classifySubscriber(self.root['item'], None)
        cntr = self.contributor_items.pop()
        cntr.finish('finish', u"Done")
        request = TestRequest(form={
                'attribution.widgets.set1': u'cat13',
                'attribution.widgets.set2': u'cat23',
                'attribution.widgets.set3': u'cat33',
                'form.widgets.workflow-message': u'OK',
                'form.buttons.finish': u"Finish"})
        pagelet = attribution.EditorialReviewForm(
            self.editor_items.pop(), request)
        pagelet.update()
        self.assertTrue(pagelet.message() == u"OK")
        # now saved on database item
        self.assertTrue(interfaces.IAttribution(self.root['item']).isAttributed('cat13'))
        self.assertTrue(interfaces.IAttribution(self.root['item']).isAttributed('cat23'))
        self.assertTrue(interfaces.IAttribution(self.root['item']).isAttributed('cat33'))
        self.assertTrue(not interfaces.IAttribution(self.root['item']).isAttributed('cat11'))
        self.assertTrue(len(self.editor_items.values()) == 0)


class SearchTests(placelesssetup.PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(SearchTests, self).setUp()
        self.root = placefulSetUp(True)
        setUpZCML(self)
        import quotationtool.search
        XMLConfig('configure.zcml', quotationtool.search)()
        hooks.setSite(self.root)
        # we need a transaction
        from zope.security.management import newInteraction
        interaction = newInteraction()
        testing.generateCategorizableItemDescriptions(self.root)
        testing.generateCategoriesContainer(self.root)
        testing.setUpIntIds(self)
        testing.setUpIndices(self)
        testing.setUpRelationCatalog(self)
        self.root['item1'] = item1 = testing.Categorizable()
        self.root['item2'] = item2 = testing.Categorizable()
        from zope.intid.interfaces import IIntIds
        self.intids = zope.component.getUtility(IIntIds, context=self.root)
        self.intids.register(self.root['item1'])
        self.intids.register(self.root['item2'])
        attribution1 = interfaces.IAttribution(item1)
        attribution1.set(('cat11', 'cat21', 'cat31',)) 
        attribution2 = interfaces.IAttribution(item2)
        attribution2.set(('cat12', 'cat22', 'cat32',))
        from quotationtool.search.searcher import QuotationtoolSearchFilter
        zope.interface.classImplements(
            QuotationtoolSearchFilter, 
            interfaces.IAttributionSearchFilter)
        
    def tearDown(self):
        super(SearchTests, self).tearDown()
        tearDown(self)
        placefulTearDown()

    def test_RenderSearchForm(self):
        from quotationtool.search.browser.searcher import SearchForm
        pagelet = SearchForm(self.root, TestRequest())
        pagelet.update()
        self.assertTrue(isinstance(pagelet.render(), unicode))
        self.assertTrue('cat12' in pagelet.render())

    def test_Query(self):
        from quotationtool.search.browser.searcher import SearchForm
        request = TestRequest(form={
                'search.button.search': 'search',
                'categorization.0.0.connector': 'AND',
                'categorization.0.0.criterium': 'attribution-set',
                'categorization.0.0.value': 'cat11',
                })
        pagelet = SearchForm(self.root, request)
        #pagelet.update()# TODO: why is there no index?


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SearchTests),
        doctest.DocTestSuite(datamanager,
                             setUp = setUpDataManager,
                             tearDown = tearDownPlaces,
                             optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                             ),
        unittest.makeSuite(AttributionTests),
        ))
