import zope.interface
import zope.component
from zope.schema.fieldproperty import FieldProperty
from zope.security.management import getInteraction
from zope.exceptions.interfaces import UserError

import interfaces
from interfaces import _
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
    open_to_users = FieldProperty(interfaces.ICategorySet['open_to_users'])
    complete = FieldProperty(interfaces.ICategorySet['complete'])

    def __init__(self):
        self._Attribution__attribution = self._new_attribution_treeset()
        super(CategorySet, self).__init__()

    def __setitem__(self, key, value):
        """ See zope.interface.common.mapping.IWriteMapping

        This is restriced depending on the value of the 'complete' and
        'open_to_users' attribute.

        >>> from quotationtool.categorization.categoryset import CategorySet
        >>> from quotationtool.categorization.category import Category
        >>> from quotationtool.categorization import testing
        >>> from zope.security.management import newInteraction
        >>> interaction = newInteraction()
        >>> descriptions = testing.generateCategorizableItemDescriptions(root)
        >>> container = testing.generateCategoriesContainer(root)
        
        >>> catset = container['catset'] = CategorySet()
        >>> catset['cat1'] = Category()
        >>> catset.complete = True
        >>> catset['cat2'] = Category()
        Traceback (most recent call last):
        ...
        UserError: categoryset-setitem-error-complete

        >>> catset.complete = False
        >>> catset.open_to_users = False
        >>> catset['cat2'] = Category()

        """
        if self.complete:
            raise UserError(_('categoryset-setitem-error-complete',
                              u"The set of category labels is 'complete'. New category labels cannot be added. Sorry."))
        if not self.open_to_users:
            interaction = getInteraction()
            if not interaction.checkPermission('quotationtool.categorization.EditCategory', self):
                raise UserError(_('categoryset-setitem-error-notopentousers',
                                  u"This set of category labels is not 'open to users'. You don't have the permission to add a new category label. Sorry."))
        super(CategorySet, self).__setitem__(key, value)
                            

    #BBB
    inherit = FieldProperty(interfaces.ICategorySet['inherit'])
