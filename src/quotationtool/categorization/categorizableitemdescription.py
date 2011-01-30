import zope.interface
import zope.component
from persistent import Persistent
from zope.schema.fieldproperty import FieldProperty
from zope.container.contained import Contained
from zope.container.btree import BTreeContainer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.app.component import hooks

import interfaces
from quotationtool.site.interfaces import INewQuotationtoolSiteEvent


class CategorizableItemDescription(Persistent, Contained):

    zope.interface.implements(
        interfaces.ICategorizableItemDescription)

    interface = FieldProperty(
        interfaces.ICategorizableItemDescription['interface'])
    label = FieldProperty(
        interfaces.ICategorizableItemDescription['label'])

    
class CategorizableItemDescriptions(BTreeContainer):

    zope.interface.implements(
        interfaces.ICategorizableItemDescriptions)


def categorizableItemDescriptionVocabulary(context):
    utility = zope.component.getUtility(
        interfaces.ICategorizableItemDescriptions,
        context = hooks.getSite())
    terms = [SimpleTerm(
        item.interface,
        token = name,
        title = item.label)
             for name, item in utility.items()]
    return SimpleVocabulary(terms)
zope.interface.alsoProvides(categorizableItemDescriptionVocabulary,
                            IVocabularyFactory)


@zope.component.adapter(INewQuotationtoolSiteEvent)
def createCategorizableItemDescriptionContainer(event):
    """Create a new container when a new site is created."""
    site = event.object
    sm = site.getSiteManager()
    site['categorizableitems'] = descriptions = CategorizableItemDescriptions()

    sm.registerUtility(
        descriptions,
        interfaces.ICategorizableItemDescriptions)
        
