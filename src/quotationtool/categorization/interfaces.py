import zope.interface
import zope.schema
import zope.component
from zope.container.interfaces import IContained, IContainer
from zope.container.interfaces import INameChooser
from zope.container.constraints import containers, contains
from zope.app.component.hooks import getSite
from zope.i18nmessageid import MessageFactory
from z3c.searcher.interfaces import ISearchFilter

_ = MessageFactory('quotationtool')


# return attribution in ALL category sets
ALL = 'all'

    
class ICategorizable(zope.interface.Interface):
    """A marker interface for classes that are categorizable."""


class ICategorizableItemDescriptions(IContainer):
    """A container storing descriptions of categorizable items. It
    will be used as a source to make a vocabulary of categorizable
    item types based on ZOPE3 interfaces. Its descriptions of
    interfaces are userfriendly."""

    contains('.ICategorizableItemDescription')


class ICategorizableItemDescription(IContained):
    """A description of a ZOPE3 interface which users can
    understand. The label will be used as title in a vocabulary's term
    instead of the python module name of the interface."""

    containers(ICategorizableItemDescriptions)

    interface = zope.schema.Choice(
        title = _('icategorizableitemdescription-interface-title',
                  u"Interface"),
        description = _('icategorizableitemdescription-interface-desc',
                        u"Choose an ZOPE-Interface from the list."),
        required = True,
        vocabulary = 'Interfaces',
        )

    label = zope.schema.TextLine(
        title = _('icategorizableitemdescription-label-title',
                  u"Label"),
        description = _('icategorrizableitemdescription-label-description',
                        u"Descriptive term for the interface which users can understand."),
        required = True,
        )
    

class IWeightedItemsContainer(IContainer):
    """A container with ordered content."""

    items_weight_attribute = zope.schema.ASCII(
        title = u"Item's weight attribute",
        description = u"Name of the attribute giving the order.",
        required = True,
        default = 'weight',
        )

    def __update_order__():
        """Update the order."""


class IWeightedItem(zope.interface.Interface):
    
    weight = zope.schema.Int(
        title = _('icategory-weight-title',
                  u"Weight"),
        description = _('icategory-weight-desc',
                        u"Give a numerical value to indicate where in the list of categories this one should appear. They will be displayed in ascending order."),
        required = True,
        min = 1,
        default = 1000,
        )


class ICategoriesContainer(IWeightedItemsContainer):
    """A container for all the category things."""

    contains('.ICategorySet')

    def getCategory(name, default=None):
        """ Returns the category with the unique name given by the
        parameter name. Returns default if not present.
        """
    def addCategory(name, category):
        """ Add a category to the containers category index."""

    def removeCategory(name):
        """ Remove the category given by its name from the index.""" 


def checkCategoryName(name, context=getSite()):
    if '\n' in name or '\r' in name:
        raise zope.interface.Invalid(
            _(u"The ID must not contain a newline character (line break)."))
    #taken from namechooser
    if isinstance(name, str):
        name = unicode(name)
    elif not isinstance(name, unicode):
        raise zope.interface.Invalid(_(u"Invalid ID type"))
    #taken from namechooser
    if not name:
        raise zope.interface.Invalid(
            _("An empty ID was provided. IDs must not be empty.")
            )
    #taken from namechooser
    if name[:1] in '+@' or '/' in name:
        raise zope.interface.Invalid(
            _(u"The ID must not begin with '+' or '@' or contain '/'")
            )
    # check if already in use
    container = zope.component.getUtility(
        ICategoriesContainer, context=context)
    if container.getCategory(name):
        raise zope.interface.Invalid(
            _("The given ID is already being used")
            )
    return True


