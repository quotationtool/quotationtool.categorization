from zope.interface import implements
import zope.component
from zope.wfmc.interfaces import ProcessError
import zope.event
from persistent import Persistent

from quotationtool.workflow import wp29

from quotationtool.categorization import interfaces
from quotationtool.categorization.interfaces import _


class ClassifikationWorkItem(wp29.SplitBranchWorkItem):
    
    def OFFstartHook(self):
        if not interfaces.ICategorizable.providedBy(self.object_):
            raise ProcessError(_('icategorizable-not-provided',
                                 u"Database item can't be classified/categorized. (ICategorizable not provided.)"
                                 ))

    #finishHook = startHook


class ContributorClassifikation(ClassifikationWorkItem):

    worklist = 'contributor'


class EditorClassifikation(ClassifikationWorkItem):

    worklist = 'editor'


class TechnicalEditorClassifikation(ClassifikationWorkItem):

    worklist = 'technicaleditor'


class ScriptClassifikation(ClassifikationWorkItem):

    worklist = 'script'


class ClassifikationContext(Persistent, wp29.CancellingContext):

    item = None # the categorizable database item

    def __init__(self, item):
        self.item = item

    def finishedHook(self):
        annotation = interfaces.IAttribution(self.item)
        annotation.set(self.object_.get())
        zope.event.notify(interfaces.AttributionModifiedEvent(self.item))
        #raise Exception(self.object_.get())
