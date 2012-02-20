import zope.component
import zope.interface
from z3c.indexer.interfaces import IIndexer, IIndex
from z3c.indexer.indexer import ValueIndexer
from z3c.indexer.index import SetIndex
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

    @property
    def value(self):
        _useless = interfaces.IAttribution(self.context)
        attribution = _useless.attribution_factory()
        intids = zope.component.getUtility(IIntIds, context=self.context)
        context_id = intids.getId(self.context)
        category_sets = zope.component.queryUtility(
            interfaces.ICategoriesContainer, context=self.context)
        if category_sets is None: return []
        for catalog in zope.component.getAllUtilitiesRegisteredFor(
            zc.relation.interfaces.ICatalog, context=self.context):
            for info in catalog.iterValueIndexInfo():
                for obj in catalog.findValues(info['name'], {zc.relation.RELATION: context_id}):
                    relattr = interfaces.IAttribution(obj).attributions
                    for category_set in category_sets.values():
                        provided = False
                        for iface in category_set.categorizable_items:
                            if iface.providedBy(self.context):
                                provided = True
                        if info['name'] in category_set.relation_indices and provided:
                            categories = _useless.attribution_factory(category_set.keys())
                            relattr = _useless.attribution_factory(relattr)
                            attr = self.intersection(relattr, categories)
                            attribution = self.union(attribution, attr)
        return list(attribution)


@zope.component.adapter(interfaces.ICategorizable, IIntIdAddedEvent)
def indexWhenRelatedCreated(obj, event):
    """ Index an new object that inherits an attribution from another
    object. Makes use of the IntrinsicRelationIndexer."""
    indexer = zope.component.getAdapter(
        obj, IIndexer, name='intrinsic-relation-attribution-set')
    indexer.doIndex()


@zope.component.adapter(interfaces.ICategorizable, IIntIdRemovedEvent)
def unindexWhenRelatedRemoved(obj, event):
    """ Unindex an object that inherits an attribution from another
    object. Makes use of the IntrinsicRelationIndexer."""
    indexer = zope.component.getAdapter(
        obj, IIndexer, name='intrinsic-relation-attribution-set')
    indexer.doUnIndex()
