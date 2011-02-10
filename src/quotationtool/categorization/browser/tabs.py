import zope.interface
from z3c.menu.ready2go.item import ContextMenuItem


class IAttributionTab(zope.interface.Interface): pass
class AttributionTab(ContextMenuItem):
    zope.interface.implements(IAttributionTab)
