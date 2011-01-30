import zope.interface
import zope.component
from zope.schema.fieldproperty import FieldProperty
from zope.dublincore.interfaces import IWriteZopeDublinCore

import interfaces
from weighteditemscontainer import WeightedItemsContainer
from quotationtool.site.interfaces import INewQuotationtoolSiteEvent


class CategoriesContainer(WeightedItemsContainer):
    """An implementation of a container to hold all category set."""

    zope.interface.implements(interfaces.ICategoriesContainer)


@zope.component.adapter(INewQuotationtoolSiteEvent)
def createCategoriesContainer(event):
    """Create a new container for categories."""
    site = event.object
    sm = site.getSiteManager()
    site['categories'] = container = CategoriesContainer()
    sm.registerUtility(
        container,
        interfaces.ICategoriesContainer)

    IWriteZopeDublinCore(container).title = u"Categories"