class ICategory(zope.interface.Interface):
    """A category label."""

    containers('.ICategorySet')

    __name__ = zope.schema.TextLine(
        title=_('icategory-name-title', u"ID"),
        description=_('icategory-name-desc', u"Unique identifier of the category label. 'Unique' means unique within the setunion of all category sets."),
        required=False,
        default=None,
        constraint=checkCategoryName,
        )

    title = zope.schema.TextLine(
        title = _('icategory-title-title',
                  u"Title/Label"),
        description = _('icategory-title-desc',
                        u"How should the category be named?"),
        required = True,
        )

    description = zope.schema.Text(
        title = _('icategory-description-title',
                  u"Description"),
        description = _('icategory-description-desc',
                        u"Short description or explanation."),
        required = True,
        )
    
    query_description = zope.schema.Text(
        title = _('icategory-querydescription-title',
                  u"Query Description"),
        description = _('icategory-querydescription-desc',
                        u"Description showing up in the query/attribution form."),
        required = False,
        )
    

class ICategorySet(zope.interface.Interface):#IWeightedItemsContainer, IWeightedItem):
    """A set of related (exclusive/ non-exclusive) categories."""

    containers('.ICategoriesContainer')

    contains(ICategory)

    title = zope.schema.TextLine(
        title = _('icategoryset-title-title',
                  u"Title"),
        description = _('icategoryset-title-desc',
                        u"How should the set of category labels be named?"),
        required = True,
        )

    description = zope.schema.Text(
        title = _('icategoryset-description-title',
                  u"Description"),
        description = _('icategoryset-description-desc',
                        u"Short description or explanation showing up in the classification of an item."),
        required = True,
        )

    query_description = zope.schema.Text(
        title = _('icategoryset-querydescription-title',
                  u"Query Description"),
        description = _('icategoryset-querydescription-desc',
                        u"Description showing up in the classification form."),
        required = False,
        )

    long_description = zope.schema.Text(
        title = _('icategoryset-longdescription-title',
                  u"Long Description"),
        description = _('icategoryset-longdescription-desc',
                        u"Long Description that is not showing in the context of an item at all."),
        required = False,
        )

    categorizable_items = zope.schema.List(
        title = _('icategoryset-usedfor-title',
                  u"Used for"),
        description = _('icategoryset-usedfor-title',
                        u"To which types of items should this set of category labels be applicable?"),
        default = [],
        value_type = zope.schema.Choice(
        title = _('icategoryset-usedfor-choice-title',
                  u"Class"),
        vocabulary = 'quotationtool.categorization.categorizableitemdescription',
        ),
        )

    mode = zope.schema.Choice(
        title = _('icategoryset-mode-title',
                  u"Mode"),
        description = _('icategoryset-mode-desc',
                        u"Choose whether the category labels of this set are mutually exclusive or non-exclusive."),
        vocabulary = 'quotationtool.categorization.mode',
        required = True,
        default = 'non-exclusive',
        )

    relation_indices = zope.schema.List(
        title = _('icategoryset-relationindices-title',
                  u"Relation Indices"),
        description = _('icategoryset-relationindices-desc',
                        u"Choose a relation type to inherit categorization from."),
        value_type = zope.schema.Choice(
        title = _('icategoryset-relationindex-title',
                  u"Index"),
        required = True,
        vocabulary = 'quotationtool.categorization.RelationIndices',
        ),
        required = False,
        default = [],
        )

    open_to_users = zope.schema.Bool(
        title = _('icategoryset-opentousers-title',
                  u"Open"),
        description = _('icategoryset-opentousers-desc',
                        u"Should arbitrary users (not only members of the editorial board) be allowed to add category labels to this set?"),
        required = False,
        default = True,
        )

    complete = zope.schema.Bool(
        title = _('icategoryset-complete-title',
                  u"Complete"),
        description = _('icategoryset-complete-desc',
                        u"Should it be impossible to add new category labels to this set?"),
        required = False,
        default = False,
        )

    #BBB
    inherit = zope.schema.Bool(
        title = _('icategoryset-inherit-title',
                  u"Inherit"),
        description = _('icategoryset-inherit-desc',
                        u"Inherit categorization from related item."),
        required = False,
        default = False,
        )


class ICategoryAddedEvent(zope.component.interfaces.IObjectEvent):
    """Indicates that a new category (= object implementing ICategory)
    has been created."""


