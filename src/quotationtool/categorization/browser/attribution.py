import md5

import zope.interface
import zope.component
from z3c.formui import form
from z3c.form import field, button
from zope.i18nmessageid import MessageFactory

from quotationtool.categorization import interfaces
from quotationtool.skin.interfaces import ITabbedContentLayout

_ = MessageFactory('quotationtool')


class AttributionFieldsMixin(object):

    def fields(self):
        flds = field.Fields()
        categories = zope.component.getUtility(
            interfaces.ICategoriesContainer,
            context = self.context)
        for category_set in categories.values():
            # only create widget if category vector is applicable to context 
            for iface in category_set.categorizable_items:
                if iface in zope.interface.providedBy(self.context):
                    # lookup an adapter depending on mode
                    if category_set.mode == 'exclusive':
                        fld = interfaces.IExclusiveAttributionField(category_set)
                    if category_set.mode == 'non-exclusive':
                        fld = interfaces.INonExclusiveAttributionField(category_set)
                    # passing a field to the fieldmanager requires a
                    # __name__. It has to be a ascii, so we use a hash
                    fld.__name__ = category_set.__name__.encode('ascii','xmlcharrefreplace')
                    flds += field.Fields(fld)
        return flds
    fields = property(fields)

    
class AttributionForm(AttributionFieldsMixin, form.EditForm):
    """An attribution form based on widgets only, no subforms.

    """
    
    zope.interface.implements(ITabbedContentLayout)

    label = _('attribution-edit-label',
              u"Edit Categorization")



class AttributionDisplayForm(AttributionFieldsMixin, form.DisplayForm):
    """Show the attributions on a categorizable object.
    
    """
    
    zope.interface.implements(ITabbedContentLayout)

    label = _('attribution-label',
              u"Categorization")
