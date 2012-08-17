import zope.interface
from persistent import Persistent
from zope.container.contained import Contained
from zope.schema.fieldproperty import FieldProperty

import interfaces

#BBB:
from attribution import Attribution


class Category(Persistent, Contained, Attribution):
    """An implementation of a category which stores attributions."""

    zope.interface.implements(interfaces.ICategory,
                              interfaces.IWeightedItem)

    title = FieldProperty(interfaces.ICategory['title'])
    description = FieldProperty(interfaces.ICategory['description'])
    weight = FieldProperty(interfaces.IWeightedItem['weight'])
