import zope.interface
from persistent import Persistent
from zope.container.contained import Contained
from zope.schema.fieldproperty import FieldProperty

import interfaces
from attribution import Attribution


class Category(Persistent, Contained, Attribution):
    """An implementation of a category which stores attributions."""

    zope.interface.implements(interfaces.ICategory)

    title = FieldProperty(interfaces.ICategory['title'])
    description = FieldProperty(interfaces.ICategory['description'])
    weight = FieldProperty(interfaces.ICategory['weight'])

    def __init__(self):
        self._Attribution__attribution = self._new_attribution_treeset()
        super(Category, self).__init__()
