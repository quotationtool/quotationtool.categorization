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
from zope.location.location import Location

from quotationtool.site.interfaces import INewQuotationtoolSiteEvent

from quotationtool.categorization import interfaces


ATTRIBUTION_KEY = 'quotationtool.categorization.attribution'
ATTRIBUTION_INDEX = 'attribution-set'

def attributionValue(value):
    return int(bool(value))


class AttributionAnnotation(Persistent, Location):
    """ An attribution implemented as a persistent annotation to
    ICategorizable objects.

    """

    zope.interface.implements(interfaces.IAttribution)
    zope.component.adapts(interfaces.ICategorizable)

    __attributions = {}

    attribution_factory = BTrees.family32.OO.TreeSet

    def __init__(self):
        self.__attributions = self.attribution_factory()

    def isAttributed(self, category_name):
        """ see IAttribution"""
        return attributionValue(self.__attributions.has_key(category_name))
        
    def _getAttributions(self):
        return self.__attributions.keys()

    def _setAttributions(self, categories):
        if not isinstance(categories, self.attribution_factory):
            categories = list(categories)
        self.__attributions = self.attribution_factory(categories)
        zope.event.notify(interfaces.AttributionModifiedEvent(self))

    attributions = property(_getAttributions, _setAttributions)

    def unattribute(self, category_name):
        """ See IAttribution."""
        self.__attributions.remove(category_name)
        zope.event.notify(interfaces.AttributionModifiedEvent(self))

    def attribute(self, category_name):
        """ See IAttribution."""
        self.__attributions.insert(category_name)
        zope.event.notify(interfaces.AttributionModifiedEvent(self))

    def clear(self):
        """ See IAttribution"""
        self.__attributions.clear()
        zope.event.notify(interfaces.AttributionModifiedEvent(self))


attribution_annotation_factory = factory(AttributionAnnotation, ATTRIBUTION_KEY)


@zope.component.adapter(interfaces.IAttributionModifiedEvent)
def attributionModifiedDispatcher(event):
    """ Dispatch AttributionModifiedEvent to ObjectModifiedEvent on
    categorizable (attributed) object."""
    zope.event.notify(ObjectModifiedEvent(event.attribution.__parent__))


class AttributionIndexer(ValueIndexer):
    """ Value indexer that indexes attributions of categorizable
    objects."""

    indexName = ATTRIBUTION_INDEX # it is a SetIndex

    zope.component.adapts(interfaces.ICategorizable)

    @property
    def value(self):
        attribution = interfaces.IAttribution(self.context)
        return attribution.attributions


@zope.component.adapter(INewQuotationtoolSiteEvent)
def createAttributionIndex(event):
    sm = event.object.getSiteManager()
    sm['default'][ATTRIBUTION_INDEX] = idx = SetIndex()
    sm.registerUtility(idx, IIndex, name=ATTRIBUTION_INDEX)


@zope.component.adapter(interfaces.ICategorizable, IObjectModifiedEvent)
def indexAttributionSubscriber(obj, event):
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
        attribution.unattribute(category.__name__)


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
            attribution.unattribute(event.oldName)
            attribution.attribute(event.newName)





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

    
