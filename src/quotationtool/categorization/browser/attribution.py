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
from zope.security.management import getInteraction
from zope.wfmc.interfaces import IProcessDefinition
from zope.viewlet.viewlet import ViewletBase
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
import datetime
import zope.event
from zope.lifecycleevent import ObjectModifiedEvent
from zope.exceptions.interfaces import UserError
from zope.location.location import LocationIterator

from quotationtool.skin.interfaces import ITabbedContentLayout
from quotationtool.workflow.interfaces import IWorkItemForm, IWorkflowHistory
from quotationtool.workflow.browser import common
from quotationtool.workflow.history import UserNotation
from quotationtool.workflow.workitem import findWorkItemsForItemAndProcessId

from quotationtool.categorization import interfaces
from quotationtool.categorization.interfaces import _
from quotationtool.categorization.reclassify import ReclassificationContext
from quotationtool.categorization.attribution import PersistentAttribution


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
        attr = interfaces.IAttribution(self.getContent())
        attr.set(categories)


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
    def handleFinish(self, action):
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
    def handleFinish(self, action):
        self._handle('finish')

    @button.buttonAndHandler(_(u"Postpone (Save as draft)"), name="postpone")
    def handlePostpone(self, action):
        self._handle('postpone')

    @button.buttonAndHandler(_(u"Cancel"), name="cancel")
    def handleCancel(self, action):
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        for location in LocationIterator(self.context):
            if zope.component.interfaces.ISite.providedBy(location):
                break
        return absoluteURL(location, self.request) + u"/account/@@worklist.html"


class CategorizationProcessName(BrowserView):
    """ A nice process name for the worklist."""

    def __call__(self):
        return _(u"Classification")


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


class ReAttributionSubForm(AttributionSubForm):
    """ A subform for the ReclassificationForm """

    def getContent(self):
        return self.context            

    def getCategorizableItem(self):
        return self.context


class ReclassificationForm(form.Form):
    """ A reclassification form. Depending on permissions the form
    starts a reclassification workflow (for normal
    quotationtool.Members) or writes the new selections to the context
    item (for quotationtool.Editors)."""

    zope.interface.implements(ITabbedContentLayout)

    fields = field.Fields(comment)

    label = _(u"Reclassify")

    info = _('reclassification-info',
             u"Please select category labels from the form below. Your selections will soon be reviewed by the editors of this website and then show up in the database.")

    info_for_editors = _('reclassification-info-for-editors',
                         u"Please select category labels from the form below.")
    
    ignoreContext = True
    ignoreReadOnly = True
    
    process_started = False

    def checkPermission(self):
        interaction = getInteraction()
        return interaction.checkPermission('quotationtool.workflow.DoEditorialReview', self.context)

    def update(self):
        # assert that there are no other classification processes
        if findWorkItemsForItemAndProcessId(self.context, 'quotationtool.reclassify') or \
                findWorkItemsForItemAndProcessId(self.context, 'quotationtool.classify'):
            raise UserError(_(u"This database item is subject of a classification task already. It must be finished before a new classification process is started."))
        super(ReclassificationForm, self).update()
        self.updateAttributionSubForm()
        if self.checkPermission():
            self.info = self.info_for_editors

    def updateAttributionSubForm(self):
        self.attribution = ReAttributionSubForm(self.context, self.request, self)
        self.attribution.update()

    @button.buttonAndHandler(_(u"Apply"), name='reclassify')
    def handleReclassify(self, action):
        self.updateAttributionSubForm()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        history = IWorkflowHistory(self.context)
        principal = getattr(self.request, 'principal', None)
        if self.checkPermission():
            # store input data to context (attribution.getContent() returns it)
            self.attribution.storeToWorkItem()
        else:
            # store input data to persistent attribution
            pattr = PersistentAttribution()
            attr_data, attr_errors = self.attribution.extractData()
            categories = []
            for catset in attr_data.values():
                for cat in catset:
                    categories.append(cat.__name__)
            pattr.set(categories)
            # start workflow process
            self.process_started = True
            pd = zope.component.getUtility(
                IProcessDefinition, name='quotationtool.reclassify')
            context = ReclassificationContext(removeAllProxies(self.context))
            proc = pd(context)
            proc.start(getattr(principal, 'id', u"Unknown"), 
                       datetime.datetime.now(),
                       data['workflow-message'],
                       removeAllProxies(history),
                       removeAllProxies(pattr))
        # write history
        history.append(UserNotation(
                getattr(principal, 'id', u"Unknown"),
                data['workflow-message']))
        zope.event.notify(ObjectModifiedEvent(self.context))
        # redirect to next url
        self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(_(u"Cancel"), name="cancel")
    def handleCancel(self, action):
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        return absoluteURL(self.context, self.request) + u"/@@attribution.html"


class ReclassificationEditorialReview(WorkItemBaseForm):
    """ The base class works for the items of the
    quotationtool.classify workflow, too."""

    label = EditorBranchForm.label

    info = _('reclassification-review-info', 
             u"The database item below has recently been reclassified. The selections of category labels from the form below need to be reviewed before the show up in the database.")

    @button.buttonAndHandler(_(u"Accept (Save to item)"), name="accept")
    def handleAccept(self, action):
        self._handle('accept')

    @button.buttonAndHandler(_(u"Reject (Keep old selections)"), name="reject")
    def handleReject(self, action):
        self._handle('reject')

    @button.buttonAndHandler(_(u"Postpone (Save as draft)"), name="postpone")
    def handlePostpone(self, action):
        self._handle('postpone')

    @button.buttonAndHandler(_(u"Cancel"), name="cancel")
    def handleCancel(self, action):
        self.request.response.redirect(self.nextURL())


class ReclassificationProcessName(BrowserView):
    """ A nice process name for the worklist."""

    def __call__(self):
        return _(u"Re-Classification")


class ReclassifyItemAction(ViewletBase):

    template = ViewPageTemplateFile('reclassify_action.pt')

    def render(self):
        return self.template()