class ICategoryRemovedEvent(zope.component.interfaces.IObjectEvent):
    """Indicates that a category was removed."""


class IWriteAttribution(zope.interface.Interface):
    """ DO/Write an attribution on a categorizable item."""

    def attribute(category_name):
        """ Attribute a categorie to categorizable item."""

    def unattribute(category_name):
        """ Unattribute a category from categorizable item."""

    def set(categories):
        """ Set attribution to the given category names."""

    def clear():
        """ Remove all categories from attribution to categorizable
        item."""


class IReadAttribution(zope.interface.Interface):
    """ Query/Read the attribution on a categorizable item."""

    def isAttributed(category_name):
        """ Returns true if and only if category was attributed."""
        
    def get():
        """ Return the attributions."""


class IAttribution(IReadAttribution, IWriteAttribution):
    """ To be provided by an adapter for categorizable item. """


class IRelatedAttribution(zope.interface.Interface):
    """ Get attribution from related items."""

    def getAttribution(category_set=ALL):
        """ Returns the list of attributions."""
    

class IAttributionModifiedEvent(zope.interface.Interface):
    """ Indicates that an attribution was modified."""

    attribution = zope.interface.Attribute("The attribution.")


class AttributionModifiedEvent(object):

    zope.interface.implements(IAttributionModifiedEvent)

    def __init__(self, attribution):
        self.attribution = attribution

    

class IAttributionField(zope.schema.interfaces.IField):
    """A field for attributing a category set."""

    category_set = zope.schema.Object(
        title = u"Category Set",
        description = u"The category set is present on the attribution field.",
        schema = ICategorySet,
        )


class IExclusiveAttributionField(zope.schema.interfaces.IChoice,
                                IAttributionField):
    """A field for attribution of a single category set."""


class INonExclusiveAttributionField(zope.schema.interfaces.IList,
                                   IAttributionField):
    """A field for attribution of a single category set."""

    
    
AttributionKeyField = zope.schema.Choice(
    title = _('iattribution-attribution-keytype-title',
              u"Category Set"),
    description = _('iattribution-attribution-keytype-desc',
                    u"Choose set of categories."),
    vocabulary = 'quotationtool.categorization.categoryset',
    )


AttributionValueField = zope.schema.Tuple(
    title = _('iattribution-attribution-valuetype-title',
              u"Attribution of Category/Categories from set"),
    description = _('iattribution-attribution-valuetype-desc',
                    u"Choose one or more attributions depending on mode."),
    value_type = zope.schema.TextLine(# Choice not possible here.
    title = _('iattribution-attribution-valuetype-tuplevaluetype-title',
              u"Category"),
    description = _('iattribution-attribution-valuetype-tuplevaluetype-desc',
                    u"A single Category."),
    required = True,
    ),
    )


class IClassificationWorkItem(zope.interface.Interface):
    """ A workflow item that asks for a database item to be classified.

    The categorizable object lives on the 'item' attribute of the
    process's context."""


class IReclassificationWorkItem(zope.interface.Interface):
    """ A workflow item used if the data base item was reclassified."""


class IAttributionSearchFilter(ISearchFilter):
    """ A marker interface in order to register attribution related
    search criteria. 

    Note: There is no implementation of a search filter at the
    moment. We only use this interface as a marker, that can be
    implemented by other search filters."""



### BBB: will be removed
class IAttributionInjection(zope.interface.Interface):
    """Injection part of the Attribution-API."""

    def attribute_doc(docid, doc):
        """Attribute category to the document identified by integer
        ID."""

    def unattribute_doc(docid):
        """Revocate attribution of the category from the document
        identified by its ID."""

    def clearAttribution():
        """Forget stored attributions!"""


class IAttributionQuery(zope.interface.Interface):
    """Query part of the Attribution-API."""
    
    def isAttributed(docid):
        """Returns True if category was attributed to document, else
        returns False."""


class IAttributionTreeSet(zope.interface.Interface):
    """Exposes the TreeSet for intersections and set unions."""

    attribution = zope.interface.Attribute(
        """An IITreeSet storing attributions.""")
