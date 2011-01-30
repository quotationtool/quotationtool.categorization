import zope.interface
import zope.component
from z3c.form.interfaces import IDataManager, NOVALUE
from zope.intid.interfaces import IIntIds

import interfaces


class ExclusiveAttributionDataManager(object):
    """A data manager for exclusive attribution fields.

    The data manager adapts to field.ExclusiveAttributionField the
    constructor of which takes a category set as argument. Since the
    field handles things restrictively we must have a valid parent for
    the category set, too. So let's create some content first.

        >>> from quotationtool.categorization.testing \
        import createSomeCategorySet
        >>> cs = createSomeCategorySet()
        >>> from quotationtool.categorization.categoriescontainer \
        import CategoriesContainer
        >>> categories = CategoriesContainer()
        >>> categories['dummy'] = cs


        >>> from quotationtool.categorization.field \
        import ExclusiveAttributionField
        >>> fld = ExclusiveAttributionField(cs)

        >>> categories = [term.value for term in fld.vocabulary]
        >>> categories
        [<quotationtool.categorization.category.Category object at ...>, <quotationtool.categorization.category.Category object at ...>]

        >>> term1 = categories[0]
        >>> term2 = categories[1]


    We also need a categorizable object.

        >>> from quotationtool.categorization import interfaces
        >>> import zope.interface
        >>> from zope.location.interfaces import ILocation
        >>> class Categorizable(object):
        ...     zope.interface.implements(
        ...         interfaces.ICategorizable,
        ...         ILocation)
        ...     __name__ = __parent__ = None


    We store it on the root folder which was created during the setup
    of the test. It's to store it there because it will be the context
    in which the datamanager will try to lookup an integer id utility.
        
        >>> p = root['p'] = Categorizable()


    And we need a integer id utility and register the object from
    above. The testing module provides us with a dummy intid utility.

        >>> from zope.intid.interfaces import IIntIds
        >>> from quotationtool.categorization.testing import DummyIntIds
        >>> intids = DummyIntIds()
        >>> sm = root.getSiteManager()
        >>> sm.registerUtility(intids, IIntIds)
        
        >>> p_id = intids.register(p)


    Now, we can test the datamanager. It takes the field (fld) and the
    categorized object (p) on its constructor:

        >>> from quotationtool.categorization.datamanager \
        import ExclusiveAttributionDataManager 
        >>> dm = ExclusiveAttributionDataManager(p, fld)


    After the set() method was called, only one of the categories is
    actually attributed (exclusive).
    
        >>> dm.set(term1)
        >>> interfaces.IAttributionQuery(term1).isAttributed(p_id)
        True

        >>> interfaces.IAttributionQuery(term2).isAttributed(p_id)
        False

        >>> dm.query() == term1
        True

        >>> dm.set(term2)
        >>> interfaces.IAttributionQuery(term1).isAttributed(p_id)
        False

        >>> interfaces.IAttributionQuery(term2).isAttributed(p_id)
        True

        >>> dm.get() == term2
        True

    When a category is attributed, the category set is attributed, too.

        >>> interfaces.IAttributionQuery(cs).isAttributed(p_id)
        True

        >>> dm.set(None)
        >>> dm.get()

        >>> interfaces.IAttributionQuery(cs).isAttributed(p_id)
        False

    """

    zope.interface.implements(IDataManager)

    zope.component.adapts(interfaces.ICategorizable,
                          interfaces.IExclusiveAttributionField)

    def __init__(self, context, field):
        self.context = context
        self.field = field
        ut = zope.component.getUtility(
            IIntIds,
            context = context)
        self.context_intid = ut.getId(context)

    def get(self):
        for term in self.field.vocabulary:
            if interfaces.IAttributionQuery(term.value).isAttributed(self.context_intid):
                return term.value
        return None # TODO: Ok?

    def query(self, default = NOVALUE):
        got = self.get()
        if got is None:
            return default
        return got

    def set(self, value):
        if self.field.readonly:
            raise TypeError("Can't set values on read-only fields "
                            "(name=%s, class=%s.%s)"
                            % (self.field.__name__,
                               self.context.__class__.__module__,
                               self.context.__class__.__name__))
        if value:
            interfaces.IAttributionInjection(self.field.category_set).attribute_doc(
                self.context_intid, self.context)
        else:
            interfaces.IAttributionInjection(self.field.category_set).unattribute_doc(
                self.context_intid)
        for term in self.field.vocabulary:
            if term.value == value:
                interfaces.IAttributionInjection(value).attribute_doc(
                    self.context_intid, self.context)
            else:
                if interfaces.IAttributionQuery(term.value).isAttributed(
                    self.context_intid):
                    interfaces.IAttributionInjection(term.value).unattribute_doc(
                        self.context_intid)
                
    def canAccess(self):
        return True # TODO

    def canWrite(self):
        return True # TODO


