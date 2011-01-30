import zope.interface
import zope.component
from z3c.form.browser.checkbox import CheckBoxWidget
from z3c.form.browser.radio import RadioWidget
from z3c.form.interfaces import IFieldWidget, IFormLayer, DISPLAY_MODE
from z3c.form.interfaces import ICheckBoxWidget, IRadioWidget
from z3c.form.widget import FieldWidget


from quotationtool.categorization import interfaces


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
        

class ExclusiveAttributionWidget(AttributionWidgetMixin, RadioWidget):

    zope.interface.implementsOnly(IExclusiveAttributionWidget)



class NonExclusiveAttributionWidget(AttributionWidgetMixin, CheckBoxWidget):

    zope.interface.implementsOnly(INonExclusiveAttributionWidget)


@zope.component.adapter(interfaces.IExclusiveAttributionField, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def ExclusiveAttributionFieldWidget(field, request):
    return FieldWidget(field, ExclusiveAttributionWidget(request))


@zope.component.adapter(interfaces.INonExclusiveAttributionField, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def NonExclusiveAttributionFieldWidget(field, request):
    return FieldWidget(field, NonExclusiveAttributionWidget(request))

