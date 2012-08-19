import zope.component
import zope.interface
from zope.viewlet.viewlet import ViewletBase
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from z3c.searcher import criterium

from quotationtool.search.interfaces import ICriteriaReturningForm, ICriteriaChainSpecifier

from quotationtool.categorization import interfaces
from quotationtool.categorization.interfaces import _
from quotationtool.categorization.attribution import ATTRIBUTION_INDEX


class SearchFormExtension(ViewletBase):
    """ Extends the search form."""

    zope.interface.implements(ICriteriaReturningForm)

    template = ViewPageTemplateFile('search.pt')

    prefix = u'categorization.'

    def render(self):
        return self.template()

    def categories(self):
        """ for the template"""
        return zope.component.getUtility(
            interfaces.ICategoriesContainer, 
            context=self.context)

    def getCriteria(self, fltr, criteria_count, errors):
        """ See ICriteriaReturningForm"""
        criteria = []
        i = 0
        MISSING = u""
        for category_set in self.categories().values():
            j = 0
            for category in category_set.values():
                criterium = self.request.form.get(self.prefix + unicode(i) + u'.' + unicode(j) + u'.criterium', MISSING)
                connector = self.request.form.get(self.prefix + unicode(i) + u'.' + unicode(j) + u'.connector', u"OR")
                value = self.request.form.get(self.prefix + unicode(i) + u'.' + unicode(j) + u'.value', MISSING)
                if value != MISSING:
                    if value == category.__name__.encode('ascii', 'xmlcharrefreplace'):
                        crit = fltr.createCriterium(criterium)
                        if criteria_count == 0:
                            crit.connectorName = ICriteriaChainSpecifier(fltr).first_criterium_connector_name
                        else:
                            crit.connectorName = connector
                        crit.value = unicode(category.__name__) #  without xmlcharrefreplace
                        criteria.append(crit)
                        criteria_count += 1 # call by reference
                    else:
                        errors.append('bad query') # call by reference
                pass
                j += 1
            i += 1
        return criteria


class AttributionCriterium(criterium.SetSearchCriterium):
    """ Search criterium"""

    indexOrName = ATTRIBUTION_INDEX

    label = _('attribution-criterium', u"Category Label")


attribution_factory = criterium.factory(AttributionCriterium, ATTRIBUTION_INDEX)
