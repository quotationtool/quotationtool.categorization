from zope.interface import implements
import zope.component
from zope.wfmc.interfaces import ProcessError, IProcessDefinition
import zope.event
from persistent import Persistent
from zope.security.management import getInteraction
import datetime

from quotationtool.workflow import wp29
from quotationtool.workflow.interfaces import IWorkflowHistory

from quotationtool.categorization import interfaces
from quotationtool.categorization.interfaces import _
from quotationtool.categorization.attribution import PersistentAttribution

class ClassificationWorkItem(wp29.SplitBranchWorkItem):
    
    implements(interfaces.IClassificationWorkItem)

    def OFFstartHook(self):
        if not interfaces.ICategorizable.providedBy(self.object_):
            raise ProcessError(_('icategorizable-not-provided',
                                 u"Database item can't be classified/categorized. (ICategorizable not provided.)"
                                 ))

    #finishHook = startHook


class ContributorClassification(ClassificationWorkItem):

    worklist = 'contributor'


class EditorClassification(ClassificationWorkItem):

    worklist = 'editor'


class TechnicalEditorClassification(ClassificationWorkItem):

    worklist = 'technicaleditor'


class ScriptClassification(ClassificationWorkItem):

    worklist = 'script'


class EditorialReview(wp29.EditorialReview):

    implements(interfaces.IClassificationWorkItem)

    worklist = 'editor'


class ClassificationContext(Persistent, wp29.CancellingContext):

    item = None # the categorizable database item

    def __init__(self, item):
        self.item = item

    def finishedHook(self):
        annotation = interfaces.IAttribution(self.item)
        annotation.set(self.object_.get())
        zope.event.notify(interfaces.AttributionModifiedEvent(self.item))
        #raise Exception(self.object_.get())


def classifySubscriber(item, event):
    """ A subscriber for an object event that fires a
    quotationtool.classify workflow process for this item."""
    pd = zope.component.getUtility(IProcessDefinition,
                                   name='quotationtool.classify')
    context = ClassificationContext(item)
    process = pd(context)
    contributor = u"unkown"
    for principal in getInteraction().participations:
        contributor = principal.id
        break
    history = IWorkflowHistory(item)
    process.start(contributor, 
                  datetime.datetime.now(), 
                  _(u"Newly created items need to be classified."),
                  history,
                  PersistentAttribution())