class NonExclusiveAttributionDataManager(object):
    """A data manager for non-exclusive attribution fields.

    The data manager adapts to field.ExclusiveAttributionField the
    constructor of which takes a category set as argument. So let's
    create some content first.

        >>> from quotationtool.categorization.testing \
        import createSomeCategorySet
        >>> cs = createSomeCategorySet()
        >>> from quotationtool.categorization.categoriescontainer \
        import CategoriesContainer
        >>> categories = CategoriesContainer()
        >>> categories['dummy'] = cs


        >>> from quotationtool.categorization.field \
        import NonExclusiveAttributionField
        >>> fld = NonExclusiveAttributionField(cs)

        >>> categories = [term.value for term in fld.value_type.vocabulary]
        >>> categories
        [<quotationtool.categorization.category.Category object at ...>, <quotationtool.categorization.category.Category object at ...>]

        >>> term1 = categories[0]
        >>> term2 = categories[1]


    We also need a categorizable object.

        >>> from quotationtool.categorization import interfaces
        >>> import zope.interface
        >>> from zope.location.interfaces import ILocation
        >>> class Categorizable(object):
        ...     zope.interface.implements(
        ...         interfaces.ICategorizable,
        ...         ILocation)
        ...     __name__ = __parent__ = None


    We store it on the root folder which was created during the setup
    of the test. It's to store it there because it will be the context
    in which the datamanager will try to lookup an integer id utility.
        
        >>> p = root['p'] = Categorizable()


    And we need a integer id utility and register the object from
    above. The testing module provides us with a dummy intid utility.

        >>> from zope.intid.interfaces import IIntIds
        >>> from quotationtool.categorization.testing import DummyIntIds
        >>> intids = DummyIntIds()
        >>> sm = root.getSiteManager()
        >>> sm.registerUtility(intids, IIntIds)
        
        >>> p_id = intids.register(p)


    Now, we can test the datamanager:

        >>> from quotationtool.categorization.datamanager \
        import NonExclusiveAttributionDataManager 
        >>> dm = NonExclusiveAttributionDataManager(p, fld)


    After set, only one of the categories given to the set method are
    attributed.
    
        >>> dm.set([term2, term1])
        >>> term1 in dm.get() and term2 in dm.get()
        True

        >>> dm.set([term1])
        >>> interfaces.IAttributionQuery(term1).isAttributed(p_id)
        True

        >>> interfaces.IAttributionQuery(term2).isAttributed(p_id)
        False

        >>> dm.query() == [term1]
        True

        >>> dm.set([term2])
        >>> interfaces.IAttributionQuery(term1).isAttributed(p_id)
        False

        >>> interfaces.IAttributionQuery(term2).isAttributed(p_id)
        True

        >>> dm.get() == [term2]
        True

    If a category is attributed, the category set is attributed, too.

        >>> interfaces.IAttributionQuery(cs).isAttributed(p_id)
        True

        >>> dm.set([])
        >>> dm.get()
        []

        >>> interfaces.IAttributionQuery(cs).isAttributed(p_id)
        False

    """

    zope.interface.implements(IDataManager)

    zope.component.adapts(interfaces.ICategorizable,
                          interfaces.INonExclusiveAttributionField)

    def __init__(self, context, field):
        self.context = context
        self.field = field
        self.vocabulary = field.value_type.vocabulary
        ut = zope.component.getUtility(
            IIntIds,
            context = context)
        self.context_intid = ut.getId(context)

    def get(self):
        rc = []
        for term in self.vocabulary:
            if interfaces.IAttributionQuery(term.value).isAttributed(self.context_intid):
                rc.append(term.value)
        return rc

    def query(self, default = NOVALUE):
        got = self.get()
        if got is None:
            return default
        return got

    def set(self, value):
        if self.field.readonly:
            raise TypeError("Can't set values on read-only fields "
                            "(name=%s, class=%s.%s)"
                            % (self.field.__name__,
                               self.context.__class__.__module__,
                               self.context.__class__.__name__))
        if value:
            interfaces.IAttributionInjection(self.field.category_set).attribute_doc(
                self.context_intid, self.context)
        else:
            interfaces.IAttributionInjection(self.field.category_set).unattribute_doc(
                self.context_intid)
        for term in self.vocabulary:
            if term.value in value:
                interfaces.IAttributionInjection(term.value).attribute_doc(
                    self.context_intid, self.context)
            else:
                try:
                    interfaces.IAttributionInjection(term.value).unattribute_doc(
                        self.context_intid)
                except KeyError:
                    pass
                
    def canAccess(self):
        return True # TODO

    def canWrite(self):
        return True # TODO


