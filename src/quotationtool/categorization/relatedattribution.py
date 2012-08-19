import zope.component
import zope.interface
from z3c.indexer.interfaces import IIndexer, IIndex
from z3c.indexer.indexer import ValueIndexer
from z3c.indexer.index import SetIndex
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.intid.interfaces import IIntIds, IIntIdAddedEvent, IIntIdRemovedEvent
import zc.relation
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.app.component.hooks import getSite
import BTrees

from quotationtool.site.interfaces import INewQuotationtoolSiteEvent

from quotationtool.categorization import interfaces


RELATED_ATTRIBUTION_INDEX = 'related-attribution-set' # it is a set index


def RelationIndicesVocabulary(context):
    terms = []
    for catalog in zope.component.getAllUtilitiesRegisteredFor(
        zc.relation.interfaces.ICatalog, context=getSite()):
        for info in catalog.iterValueIndexInfo():
            term = SimpleTerm(info['name'], title=info['name'])
            terms.append(term)
    return SimpleVocabulary(terms)
zope.interface.alsoProvides(RelationIndicesVocabulary, IVocabularyFactory)


class RelatedAttribution(object):
    """ An adapter that finds intrinsically related objects an
    calculated the attribution inherited from these object."""

    zope.interface.implements(interfaces.IRelatedAttribution)
    zope.component.adapts(interfaces.ICategorizable)

    union = BTrees.family32.OO.union
    intersection = BTrees.family32.OO.intersection
    attribution_factory = BTrees.family32.OO.TreeSet

    def __init__(self, context):
        self.context = context

    def getAttribution(self, category_set=interfaces.ALL):
        attribution = self.attribution_factory()
        # get integer id of context object
        intids = zope.component.getUtility(IIntIds, context=self.context)
        context_id = intids.getId(self.context)
        # get categories container utility
        categories_container = zope.component.queryUtility(
            interfaces.ICategoriesContainer, context=self.context)
        if categories_container is None: return []
        # iterate relation catalogs
        for catalog in zope.component.getAllUtilitiesRegisteredFor(
            zc.relation.interfaces.ICatalog, context=self.context):
            # iterate value indices of each relation catalog
            for info in catalog.iterValueIndexInfo():
                # iterate intrinsically related (can only be zero or one) objects
                for obj in catalog.findValues(info['name'], {zc.relation.RELATION: context_id}):
                    if category_set != interfaces.ALL:
                        category_sets = (category_set,)
                    else:
                        category_sets = categories_container.values()
                    # iterate category sets and check if the
                    # attribution of the intrinsically related object
                    # is inherited by the context object
                    relattr = interfaces.IAttribution(obj).get()
                    for category_set in category_sets:
                        provided = False
                        for iface in category_set.categorizable_items:
                            if iface.providedBy(self.context):
                                provided = True
                        if info['name'] in category_set.relation_indices and provided:
                            # calculate attribution
                            categories = self.attribution_factory(category_set.keys())
                            relattr = self.attribution_factory(relattr)
                            attr = self.intersection(relattr, categories)
                            attribution = self.union(attribution, attr)
        return list(attribution)
        

@zope.component.adapter(INewQuotationtoolSiteEvent)
def createRelatedAttributionIndex(event):
    sm = event.object.getSiteManager()
    sm['default'][RELATED_ATTRIBUTION_INDEX] = idx = SetIndex()
    sm.registerUtility(idx, IIndex, name=RELATED_ATTRIBUTION_INDEX)


class IntrinsicRelationIndexer(ValueIndexer):
    """ Finds intrinsic relations of the context object by querying
    the catalog findValues(self.context) and calculates the related
    attribution for the context object.
    """

    indexName = RELATED_ATTRIBUTION_INDEX

    zope.component.adapts(interfaces.ICategorizable)

    union = BTrees.family32.OO.union
    intersection = BTrees.family32.OO.intersection
    attribution_factory = BTrees.family32.OO.TreeSet

    @property
    def value(self):
        attribution = self.attribution_factory()
        intids = zope.component.getUtility(IIntIds, context=self.context)
        context_id = intids.getId(self.context)
        category_sets = zope.component.queryUtility(
            interfaces.ICategoriesContainer, context=self.context)
        if category_sets is None: return []
        for catalog in zope.component.getAllUtilitiesRegisteredFor(
            zc.relation.interfaces.ICatalog, context=self.context):
            for info in catalog.iterValueIndexInfo():
                for obj in catalog.findValues(info['name'], {zc.relation.RELATION: context_id}):
                    relattr = interfaces.IAttribution(obj).get()
                    for category_set in category_sets.values():
                        provided = False
                        for iface in category_set.categorizable_items:
                            if iface.providedBy(self.context):
                                provided = True
                        if info['name'] in category_set.relation_indices and provided:
                            categories = self.attribution_factory(category_set.keys())
                            relattr = self.attribution_factory(relattr)
                            attr = self.intersection(relattr, categories)
                            attribution = self.union(attribution, attr)
        return list(attribution)


@zope.component.adapter(interfaces.ICategorizable, IIntIdAddedEvent)
def indexWhenIntrinsicallyRelatedCreated(obj, event):
    """ Index an new object that inherits an attribution from another
    object. Makes use of the IntrinsicRelationIndexer."""
    indexer = zope.component.getAdapter(
        obj, IIndexer, name='related-attribution-set')
    indexer.doIndex()


@zope.component.adapter(interfaces.ICategorizable, IIntIdRemovedEvent)
def unindexWhenIntrinsicallyRelatedRemoved(obj, event):
    """ Unindex an object that inherits an attribution from another
    object. Makes use of the IntrinsicRelationIndexer."""
    indexer = zope.component.getAdapter(
        obj, IIndexer, name='related-attribution-set')
    indexer.doUnIndex()


@zope.component.adapter(interfaces.ICategorizable, IObjectModifiedEvent)
def reindexWhenIntrinsicallyRelatedModified(obj, event):
    """ Reindex an object that inherits an attribution from another
    object when the object was modified, because maybe it now
    intrinsically relates to another object. Makes use of the
    IntrinsicRelationIndexer."""
    #raise Exception(obj)
    indexer = zope.component.getAdapter(
        obj, IIndexer, name='related-attribution-set')
    indexer.doIndex()


@zope.component.adapter(interfaces.IAttributionModifiedEvent)
def reindexWhenRelatedModified(event):
    """ Reindex all related objects when an attribution was
    modified."""
    obj = event.attribution.__parent__
    intids = zope.component.getUtility(IIntIds, context=obj)
    oid = intids.getId(obj)
    for catalog in zope.component.getAllUtilitiesRegisteredFor(
        zc.relation.interfaces.ICatalog, context=obj):
        for idx in catalog.iterValueIndexInfo():
            for related in catalog.findRelations({idx['name']: oid}):
                indexer = IIndexer(related)
                indexer.doIndex()

# Note: We don't have to index and unindex related objects when an
# object is added or removed, because in quotationtool related objects
# are always created after. NO! TODO!
