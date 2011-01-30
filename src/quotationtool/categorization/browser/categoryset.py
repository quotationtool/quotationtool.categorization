import zope.interface
import zope.component
from z3c.formui import form
from z3c.form import field
from zope.traversing.browser import absoluteURL
from zope.exceptions.interfaces import UserError
from z3c.pagelet.browser import BrowserPagelet
from zope.i18nmessageid import MessageFactory
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView

from quotationtool.categorization import interfaces
from quotationtool.categorization.categoryset import CategorySet
from widget import NonExclusiveAttributionFieldWidget, ExclusiveAttributionFieldWidget
from quotationtool.skin.interfaces import ITabbedContentLayout

_ = MessageFactory('quotationtool')
contentMsg = MessageFactory('quotationtool.categorization.content')


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


class CategorySetContainerView(form.DisplayForm):
    """A view that lists the contained objects in a category set."""

    zope.interface.implements(ITabbedContentLayout)

    label = _('categoryset-display-label',
              u"Category Set")

    fields = field.Fields(interfaces.ICategorySet).omit(
        '__name__', '__parent__', 'items_weight_attribute')


class CategorySetAttributions(BrowserPagelet):
    """Show attributions."""

    zope.interface.implements(ITabbedContentLayout)
