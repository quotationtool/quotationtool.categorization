Categorizable Items
-------------------

    >>> from quotationtool.categorization import interfaces
    >>> import zope.interface
    >>> import zope.component
    >>> from quotationtool.categorization.categorizableitemdescription\
    ...     import CategorizableItemDescription, CategorizableItemDescriptions

    >>> publication_desc = CategorizableItemDescription()
    >>> publication_desc.interface = object()
    Traceback (most recent call last):
    ...
    ConstraintNotSatisfied: <object object at ...>

    >>> class IPublication(zope.interface.Interface):
    ...     pass

    >>> zope.component.interface.provideInterface('.IPublication', IPublication)
    >>> iface = zope.component.interface.getInterface(None, '.IPublication')
    >>> iface == IPublication
    True

    >>> publication_desc.interface = IPublication
    >>> publication_desc.interface
    <InterfaceClass __builtin__.IPublication>

    >>> publication_desc.label = u"printed publication"

    >>> class IQuotation(zope.interface.Interface):
    ...     pass

    >>> zope.component.interface.provideInterface('.IQuotation', IQuotation)
    >>> quotation_desc = CategorizableItemDescription()
    >>> quotation_desc.interface = IQuotation
    >>> quotation_desc.label = u"quotation from publication"

Descriptions stored in a CategorizableItemDescriptions are possible
values for the categorizable_items attribute. To make this work the
container must be registered as a utility. That was done in test setup
already. So here we yust need to query that utility and store our
descriptions in it:

    >>> descriptions = zope.component.getUtility(
    ...     interfaces.ICategorizableItemDescriptions,
    ...     context = root)

    >>> descriptions['.ipublkation'] = publication_desc
    >>> descriptions['.iquotation'] = quotation_desc
    >>> interfaces.ICategorySet['categorizable_items'].validate([IPublication])

    >>> class IBad(zope.interface.Interface):
    ...     pass
    >>> interfaces.ICategorySet['categorizable_items'].validate([IBad])
    Traceback (most recent call last):
    ...
    WrongContainedType:...ConstraintNotSatisfied...





Categories and Category Sets
----------------------------



    >>> from quotationtool.categorization.categoryset import CategorySet
    >>> from quotationtool.categorization.category import Category


    >>> faculties = CategorySet()
    >>> faculties.title = u"Faculty"
    >>> faculties.description = u"The department of a university by which the item is administered."
    >>> faculties.categorizable_items = [IPublication, IQuotation]
    >>> faculties.weight = 1
    >>> faculties.mode = 'exclusive'
    >>> faculties.inherit = True

    >>> philosophy = Category()
    >>> philosophy.title = u"Philosophy"
    >>> philosophy.description = u"Kant calls it the ``lower faculty''. Truth is made here."
    >>> philosophy.weight = 1
    >>> faculties['philosophy'] = philosophy

    >>> medcine = Category()
    >>> medcine.title = u"Medical Science"
    >>> medcine.descriptions = u"Physicians are made here."
    >>> medcine.weight = 101
    >>> faculties['medcine'] = medcine

    >>> law = Category()
    >>> law.title = u"Law"
    >>> law.description = u"Executives are made here."
    >>> law.weight = 100
    >>> faculties['law'] = law

    >>> theology = Category()
    >>> theology.title = u"Theology"
    >>> theology.description = u"Priests are made here."
    >>> theology.weight = 102
    >>> faculties['theology'] = theology

    >>> faculties.keys()
    [u'philosophy', u'law', u'medcine', u'theology']

    >>> [dep.weight for dep in faculties.values()]
    [1, 100, 101, 102]

    >>> import zope.component.event
    >>> law.weight = 103
    >>> [dep.weight for dep in faculties.values()]
    [1, 103, 101, 102]

