from zope.interface import implements
import zope.component
from zope.wfmc.interfaces import ProcessError

from quotationtool.workflow import wp29

from quotationtool.categorization import interfaces
from quotationtool.categorization.interfaces import _


class ClassifikationWorkItem(wp29.SplitBranchWorkItem):
    
    def startHook(self):
        if not interfaces.ICategorizable.providedBy(self.object_):
            raise ProcessError(_('icategorizable-not-provided',
                                 u"Database item can't be classified/categorized. (ICategorizable not provided.)"
                                 ))

    finishHook = startHook


class ContributorClassifikation(ClassifikationWorkItem):

    worklist = 'contributor'


class EditorClassifikation(ClassifikationWorkItem):

    worklist = 'editor'


class TechnicalEditorClassifikation(ClassifikationWorkItem):

    worklist = 'technicaleditor'


class ScriptClassifikation(ClassifikationWorkItem):

    worklist = 'script'
