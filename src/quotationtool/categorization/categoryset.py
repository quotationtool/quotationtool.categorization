import zope.interface
import zope.component
from zope.schema.fieldproperty import FieldProperty

import interfaces
from weighteditemscontainer import WeightedItemsContainer
from attribution import Attribution


class CategorySet(WeightedItemsContainer, Attribution):
    """An implementation of a category set which stores attributions."""

    zope.interface.implements(interfaces.ICategorySet)

    title = FieldProperty(interfaces.ICategorySet['title'])
    description = FieldProperty(interfaces.ICategorySet['description'])
    mode = FieldProperty(interfaces.ICategorySet['mode'])
    categorizable_items = FieldProperty(interfaces.ICategorySet['categorizable_items'])
    weight = FieldProperty(interfaces.ICategorySet['weight'])
    relation_indices = FieldProperty(interfaces.ICategorySet['relation_indices'])
    inherit = FieldProperty(interfaces.ICategorySet['inherit'])
    open_to_users = FieldProperty(interfaces.ICategorySet['open_to_users'])
    complete = FieldProperty(interfaces.ICategorySet['complete'])

    def __init__(self):
        self._Attribution__attribution = self._new_attribution_treeset()
        super(CategorySet, self).__init__()
