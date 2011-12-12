import zope.interface
import zope.component
import BTrees
from zope.annotation import factory

import interfaces


ATTRIBUTION_KEY = 'quotationtool.categorization.attribution'

class AttributionAnnotation(BTreeContainer):

    zope.interface.implements(interfaces.IAttribution)
    zope.component.adapts(interface.ICategorizable)

    __name__ = __parent__ = None

    def _ensureCategoryClass(self, klas):
        if not klas.__name__ in self:
            self[klas.__name__] = BTreeContainer()

    def setAttributes(self, klas, categories):
        self._ensureCategoryClass(klas)
        for category in categories:
            self[klas.__name__][category.__name__] = 1
            
    def unsetAttributes(self, klas, categories):
        self._ensureCategoryClass(klas)
        for category in categories:
            self[klas.__name__][category.__name__] = 0

    def resetAttribution(self, klas):
        self._ensureCategoryClass(klas)
        for category in klas.keys():
            self[klas.__name][category] = 0

    def isAttributed(self, klas, category):
        self._ensureCategoryClass(klas)
        if category.__name in self[klas.__name__]:
            return self[klas.__name][category.__name__] == 1
        return False

    def getAttribution(self, klas):
        for name, category in klas.items():
            if self.isAttributed(klas, category):
                yield category
            
    def getAttributions(self):
        ut = zope.component.getUtility(
            interfaces.ICategoriesContainer,
            context=self)
        d = {}
        for name, klas in ut.items():
            d[name] = list(self.getAttribution(klas))
        return d

attribution_factory = factory(AttributionAnnotation, ATTRIBUTION_KEY)


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

    
