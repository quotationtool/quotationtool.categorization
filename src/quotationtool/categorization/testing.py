import zope.interface
from persistent import Persistent
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.container.contained import Contained
from zope.app.component import hooks

from quotationtool.categorization.interfaces import ICategorizable
from quotationtool.categorization import interfaces
from quotationtool.categorization.categoryset import CategorySet
from quotationtool.categorization.category import Category
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.location.interfaces import ILocation
from zope.location.interfaces import IContained
import zope.event
from zope.intid.interfaces import IIntIds, IIntIdEvent
from zope.intid.interfaces import IntIdAddedEvent, IntIdRemovedEvent

class ISomeCategorizable(zope.interface.Interface):
    """ """

class Categorizable(Persistent, Contained):
    """ A dummy class that is categorizable."""
    zope.interface.implements(ISomeCategorizable,
                              IAttributeAnnotatable, 
                              ICategorizable)


def createSomeCategorySet():
    faculty = CategorySet()
    faculty.title = u"Faculty"
    faculty.description = u"The department of a university..."
    faculty.mode = 'exclusive'
    faculty.inherit = True
    faculty.weight = 1
    faculty['philosophy'] = philosophy = Category()
    philosophy.title = u"Philosophy"
    philosophy.description = u"What Kant calls the first faculty."
    philosophy.weight = 1
    faculty['jura'] = jura = Category()
    jura.title = u"Law"
    jura.description = u"Where lawers are made."
    jura.weight = 10
    return faculty

def generateCategoriesContainer(root):
    from quotationtool.categorization.categoriescontainer import CategoriesContainer
    from quotationtool.categorization.interfaces import ICategoriesContainer
    root['categories'] = container = CategoriesContainer()
    if zope.component.interfaces.ISite.providedBy(root):
        # we have a placeful set up
        sm = root.getSiteManager()
        sm.registerUtility(container, ICategoriesContainer)
    else:
        zope.component.provideUtility(container, ICategoriesContainer)
    # set up some categories
    from quotationtool.categorization.categoryset import CategorySet
    from quotationtool.categorization.category import Category
    for i in range(3):
        container['set'+str(i+1)] = catset = CategorySet()
        catset.title = u"Category Set " + unicode(i+1)
        catset.description = u"About Category Set " + unicode(i+1)
        catset.categorizable_items = [interfaces.ICategorizable]
        catset.mode = 'non-exclusive'
        catset.relation_indices = []
        catset.open_to_users = False
        catset.complete = False
        catset.inherit = False #BBB
        for l in range(3):
            catset['cat'+str(i+1)+str(l+1)] = cat = Category()
            cat.title = u"Category "+unicode(i+1)+unicode(l+1)
            cat.description = u"About Category "+unicode(i+1)+unicode(l+1)
    return container


def generateCategorizableItemDescriptions(root):
    from quotationtool.categorization.categorizableitemdescription import CategorizableItemDescriptions, CategorizableItemDescription
    from quotationtool.categorization.interfaces import ICategorizableItemDescriptions
    root['categorizableitems'] = descs = CategorizableItemDescriptions()
    if zope.component.interfaces.ISite.providedBy(root):
        # placefull set up
        sm = root.getSiteManager()
        sm.registerUtility(descs, ICategorizableItemDescriptions)
        from zope.interface.interfaces import IInterface
        sm.registerUtility(interfaces.ICategorizable, IInterface, name='ICategorizable')
    else:
        zope.component.provideUtility(descs, ICategorizableItemDescriptions)

    zope.component.interface.provideInterface('ICategorizable', interfaces.ICategorizable)
    # In a placeful setup, this is not enough. We need the interface
    # to be registered as a local utility, god knows why... (see above)

    descs['ICategorizable'] = desc = CategorizableItemDescription()
    desc.interface = interfaces.ICategorizable
    desc.label = u"arbitrary"
    return descs



def setUpRelationCatalog(test):
    import zc.relation
    cat = zc.relation.catalog.Catalog(dump, load)
    def dummy(obj, catalog):
        return getattr(obj, 'ref', None)
    cat.addValueIndex(dummy, dump, load)
    site = hooks.getSite()
    if zope.component.interfaces.ISite.providedBy(site):
        sm = site.getSiteManager()
        sm['default']['relations'] = cat
        sm.registerUtility(cat, zc.relation.interfaces.ICatalog)
    else:
        zope.component.provideUtility(cat, zc.relation.interfaces.ICatalog)


# dump and load methods for relation catalog

def dump(obj, catalog, cache):
    """ Dump an object."""
    intids_ut = cache.get('intids_ut')
    if not intids_ut:
        intids_ut = zope.component.getUtility(IIntIds)
        cache['intids_ut'] = intids_ut
    return intids_ut.getId(obj)

def load(token, catalog, cache):
    """Load an object."""
    intids_ut = cache.get('intids_ut')
    if not intids_ut:
        intids_ut = zope.component.getUtility(IIntIds)
        cache['intids_ut'] = intids_ut
    return intids_ut.getObject(token)

def setUpIntIds(test):
    from zope.intid import IntIds
    from zope.intid.interfaces import IIntIds
    from zope.keyreference.testing import SimpleKeyReference
    zope.component.provideAdapter(SimpleKeyReference)
    site = hooks.getSite()
    if zope.component.interfaces.ISite.providedBy(site):
        sm = site.getSiteManager()
        sm['default']['intids'] = intids = IntIds()
        sm.registerUtility(intids, IIntIds)
    else:
        zope.component.provideUtility(IntIds(), IIntIds)

def setUpIndices(test):
    from z3c.indexer.interfaces import IIndex
    from z3c.indexer.index import SetIndex
    site = hooks.getSite()
    if zope.component.interfaces.ISite.providedBy(site):
        sm = site.getSiteManager()
        sm['default']['attribution-set'] = idx = SetIndex()
        sm.registerUtility(idx, IIndex, name='attribution-set')
        sm['default']['related-attribution-set'] = idx = SetIndex()
        sm.registerUtility(idx, IIndex, name='related-attribution-set')
    else:
        zope.component.provideUtility(SetIndex(), IIndex, name='attribution-set')
        zope.component.provideUtility(SetIndex(), IIndex, name='related-attribution-set')
