import zope.component
from z3c.formui import form
from z3c.form import field
from zope.traversing.browser import absoluteURL
from zope.i18nmessageid import MessageFactory
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from quotationtool.categorization.category import Category
from quotationtool.categorization import interfaces
from quotationtool.skin.interfaces import ITabbedContentLayout

_ = MessageFactory('quotationtool')
contentMsg = MessageFactory('quotationtool.categorization.content')


class AddCategory(form.AddForm):
    """Add a new category object to a categoryset container.

        >>> from z3c.form.testing import setupFormDefaults, TestRequest
        >>> setupFormDefaults()
        >>> request = TestRequest()
        >>> from quotationtool.categorization.browser.category \
                import AddCategory
        >>> form = AddCategory(root, request)
        >>> form.update()

        >>> form.widgets.keys()
        ['weight', 'title', 'description']

    """

    zope.interface.implements(ITabbedContentLayout)

    label = _('category-add-label',
              u"Add a new Category")

    fields = field.Fields(interfaces.ICategory).omit(
        '__name__', '__parent__','items_weight_attribute')
    
    def create(self, data):
        category = Category()
        form.applyChanges(self, category, data)
        return category

    def add(self, category):
        name = category.title
        if name in self.context:
           raise UserError(_('addcategory-duplication-error',
                             u"Category named ${title} already exists.",
                             mapping = {'title': name}))
        self.context[name] = category

    def nextURL(self):
        return absoluteURL(self.context, self.request)


class EditCategory(form.EditForm):
    """Edit a category object.



    """

    zope.interface.implements(ITabbedContentLayout)

    label = _('category-edit-label',
              u"Edit Category")

    fields = field.Fields(interfaces.ICategory).omit(
        '__name__', '__parent__','items_weight_attribute')    


class DisplayCategory(form.DisplayForm):
    """Display a category object.



    """

    zope.interface.implements(ITabbedContentLayout)

    label = _('category-display-label',
              u"Category")

    fields = field.Fields(interfaces.ICategory).omit(
        '__name__', '__parent__','items_weight_attribute')
