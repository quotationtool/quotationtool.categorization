import zope.interface
import zope.component
from z3c.formui import form
from z3c.form import field
from z3c.form.form import DisplayForm as DisplayFormView
from zope.traversing.browser import absoluteURL
from zope.exceptions.interfaces import UserError
from z3c.pagelet.browser import BrowserPagelet
from zope.i18nmessageid import MessageFactory
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.browser.radio import RadioFieldWidget

from quotationtool.categorization import interfaces
from quotationtool.categorization.categoryset import CategorySet
from widget import NonExclusiveAttributionFieldWidget, ExclusiveAttributionFieldWidget
from quotationtool.skin.interfaces import ITabbedContentLayout

_ = MessageFactory('quotationtool')


class DetailsView(DisplayFormView):

    fields = field.Fields(interfaces.ICategorySet).omit('inherit', '__parent__') + \
        field.Fields(interfaces.IWeightedItem)

    def __call__(self):
        self.update()
        return self.render()


class LabelView(BrowserView):
    
    def __call__(self):
        return _('categoryset-label',
                 u"Set of Category Labels: $CATEGORYSET",
                 mapping = {'CATEGORYSET': self.context.__name__},
                 )


class AddCategorySet(form.AddForm):
    """Add a new category set to the categories container.
    """

    label = _('categoryset-add-label',
              u"Add a new Category Set")
    
    fields = field.Fields(interfaces.ICategorySet).omit(
        '__name__', '__parent__', 'items_weight_attribute', 'inherit')
    fields['categorizable_items'].widgetFactory = CheckBoxFieldWidget
    fields['mode'].widgetFactory = RadioFieldWidget

    def create(self, data):
        category_set = CategorySet()
        form.applyChanges(self, category_set, data)

        # Grant the current user the Edit permission by assigning him
        # the quotationtool.Creator role, but only locally in the
        # context of the newly created object.
        manager = IPrincipalRoleManager(category_set)
        manager.assignRoleToPrincipal(
            'quotationtool.Creator',
            self.request.principal.id)

        return category_set

    def add(self, category_set):
        name = category_set.title
        if name in self.context:
            raise UserError(_('categoryset-duplication-error',
                              u"Category Set named ${title} already exists!",
                              mapping = {'title': name}))
        self.context[name] = category_set

    def nextURL(self):
        return absoluteURL(self.context, self.request)


class EditCategorySet(form.EditForm):
    """Edit a category set."""

    zope.interface.implements(ITabbedContentLayout)

    label = _('categoryset-edit-label',
              u"Edit Category Set")

    fields = field.Fields(interfaces.ICategorySet).omit(
        '__name__', '__parent__', 'items_weight_attribute', 'inherit')
    fields['categorizable_items'].widgetFactory = CheckBoxFieldWidget
    fields['mode'].widgetFactory = RadioFieldWidget


class CategorySetContainerPagelet(BrowserPagelet):
    """A view that lists the contained objects in a category set."""

    zope.interface.implements(ITabbedContentLayout)

    def categories(self):
        return self.context.values()


class CategorySetAttributions(BrowserPagelet):
    """Show attributions."""

    zope.interface.implements(ITabbedContentLayout)
