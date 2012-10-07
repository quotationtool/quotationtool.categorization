import zope.interface
import zope.component
from z3c.form.browser.checkbox import CheckBoxWidget
from z3c.form.browser.radio import RadioWidget
from z3c.form.interfaces import IFieldWidget, IFormLayer, DISPLAY_MODE
from z3c.form.interfaces import ICheckBoxWidget, IRadioWidget
from z3c.form.widget import FieldWidget
from z3c.form.browser.widget import addFieldClass
from zope.schema.interfaces import ITitledTokenizedTerm
from zope.i18n import translate

from quotationtool.categorization import interfaces
from quotationtool.categorization.interfaces import _


class IExclusiveAttributionWidget(IRadioWidget):
    pass


class INonExclusiveAttributionWidget(ICheckBoxWidget):
    pass


class AttributionWidgetMixin(object):
    
    klass = 'attribution-widget'
    
    def disabled(self):
        if self.mode == DISPLAY_MODE:
            return u"disabled"
        return u""

    def readonly(self):
        if self.mode == DISPLAY_MODE:
            return u"readonly"
        return u""
        
    def updateItems(self):
        """ taken from z3c.form.browser.checkbox (radio), but
        description and query_description added."""
        self.items = []
        for count, term in enumerate(self.terms):
            checked = self.isChecked(term)
            id = '%s-%i' % (self.id, count)
            label = term.token
            if ITitledTokenizedTerm.providedBy(term):
                label = translate(term.title, context=self.request,
                                  default=term.title)
            self.items.append(
                {'id':id, 'name':self.name + ':list', 'value':term.token,
                 'label':label, 'checked':checked,
                 'description': term.value.description,
                 'query_description': term.value.query_description,})


class ExclusiveAttributionWidget(AttributionWidgetMixin, RadioWidget):

    zope.interface.implementsOnly(IExclusiveAttributionWidget)

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(ExclusiveAttributionWidget, self).update()
        addFieldClass(self)
        self.updateItems()


class NonExclusiveAttributionWidget(AttributionWidgetMixin, CheckBoxWidget):

    zope.interface.implementsOnly(INonExclusiveAttributionWidget)

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(NonExclusiveAttributionWidget, self).update()
        addFieldClass(self)
        self.updateItems()


@zope.component.adapter(interfaces.IExclusiveAttributionField, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def ExclusiveAttributionFieldWidget(field, request):
    return FieldWidget(field, ExclusiveAttributionWidget(request))


@zope.component.adapter(interfaces.INonExclusiveAttributionField, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def NonExclusiveAttributionFieldWidget(field, request):
    return FieldWidget(field, NonExclusiveAttributionWidget(request))

