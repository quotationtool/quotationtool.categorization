import zope.interface
import zope.component
from zope.schema.fieldproperty import FieldProperty
from zope.dublincore.interfaces import IWriteZopeDublinCore
from BTrees.OOBTree import OOBTree
from zope.lifecycleevent.interfaces import IObjectAddedEvent, IObjectRemovedEvent, IObjectMovedEvent

from weighteditemscontainer import WeightedItemsContainer
from quotationtool.site.interfaces import INewQuotationtoolSiteEvent

from quotationtool.categorization import interfaces


class CategoriesContainer(WeightedItemsContainer):
    """An implementation of a container to hold all category set. """

    zope.interface.implements(interfaces.ICategoriesContainer)

    __categories = {}

    def __init__(self):
        self.__categories = self._newCategoriesData()
        super(CategoriesContainer, self).__init__()

    def _newCategoriesData(self):
        return self._newContainerData()

    def getCategory(self, name, default=None):
        return self.__categories.get(name, default)

    def addCategory(self, name, category):
        self.__categories[name] = category

    def removeCategory(self, name):
        del self.__categories[name]


@zope.component.adapter(interfaces.ICategory, IObjectAddedEvent)
def addCategorySubscriber(category, event):
    """ Helps to keep CategoriesContainer.__categories up to date.

    Note that a category is written to the container no matter where
    the category is added, whether it is a category set or some other
    container."""
    container = zope.component.getUtility(
        interfaces.ICategoriesContainer, context=category)
    container.addCategory(category.__name__, category)


@zope.component.adapter(interfaces.ICategory, IObjectRemovedEvent)
def removeCategorySubscriber(category, event):
    """ Helps to keep CategoriesContainer.__categories up to date."""
    container = zope.component.getUtility(
        interfaces.ICategoriesContainer, context=category)
    container.removeCategory(category.__name__)


@zope.component.adapter(interfaces.ICategory, IObjectMovedEvent)
def moveCategorySubscriber(category, event):
    if event.newName and event.oldName:
        # otherwise it might be an added or removed event which is
        # derived from moved event
        container = zope.component.getUtility(
            interfaces.ICategoriesContainer, context=category)
        container.removeCategory(event.oldName)
        container.addCategory(event.newName, category)


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
