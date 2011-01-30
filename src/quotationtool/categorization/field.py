import md5

import zope.interface
import zope.component
import zope.schema
from zope.schema.fieldproperty import FieldProperty
from zope.i18nmessageid import MessageFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

import interfaces


contentMsg = MessageFactory('quotationtool.categorization.content')


def categoryVocabularyFactory(category_set):
    """Returns a vocabulary for a given category set.
    
        >>> from quotationtool.categorization.field \
        import categoryVocabularyFactory 
        >>> from quotationtool.categorization.testing \
        import createSomeCategorySet
        >>> cs = createSomeCategorySet()
        >>> cs.__name__ = u'dummy'
        >>> voc = categoryVocabularyFactory(cs)
        >>> categories_from_voc = [term.value for term in voc]
        >>> categories_from_voc == cs.values()
        True

        >>> titles_tokens = [(term.title, term.token) for term in voc]
        >>> titles_tokens
        [(u'dummy-philosophy-title', 'philosophy'), (u'dummy-jura-title', 'jura')]

    """
    
    return SimpleVocabulary(
        [SimpleTerm(category,
                    token = category.__name__.encode('ascii','xmlcharrefreplace'),
                    title = contentMsg(category_set.__name__ +
                                       u'-' + category.__name__ + u'-title',
                                       category.title))
         for category in category_set.values()])


class ExclusiveAttributionField(zope.schema.Choice):
    """A field for exclusive attribution. This is an adapter that
    adapts interfaces.ICategorySet.

    First let's create a category set. We also need a valid parent for
    it because the field property for the 'category_set' attribute of
    the datamanager is very restrictive. (Other components required
    are registered during test setup.)

        >>> from quotationtool.categorization.field \
        import ExclusiveAttributionField
        >>> from quotationtool.categorization.testing \
        import createSomeCategorySet
        >>> cs = createSomeCategorySet()
        >>> from quotationtool.categorization.categoriescontainer \
        import CategoriesContainer
        >>> categories = root['categories'] = CategoriesContainer()
        >>> categories['dummy'] = cs

    
    Now we can init our datamanager:

        >>> fld = ExclusiveAttributionField(cs)
        >>> fld
        <quotationtool.categorization.field.ExclusiveAttributionField object at ...>

        >>> fld.title
        u'dummy-title'

        >>> fld.description
        u'dummy-desc'

        >>> [term.value for term in fld.vocabulary] == cs.values()
        True

        >>> fld.category_set == cs
        True

    """

    zope.interface.implements(interfaces.IExclusiveAttributionField)
    
    zope.component.adapts(interfaces.ICategorySet)

    category_set = FieldProperty(interfaces.IAttributionField['category_set'])

    def __init__(self, context):
        self.category_set =  context
        kw = {
        'title': contentMsg(
            context.__name__ + '-title', context.title),
        'description': contentMsg(
            context.__name__ + '-desc', context.description),
        'required': False,
        'vocabulary': categoryVocabularyFactory(context),
        }
        super(ExclusiveAttributionField, self).__init__(**kw)
        

class NonExclusiveAttributionField(zope.schema.List):
    """A field for a non-exclusive attribution. It is an adapter that
    adapts to interfaces.ICategorySet

    First let's create a category set. We also need a valid parent for
    it because the field property for the 'category_set' attribute of
    the datamanager is very restrictive.

        >>> from quotationtool.categorization.testing \
        import createSomeCategorySet
        >>> cs = createSomeCategorySet()
        >>> from quotationtool.categorization.categoriescontainer \
        import CategoriesContainer
        >>> categories = root['categories'] = CategoriesContainer()
        >>> categories['dummy'] = cs

    
    Now we can init our datamanager:

        >>> from quotationtool.categorization.field \
        import NonExclusiveAttributionField
        >>> fld = NonExclusiveAttributionField(cs)
        >>> fld
        <quotationtool.categorization.field.NonExclusiveAttributionField object at ...>

        >>> fld.title
        u'dummy-title'

        >>> fld.description
        u'dummy-desc'

        >>> [term.value for term in fld.value_type.vocabulary] == cs.values()
        True

        >>> fld.category_set == cs
        True

    """

    zope.interface.implements(interfaces.INonExclusiveAttributionField)
    
    zope.component.adapts(interfaces.ICategorySet)

    category_set = FieldProperty(interfaces.IAttributionField['category_set'])

    def __init__(self, context):
        self.category_set = context
        kw = {
        'title': contentMsg(
            context.__name__ + '-title', context.title),
        'description': contentMsg(
            context.__name__ + '-desc', context.description),
        'required': False,
        'value_type': zope.schema.Choice(
            title = contentMsg(context.__name__ + 'valuetype-title',
                               context.title),
            required = False,
            vocabulary = categoryVocabularyFactory(context),
            ),
        }
        super(NonExclusiveAttributionField, self).__init__(**kw)
