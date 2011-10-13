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

from quotationtool.categorization import interfaces
from quotationtool.categorization.categoryset import CategorySet
from widget import NonExclusiveAttributionFieldWidget, ExclusiveAttributionFieldWidget
from quotationtool.skin.interfaces import ITabbedContentLayout

_ = MessageFactory('quotationtool')
contentMsg = MessageFactory('quotationtool.categorization.content')


class DetailsView(BrowserView):

    template = ViewPageTemplateFile('categoryset_details.pt')

    def __call__(self):
        return self.template()


class DetailsViewOFF(DisplayFormView):

    label = _('categoryset-details-label',
              u"Category Set")

    fields = field.Fields(interfaces.ICategorySet).omit(
        '__name__', '__parent__', 'items_weight_attribute')

    def __call__(self):
        self.update()
        return self.render()


class LabelView(BrowserView):
    
    def __call__(self):
        return _('categoryset-label',
                 u"Category Set: $CATEGORYSET",
                 mapping = {'CATEGORYSET': self.context.__name__},
                 )


class AddCategorySet(form.AddForm):
    """Add a new category set to the categories container.

        >>> from z3c.form.testing import setupFormDefaults, TestRequest
        >>> setupFormDefaults()
        >>> request = TestRequest()
        >>> from quotationtool.categorization.browser.categoryset \
                import AddCategorySet
        >>> form = AddCategorySet(root, request)
        >>> form.update()

        >>> form.widgets.keys()
        ['weight', 'title', 'description', 'categorizable_items', 'mode', 'inherit', 'open_to_users', 'complete']
        
        >>> form.prefix
        'form.'

        >>> form.widgets['weight'].name
        'form.widgets.weight'

        >>> form.buttons.keys()
        ['add']

        >>> request = TestRequest(form = {
        ...     'form.widgets.weight': u"3",
        ...     'form.widgets.title': u"Faculty",
        ...     'form.widgets.description': u"The department ...",
        ...     'form.widgets.categorizabel_items': [],
        ...     'form.widgets.mode': u"exclusive",
        ...     'form.widgets.inherit': u"",
        ...     'form.buttons.add': u"Add",
        ...     })

        >>> form = AddCategorySet(root, request)
        >>> form.update() # TODO

    """

    label = _('categoryset-add-label',
              u"Add a new Category Set")
    
    fields = field.Fields(interfaces.ICategorySet).omit(
        '__name__', '__parent__', 'items_weight_attribute')
    fields['categorizable_items'].widgetFactory = NonExclusiveAttributionFieldWidget
    fields['mode'].widgetFactory = ExclusiveAttributionFieldWidget

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
        '__name__', '__parent__', 'items_weight_attribute')
    fields['categorizable_items'].widgetFactory = NonExclusiveAttributionFieldWidget
    fields['mode'].widgetFactory = ExclusiveAttributionFieldWidget


class CategorySetContainerPagelet(BrowserPagelet):
    """A view that lists the contained objects in a category set."""

    zope.interface.implements(ITabbedContentLayout)

    def categories(self):
        return self.context.values()


class CategorySetAttributions(BrowserPagelet):
    """Show attributions."""

    zope.interface.implements(ITabbedContentLayout)
