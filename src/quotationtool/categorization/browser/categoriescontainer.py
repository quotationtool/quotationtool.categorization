import zope.component
from z3c.pagelet.browser import BrowserPagelet
from zope.schema.interfaces import IVocabularyFactory
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from quotationtool.categorization import interfaces


class CategoriesContainerContainerView(BrowserPagelet):
    """A view that displays all objects contained in a
    CategoriesContainer."""

    def __init__(self, context, request):
        self.item_vocabulary = zope.component.getUtility(
            IVocabularyFactory,
            context = context,
            name = 'quotationtool.categorization.categorizableitemdescription')(context)
        super(CategoriesContainerContainerView, self).__init__(context, request)

    def getItemTitle(self, terms):
        for term in terms:
            yield self.item_vocabulary.getTerm(term).title
    
