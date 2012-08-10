from zope.interface import implements
import zope.component
from zope.wfmc.interfaces import ProcessError, IProcessContext

from quotationtool.workflow.workitem import WorkItemBase
from quotationtool.workflow.interfaces import IStandardParameters

from quotationtool.categorization import interfaces
from quotationtool.categorization.interfaces import _


class EditorialReviewWorkItem(WorkItemBase):

    implements(interfaces.IReclassificationWorkItem,
               IStandardParameters)

    worklist = 'editor'

    contributor = starttime = message = history = object_ = None 

    def start(self, contributor, starttime, message, history, object_):
        self.contributor = contributor
        self.starttime = starttime
        self.message = message
        self.history = history
        self.object_ = object_
        self._appendToWorkList()

    def finish(self, finish, message):
        if not finish in ('postpone', 'accept', 'reject'):
            raise ProcessError(_(u"Error finishing workitem: $finish", 
                                 mapping={'finish': finish}))
        self.message = message
        self._removeFromWorkList()
        self.participant.activity.workItemFinished(self, finish, message, self.history)


class ReclassificationContext(object):

    implements(IProcessContext)

    item = None # the categorizable database item

    def __init__(self, item):
        self.item = item

    def processFinished(self, process, history, object_, finish):
        if finish == 'accept':
            annotation = interfaces.IAttribution(self.item)
            annotation.set(object_.get())
            zope.event.notify(interfaces.AttributionModifiedEvent(self.item))

