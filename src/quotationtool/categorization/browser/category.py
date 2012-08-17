import zope.component
from z3c.formui import form
from z3c.form import field, validator
from z3c.form.form import DisplayForm as DisplayFormView
from zope.traversing.browser import absoluteURL
from zope.i18nmessageid import MessageFactory
from zope.publisher.browser import BrowserView
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from z3c.pagelet.browser import BrowserPagelet

from quotationtool.skin.interfaces import ITabbedContentLayout
from quotationtool.skin.interfaces import IQuotationtoolBrowserLayer

from quotationtool.categorization.category import Category
from quotationtool.categorization import interfaces


_ = MessageFactory('quotationtool')


class DetailsView(DisplayFormView):

    fields = field.Fields(interfaces.ICategory).omit(
        '__parent__') + \
        field.Fields(interfaces.IWeightedItem)

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
    """

    zope.interface.implements(ITabbedContentLayout)

    label = _('category-add-label',
              u"Add a new Category Label")

    info = _('category-add-info',
             u"Note: If you don't provide an ID, the title will be used as ID.")

    fields = field.Fields(interfaces.ICategory).omit(
        '__parent__') + \
        field.Fields(interfaces.IWeightedItem)

    def update(self):
        super(AddCategory, self).update()
        self.widgets['__name__'].required = False

    def create(self, data):
        if data['__name__']:
            self.category_name = data['__name__']
        else:
            self.category_name = data['title']
        #interfaces.checkCategoryName(self.category_name, context=self.context)
        category = Category()
        del data['__name__']
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
        self.context[self.category_name] = category

    def nextURL(self):
        return absoluteURL(self.context, self.request)

    @property
    def action(self):
        """See interfaces.IInputForm"""
        return self.request.getURL() + u"#tabs"


class CategoryNameValidator(validator.SimpleFieldValidator):
    
    def validate(self, value):
        if value == self.field.missing_value:
            value = self.view.widgets['title'].extract()
        return interfaces.checkCategoryName(value, context=self.context)


validator.WidgetValidatorDiscriminators(
    CategoryNameValidator,
    field=interfaces.ICategory['__name__'],
    request=IQuotationtoolBrowserLayer,
    )


class EditCategory(form.EditForm):
    """Edit a category object.
    """

    zope.interface.implements(ITabbedContentLayout)

    label = _('category-edit-label',
              u"Edit Category")

    info = _('category-edit-info',
             u"Note: Please use the 'move' action for changing the ID.")

    fields = field.Fields(interfaces.ICategory).omit(
        '__name__', '__parent__') + \
        field.Fields(interfaces.IWeightedItem)


class CategoriesPagelet(BrowserPagelet):
    """ Show the other categories of the set.
    """

    zope.interface.implements(ITabbedContentLayout)

    def categories(self):
        return self.context.__parent__.values()
        
