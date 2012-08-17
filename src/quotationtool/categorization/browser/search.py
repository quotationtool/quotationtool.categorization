import zope.component
import zope.interface
from zope.viewlet.viewlet import ViewletBase
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from quotationtool.categorization import interfaces


class SearchFormExtension(ViewletBase):
    """ Extends the search form."""

    template = ViewPageTemplateFile('search.pt')

    def render(self):
        return self.template()

    def categories(self):
        return zope.component.getUtility(
            interfaces.ICategoriesContainer, 
            context=self.context)
