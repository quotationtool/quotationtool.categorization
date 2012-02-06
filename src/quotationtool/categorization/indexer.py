from z3c.indexer.interfaces import IIndex
from z3c.indexer.index import SetIndex
from z3c.indexer.indexer import ValueIndexer
import zope.component

from quotationtool.site.interfaces import INewQuotationtoolSiteEvent

from quotationtool.categorization import interfaces


class AttributionIndexer(ValueIndexer):

    indexName = 'attribution-set' # it is a SetIndex

    zope.component.adapts(interfaces.ICategorizable)

    @property
    def value(self):
        attribution = interfaces.IAttribution(self.context)
        return attribution.attributes


@zope.component.adapter(INewQuotationtoolSiteEvent)
def createAttributionIndex(event):
    sm = event.object.getSiteManager()
    sm['default']['attribution-value'] = idx = SetIndex()
    sm.registerUtility(idx, IIndex, name='attribution-set')
