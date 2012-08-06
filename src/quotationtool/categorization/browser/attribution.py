import zope.interface
import zope.component
import zope.schema
from z3c.formui import form
from z3c.form import field, button, subform
from cgi import escape
from zope.traversing.browser import absoluteURL

from quotationtool.skin.interfaces import ITabbedContentLayout
from quotationtool.workflow.interfaces import IWorkItemForm
from quotationtool.workflow.browser import common
from quotationtool.workflow.history import UserNotation

from quotationtool.categorization import interfaces
from quotationtool.categorization.interfaces import _


class AttributionFieldsMixin(object):

    def fields(self):
        flds = field.Fields()
        categories = zope.component.getUtility(
            interfaces.ICategoriesContainer,
            context = self.getContent())
        for category_set in categories.values():
            # only create widget if category vector is applicable to context 
            for iface in category_set.categorizable_items:
                if iface in zope.interface.providedBy(self.getContent()):
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

    
class AttributionDisplayForm(AttributionFieldsMixin, form.DisplayForm):
    """Show the attributions on a categorizable object.
    """
    
    zope.interface.implements(ITabbedContentLayout)

    label = _('attribution-label',
              u"Categorization")


class AttributionSubForm(AttributionFieldsMixin, subform.EditSubForm):
    """A subform for attributions to be used for workflow forms. This
    form takes the workitem as context.
    """
    
    prefix = 'attribution'

    label = _('attribution-edit-label',
              u"Edit Categorization")

    def getContent(self):
        # We need the categorizable item to determine the category
        # sets that can be applied.
        return self.context.participant.activity.process.context.item

    def storeToWorkItem(self):
        data, errors = self.extractData()
        categories = []
        for catset in data.values():
            for cat in catset:
                categories.append(cat.__name__)
        self.context.object_.set(categories)


comment = zope.schema.Text(
    title=_('classification-comment-title',
            u"Message"),
    description=_('classification-comment-desc',
                  u"If you want to leave a message about your decisions you can leave it here."),
    required=True,
    )
comment.__name__ = 'workflow-message'


class ClassificationForm(AttributionFieldsMixin, form.Form):

    zope.interface.implements(IWorkItemForm)

    fields = field.Fields(comment)

    label = info = 'TODO'
    
    def update(self):
        super(ClassificationForm, self).update()
        self.updateAttributionSubForm()

    def updateAttributionSubForm(self):
        self.attribution = AttributionSubForm(self.context, self.request, self)
        self.attribution.update()

    def _handle(self, finish_value):
        self.updateAttributionSubForm()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        history = self.context.history
        principal = getattr(self.request, 'principal', None)
        history.append(UserNotation(
                getattr(principal, 'id', u"Unkown"),
                data['workflow-message']))
        self.attribution.storeToWorkItem()
        url = self.nextURL()
        self.context.finish(finish_value, data['workflow-message'])
        self.request.response.redirect(url)

    @button.buttonAndHandler(_(u"Apply"), name="apply")
    def handleApply(self, action):
        self._handle('finish')

    @button.buttonAndHandler(_(u"Postpone"), name="postpone")
    def handlePostpone(self, action):
        self._handle('postpone')

    @button.buttonAndHandler(_(u"Cancel"), name="cancel")
    def handleCancel(self, action):
        self.request.response.redirect(self.nextURL())

    def contributor(self):
        return common.getPrincipalTitle(self.context.contributor)

    def message(self):
        return escape(self.context.message).replace('\n', '<br />')

    def nextURL(self):
        return absoluteURL(self.context.__parent__, self.request)
