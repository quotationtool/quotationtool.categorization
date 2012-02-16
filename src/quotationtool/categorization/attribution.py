import zope.interface
import zope.component
import BTrees
from zope.annotation import factory
from persistent import Persistent
import BTrees.OOBTree
from z3c.indexer.interfaces import IIndex, IIndexer
from z3c.indexer.index import SetIndex
from z3c.indexer.indexer import ValueIndexer
from z3c.indexer.query import AnyOf
from z3c.indexer.search import SearchQuery
from zope.lifecycleevent.interfaces import IObjectMovedEvent, IObjectModifiedEvent
from zope.intid.interfaces import IIntIdRemovedEvent, IIntIds
from zope.lifecycleevent import ObjectModifiedEvent
import zope.event

from quotationtool.site.interfaces import INewQuotationtoolSiteEvent

from quotationtool.categorization import interfaces


ATTRIBUTION_KEY = 'quotationtool.categorization.attribution'
ATTRIBUTION_INDEX = 'attribution-set'

def attributionValue(value):
    return int(bool(value))


class AttributionAnnotation(Persistent):
    """ An attribution implemented as a persistent annotation to
    ICategorizable objects.

    """

    zope.interface.implements(interfaces.IAttribution)
    zope.component.adapts(interfaces.ICategorizable)

    __name__ = __parent__ = None

    __attributions = {}

    def __init__(self):
        self.__attributions = self._newAttributionData()

    def _newAttributionData(self):
        return BTrees.family32.OO.TreeSet()

    def isAttributed(self, category_name):
        """ see IQueryAttribution"""
        return attributionValue(self.__attributions.has_key(category_name))
        
    @property
    def attributions(self):
        """ See IQueryAttribution"""
        return self.__attributions.keys()

    def attribute(self, **kwargs):
        """ See IDoAttribution"""
        # TODO: reset all?
        for name, value in kwargs.items():
            if attributionValue(value):
                if not self.__attributions.has_key(name):
                    self.__attributions.insert(name)
            else:
                if self.__attributions.has_key(name):
                    self.__attributions.remove(name)
        zope.event.notify(ObjectModifiedEvent(self))

    def clear(self):
        """ See IDoAttribution"""
        self.__attributions.clear()


attribution_factory = factory(AttributionAnnotation, ATTRIBUTION_KEY)


class AttributionIndexer(ValueIndexer):
    """ Value indexer that indexes attributions of categorizable
    objects."""

    indexName = ATTRIBUTION_INDEX # it is a SetIndex

    zope.component.adapts(interfaces.ICategorizable)

    @property
    def value(self):
        attribution = interfaces.IAttribution(self.context)
        return attribution.attributes


@zope.component.adapter(INewQuotationtoolSiteEvent)
def createAttributionIndex(event):
    sm = event.object.getSiteManager()
    sm['default'][ATTRIBUTION_INDEX] = idx = SetIndex()
    sm.registerUtility(idx, IIndex, name=ATTRIBUTION_INDEX)


@zope.component.adapter(interfaces.ICategorizable, IObjectModifiedEvent)
def indexAttributionSubscriber(obj, event):
    #raise Exception(obj.__parent__)
    indexer = zope.component.getAdapter(obj, IIndexer, name=ATTRIBUTION_INDEX)
    indexer.doIndex()


@zope.component.adapter(interfaces.ICategory, IIntIdRemovedEvent)
def removeAttributionSubscriber(category, event):
    """ Remove attributions if a category is removed."""
    intids = zope.component.getUtility(IIntIds, context=category)
    container = zope.component.getUtility(interfaces.ICategoriesContainer, context=category)
    query = SearchQuery(AnyOf(ATTRIBUTION_INDEX, (category.__name__,)))
    result = query.apply()
    for intid in result:
        categorizable = intids.getObject(intid)
        attribution = interfaces.IAttribution(categorizable)
        d = {}
        for cat in attribution.attributions:
            if cat != category.__name__:
                d[cat] = 1
        attribution.clear()
        attribution.attribute(**d)


@zope.component.adapter(interfaces.ICategory, IObjectMovedEvent)
def moveAttributionSubscriber(category, event):
    """ Keep an attribution up to date if a category is renamed."""
    if event.oldName and event.newName:
        intids = zope.component.getUtility(IIntIds, context=category)
        container = zope.component.getUtility(interfaces.ICategoriesContainer, context=category)
        query = SearchQuery(AnyOf(ATTRIBUTION_INDEX, (event.oldName,)))
        result = query.apply()
        for intid in result:
            categorizable = intids.getObject(intid)
            attribution = interfaces.IAttribution(categorizable)
            d = {event.newName: 1}
            for cat in attribution.attributions:
                if cat != event.newName:
                    d[cat] = 1
            attribution.clear()
            attribution.attribute(**d)





#BBB: will be removed
class Attribution(object):
    """A mixin class which implements the attribution-api relevant
    interfaces."""

    zope.interface.implements(interfaces.IAttributionInjection,
                              interfaces.IAttributionQuery,
                              interfaces.IAttributionTreeSet)


    def _new_attribution_treeset(self):
        """Create a new treeset for attributions."""
        #return BTrees.family32.II.TreeSet()
        return BTrees.family32.IF.BTree()

    def __init__(self):
        self.__attribution = self._new_attribution_treeset()

    def getAttribution(self):
        return self.__attribution
    # See IAttributionTreeSet:
    attribution = property(getAttribution)

    def attribute_doc(self, docid, doc):
        """See IAttributionInjection."""
        #self.__attribution.insert(docid)
        self.__attribution.insert(docid, 1)

    def unattribute_doc(self, docid):
        """See IAttributionInjection."""
        # TODO: Should we test has_key before trying to remove?
        #self.__attribution.remove(docid)
        self.__attribution.__delitem__(docid)

    def clearAttribution(self):
        """See IAttributionInjection."""
        self.__attribution.clear()

    def isAttributed(self, docid):
        """See IAttributionQuery."""
        return bool(self.__attribution.has_key(docid))

    
