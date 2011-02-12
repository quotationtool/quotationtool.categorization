import zope.interface
import zope.component
from z3c.formui import form
from z3c.form import field
from zope.i18nmessageid import MessageFactory
from zope.exceptions.interfaces import DuplicationError, UserError
from zope.traversing.browser import absoluteURL
from z3c.pagelet.browser import BrowserPagelet
from zope.publisher.browser import BrowserView
from zope.securitypolicy.interfaces import IPrincipalRoleManager


_ = ReferatoryMessageFactory = MessageFactory('quotationtool')

from quotationtool.categorization import interfaces
from quotationtool.categorization.categorizableitemdescription import CategorizableItemDescription


class LabelView(BrowserView):

    def __call__(self):
        return _('categorizableitemdescriptions-label', u"Categorizable items")


class CategorizableItemDescriptionsContainerView(BrowserPagelet):
    """A view that shows the contents of the
    CategorizableItemDescrriptions container."""


class AddCategorizableItemDescription(form.AddForm):
    """Add a CategorizableItemDescription.


        >>> from z3c.form.testing import setupFormDefaults, TestRequest
        >>> setupFormDefaults()
        >>> request = TestRequest()
        >>> from quotationtool.categorization.browser.categorizableitemdescription \
                import AddCategorizableItemDescription
        >>> form = AddCategorizableItemDescription(root, request)
        >>> form.update()

        >>> form.widgets.keys()
        ['interface', 'label']

    """

    label = _('categorizableitemdescription-add-label',
              u"Add a Item Class for Categorization")

    fields = field.Fields(
        interfaces.ICategorizableItemDescription).omit(
        '__name__', '__parent__')

    def create(self, data):
        description = CategorizableItemDescription()
        form.applyChanges(self, description, data)

        # Grant the current user the Edit permission by assigning him
        # the quotationtool.Creator role, but only locally in the
        # context of the newly created object.
        manager = IPrincipalRoleManager(description)
        manager.assignRoleToPrincipal(
            'quotationtool.Creator',
            self.request.principal.id)

        return description

    def add(self, obj):
        name = obj.interface.__module__ + '.' + obj.interface.__name__
        try:
            self.context[name] = obj
        except DuplicationError:
            raise UserError(
                _('categorizableitemdescrption-add-duplication-error',
                  u"Interface already defined."))

    def nextURL(self):
        return absoluteURL(self.context, self.request)


class EditCategorizableItemDescription(form.EditForm):
    """Edit a CategorizableItemDescription."""

    label = _('categorizabelitemdescription-edit-label',
              u"Edit Description of Categorizable Item Class")

    fields = field.Fields(
        interfaces.ICategorizableItemDescription).omit(
        '__name__', '__parent__')


class RemoveCategorizbaleItemDescription(BrowserView):
    """Remove a CategorizableItemDescription."""

    def __call__(self):
        name = self.request.get['remove']
        del self.context[name]
        self.request.response.redirect(
            absoluteURL(self.context, self.request))