To notify when a category is reweighted there is an event handler. 

    >>> from quotationtool.categorization.weighteditemscontainer import updateWeightedItemsContainerOrder
    >>> zope.component.provideHandler(updateWeightedItemsContainerOrder)
    >>> from zope.lifecycleevent import ObjectModifiedEvent
    >>> zope.component.event.objectEventNotify(ObjectModifiedEvent(law))
    >>> [dep.weight for dep in faculties.values()]
    [1, 101, 102, 103]



Categories Container
--------------------

The category sets live in a container which implements the
IWeightedItemsContainer interface, too.

    >>> from quotationtool.categorization.categoriescontainer import CategoriesContainer
    >>> categories = CategoriesContainer()
    >>> categories['faculties'] = faculties
    >>> categories.keys()
    [u'faculties']

    >>> categories['artesliberales'] = artes = CategorySet()
    >>> artes.title = u"Artes liberales"
    >>> artes.description = u"The seven liberal arts"
    >>> categories.keys()
    [u'faculties', u'artesliberales']

    >>> [set.weight for set in categories.values()]
    [1, 1000]

    >>> del categories['artesliberales']
    >>> categories.keys()
    [u'faculties']


Play around with BTrees
~~~~~~~~~~~~~~~~~~~~~~~

    >>> import BTrees.IIBTree
    >>> TreeSet = BTrees.family32.II.TreeSet
    >>> #for i in zope.interface.providedBy(TreeSet()): print i
    >>> ints = TreeSet()
    >>> ints.insert(1)
    1
    
    >>> list(ints.keys())
    [1]
    
    >>> ints.insert(100)
    1

    >>> ints.insert(10)
    1

    >>> list(ints.keys())
    [1, 10, 100]

    >>> list(ints)
    [1, 10, 100]

    >>> ints.update([5,50,500])
    3

    >>> list(ints)
    [1, 5, 10, 50, 100, 500]

    >>> bool(ints.has_key(50))
    True
    

    >>> ints.remove(50)

    >>> bool(ints.has_key(50))
    False

    >>> ints.clear()
    >>> list(ints)
    []



    >>> interfaces.IAttributionInjection.providedBy(philosophy)
    True

    >>> interfaces.IAttributionQuery.providedBy(philosophy)
    True
    
    >>> interfaces.IAttributionTreeSet.providedBy(philosophy)
    True

    >>> philosophy.attribution
    <BTrees.IFBTree.IFBTree object at ...>

    #<BTrees.IIBTree.IITreeSet object at ...>


    >>> interfaces.IAttributionInjection.providedBy(faculties)
    True

    >>> interfaces.IAttributionQuery.providedBy(faculties)
    True
    
    >>> interfaces.IAttributionTreeSet.providedBy(faculties)
    True

    >>> faculties.attribution
    <BTrees.IFBTree.IFBTree object at ...>

    #<BTrees.IIBTree.IITreeSet object at ...>


    >>> class Item(object):
    ...     zope.interface.implements(interfaces.ICategorizable)

    >>> items = {}
    >>> for i in range(100):
    ...     items[i] = new_item = Item()
    ...     new_item.hello = u"Hello from %d" % i
    ...     faculties.attribute_doc(i, new_item)
    ...     if i % 4 == 0:
    ...         philosophy.attribute_doc(i, new_item)
    ...     if i % 4 == 1:
    ...         law.attribute_doc(i, new_item)
    ...     if i % 4 == 2:
    ...         medcine.attribute_doc(i, new_item)
    ...     if i % 4 == 3:
    ...         theology.attribute_doc(i, new_item)

    >>> faculties.isAttributed(1)
    True

    >>> philosophy.isAttributed(1)
    False

    >>> law.isAttributed(1)
    True

    >>> medcine.isAttributed(42)
    True

    >>> theology.isAttributed(69)
    False

    >>> medcine.unattribute_doc(42)

    >>> medcine.isAttributed(42)
    False

    >>> medcine.clearAttribution()
    >>> list(medcine.getAttribution())
    []

    >>> list(faculties.getAttribution())
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]

    >>> list(philosophy.getAttribution())
    [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96]



