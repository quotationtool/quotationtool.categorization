import zope.interface
import zope.component
from zope.container.btree import BTreeContainer
from zope.schema.fieldproperty import FieldProperty
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

import interfaces


class WeightedItemsContainer(BTreeContainer):
    """A container the keys, values and items methods of which return
    sorted lists."""

    zope.interface.implements(interfaces.IWeightedItemsContainer)

    items_weight_attribute = FieldProperty(
        interfaces.IWeightedItemsContainer['items_weight_attribute'])

    __order__ = []

    def __update_order__(self):
        self.__order__ = sorted(
            [key for key in super(WeightedItemsContainer, self).keys()],
            cmp = lambda x,y: cmp(getattr(self.__getitem__(x),
                                          self.items_weight_attribute),
                                  getattr(self.__getitem__(y),
                                          self.items_weight_attribute)))

    def __setitem__(self, key, value):
        super(WeightedItemsContainer, self).__setitem__(key, value)
        self.__update_order__()

    def __delitem__(self, key):
        super(WeightedItemsContainer, self).__delitem__(key)
        self.__update_order__()

    def values(self):
        return [self.__getitem__(key) for key in self.__order__]

    def keys(self):
        return self.__order__

    def items(self):
        return [(key, self.__getitem__(key)) for key in self.__order__]
    


@zope.component.adapter(interfaces.IWeightedItem, IObjectModifiedEvent)
def updateWeightedItemsContainerOrder(category, event):
    if interfaces.IWeightedItemsContainer.providedBy(category.__parent__):
        category.__parent__.__update_order__()

