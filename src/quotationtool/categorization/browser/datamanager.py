import zope.interface
import zope.component
from z3c.form.interfaces import IDataManager, NO_VALUE
import BTrees

from quotationtool.categorization import interfaces


class NonExclusiveAttributionDataManager(object):
    """Data manager. 

    Generate some categories:

        >>> from quotationtool.categorization import testing, field, interfaces
        >>> categories = testing.generateCategoriesContainer(root)
        >>> categories['set1'].title = u"Set 1"
        >>> categories['set1'].description = u"Description of Set 1"

    Create a field:

        >>> fld = field.NonExclusiveAttributionField(categories['set1'])

    Create a categorizable item and set some attribution.

        >>> from quotationtool.categorization.testing import Categorizable
        >>> item = Categorizable()
        >>> attribution = interfaces.IAttribution(item)
        >>> attribution.set(('cat11', 'cat12', 'cat21', 'cat23', 'cat31',))

    Now we can use our datamanager:

        >>> from quotationtool.categorization.browser import datamanager
        >>> dm = datamanager.NonExclusiveAttributionDataManager(item, fld)
        >>> categories['set1']['cat11'] in dm.get()
        True
        >>> categories['set1']['cat12'] in dm.get()
        True
        >>> categories['set1']['cat13'] in dm.get()
        False

        >>> dm.query(default=None) == dm.get()
        True

        >>> dm.set(('cat13',))
        >>> list(attribution.get())
        [u'cat13', 'cat21', 'cat23', 'cat31']

        >>> dm.set(('cat11', 'cat22', 'cat32',))
        >>> list(attribution.get())
        [u'cat11', 'cat21', 'cat23', 'cat31']
        
        >>> dm.set(())
        >>> list(attribution.get())
        ['cat21', 'cat23', 'cat31']

        >>> dm.get()
        []

    The data manager can be looked up as a multiadapter.

        >>> from z3c.form.interfaces import IDataManager
        >>> import zope.component
        >>> dm = zope.component.getMultiAdapter((item, fld), IDataManager)
        >>> dm
        <quotationtool.categorization.browser.datamanager.NonExclusiveAttributionDataManager object at 0x...>
        >>> dm.get()
        []


    """

    zope.interface.implements(IDataManager)

    def __init__(self, context, field):
        self.context = context
        self.field = field
        self.category_set = field.category_set

    def get(self):
        attribution = list(interfaces.IAttribution(self.context).get())
        vocabulary = self.field.value_type.vocabulary
        rc = []
        for term in vocabulary:
            if term.value.__name__ in attribution:
                rc.append(term.value)
        return rc

    def query(self, default=NO_VALUE):
        return self.get()

    def queryOFF(self, default=NO_VALUE):
        try:
            return self.get()
        except Exception:
            return default

    def set(self, value):
        if self.field.readonly:
            raise TypeError("Can't set values on read-only fields "
                            "(name=%s, class=%s.%s)"
                            % (self.field.__name__,
                               self.context.__class__.__module__,
                               self.context.__class__.__name__))
        attribution = interfaces.IAttribution(self.context)
        vocabulary = self.field.value_type.vocabulary
        for term in vocabulary:
            if term.token in value:
                attribution.attribute(term.value.__name__)
            else:
                if attribution.isAttributed(term.value.__name__):
                    attribution.unattribute(term.value.__name__)

        #cats = attribution.attribution_factory(self.category_set.values())
        #for cat in cats:
        #    if cat.__name__ in value:
        #        attribution.attribute(cat.__name__)
        #    else:
        #        if attribution.isAttributed(cat.__name__):
        #            attribution.unattribute(cat.__name__)
                
    def canAccess(self):
        return True # TODO

    def canWrite(self):
        return True # TODO


class ExclusiveAttributionDataManager(NonExclusiveAttributionDataManager):
    """ Data manager that adapts to field.ExclusiveAttributionField.

    """

