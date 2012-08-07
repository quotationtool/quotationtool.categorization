import zope.interface
import zope.component
import zope.schema
from z3c.formui import form
from z3c.form import field, button, subform
from cgi import escape
from zope.traversing.browser import absoluteURL
from zope.proxy import removeAllProxies
from zope.i18n import translate
from zope.publisher.browser import BrowserView

from quotationtool.skin.interfaces import ITabbedContentLayout
from quotationtool.workflow.interfaces import IWorkItemForm
from quotationtool.workflow.browser import common
from quotationtool.workflow.history import UserNotation

from quotationtool.categorization import interfaces
from quotationtool.categorization.interfaces import _


class AttributionFieldsMixin(object):

    def getCategorizableItem(self):
        """ The categorizable item is needed to determine the category
        sets that can be applied."""
        return self.context

    @property
    def fields(self):
        flds = field.Fields()
        categories = zope.component.getUtility(
            interfaces.ICategoriesContainer,
            context = self.getCategorizableItem())
        for category_set in categories.values():
            # only create widget if category vector is applicable to context 
            for iface in category_set.categorizable_items:
                if iface in zope.interface.providedBy(self.getCategorizableItem()):
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

    
class DisplayForm(AttributionFieldsMixin, form.DisplayForm):
    """Show the attributions on a categorizable object.
    """
    
    zope.interface.implements(ITabbedContentLayout)

    label = _('attribution-label',
              u"Categorization")

    ignoreContext = False


class AttributionSubForm(AttributionFieldsMixin, subform.EditSubForm):
    """A subform for attributions to be used for workflow forms. This
    form takes the workitem as context.
    """
    
    prefix = 'attribution'

    def getContent(self):
        return self.context.object_

    def getCategorizableItem(self):
        ctxt = removeAllProxies(self.context)
        return ctxt.participant.activity.process.context.item

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
    required=False,
    )
comment.__name__ = 'workflow-message'


class WorkItemBaseForm(AttributionFieldsMixin, form.Form):

    zope.interface.implements(IWorkItemForm)

    fields = field.Fields(comment)

    label = info = 'NOT DEFINED'
    
    ignoreContext = True
    ignoreReadOnly = True
    
    def update(self):
        super(WorkItemBaseForm, self).update()
        #self.widgets['workflow-message'].ignoreContext = True
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

    def contributor(self):
        return common.getPrincipalTitle(self.context.contributor)

    def message(self):
        message = getattr(self.context, 'message', u"")
        if not message: message = u""
        return escape(message).replace('\n', '<br />')

    def nextURL(self):
        return absoluteURL(self.context.__parent__, self.request)


class EditorBranchForm(WorkItemBaseForm):
    """ For editorial review."""

    label = _('attribution-editorbranch-label',
              u"Categorization Task")

    info = _('attribution-editorbranch-info',
             u"The database item below has been created recently and has not yet been categorized. Please select category labels from the form below.") 

    @button.buttonAndHandler(_(u"Finish (Save to item)"), name="finish")
    def handleApply(self, action):
        self._handle('finish')

    @button.buttonAndHandler(_(u"Postpone (Save as draft)"), name="postpone")
    def handlePostpone(self, action):
        self._handle('postpone')

    @button.buttonAndHandler(_(u"Cancel"), name="cancel")
    def handleCancel(self, action):
        self.request.response.redirect(self.nextURL())


class EditorialReviewForm(EditorBranchForm):
    """ For the editorial review in the split branch."""

    info = _('attribution-editorial-review-info',
             u"The database item below has recently been created and categorized by a user. Please review the selection of category labels in the form below.") 


class ContributorBranchForm(WorkItemBaseForm):
    """ For contributor work item in the split branch."""

    label = EditorBranchForm.label
    info = EditorBranchForm.info

    @button.buttonAndHandler(_(u"Finish"), name="finish")
    def handleApply(self, action):
        self._handle('finish')

    @button.buttonAndHandler(_(u"Postpone (Save as draft)"), name="postpone")
    def handlePostpone(self, action):
        self._handle('postpone')

    @button.buttonAndHandler(_(u"Cancel"), name="cancel")
    def handleCancel(self, action):
        self.request.response.redirect(self.nextURL())


class CategorizationProcessName(BrowserView):
    """ A nice process name for the worklist."""

    def __call__(self):
        return _(u"Categorization")


class ObjectLabel(BrowserView):
    """ A label used in the ObjectLabelColumn of a worklist table."""
    
    def __call__(self):
        ctxt = removeAllProxies(self.context)
        item = ctxt.participant.activity.process.context.item
        label =  zope.component.queryMultiAdapter(
            (item, self.request), name='label')
        if not label:
            return _(u"Unkown")
        try:
            return translate(label(), context=self.request)
        except Exception:
            return label()
