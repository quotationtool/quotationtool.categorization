import zope.interface
import zope.component
import BTrees
from zope.annotation import factory
from persistent import Persistent
import BTrees.OOBTree

import interfaces


def attributionValue(value):
    return int(bool(value))


ATTRIBUTION_KEY = 'quotationtool.categorization.attribution'

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

    def clear(self):
        """ See IDoAttribution"""
        self.__attributions.clear()


attribution_factory = factory(AttributionAnnotation, ATTRIBUTION_KEY)





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

    
