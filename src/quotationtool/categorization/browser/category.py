import zope.component
from z3c.formui import form
from z3c.form import field
from z3c.form.form import DisplayForm
from zope.traversing.browser import absoluteURL
from zope.i18nmessageid import MessageFactory
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from z3c.pagelet.browser import BrowserPagelet

from quotationtool.categorization.category import Category
from quotationtool.categorization import interfaces
from quotationtool.skin.interfaces import ITabbedContentLayout


_ = MessageFactory('quotationtool')
contentMsg = MessageFactory('quotationtool.categorization.content')


class DetailsView(BrowserView):

    template = ViewPageTemplateFile('category_details.pt')

    def __call__(self):
        return self.template()


class DetailsViewOFF(DisplayForm):
    """Display a category object.
    """

    label = _('category-details-label',
              u"Category")

    fields = field.Fields(interfaces.ICategory).omit(
        '__name__', '__parent__','items_weight_attribute')

    def __call__(self):
        self.update()
        return self.render()


class LabelView(BrowserView):
    """ The label of a category."""
    
    def __call__(self):
        return _('category-label',
                 u"Category Set: $CATEGORYSET --> Category: $CATEGORY",
                 mapping = {'CATEGORYSET': self.context.__parent__.__name__,
                            'CATEGORY': self.context.__name__},
                 )


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

        # Grant the current user the Edit permission by assigning him
        # the quotationtool.Creator role, but only locally in the
        # context of the newly created object.
        manager = IPrincipalRoleManager(category)
        manager.assignRoleToPrincipal(
            'quotationtool.Creator',
            self.request.principal.id)

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


class CategoriesPagelet(BrowserPagelet):
    """ Show the other categories of the set.
    """

    zope.interface.implements(ITabbedContentLayout)

    def categories(self):
        return self.context.__parent__.values()
        
