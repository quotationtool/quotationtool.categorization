import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('quotationtool')


modes = {
     'exclusive': _('quotationtool.categorization.mode.exclusive',
                    u"exclusive"),
     'non-exclusive': _('quotationtool.categorization.mode.non-exclusive',
                        u"non-exclusive"),
     }


def modeVocabulary(context):
    terms = [SimpleTerm(name, title = item) for name, item in modes.items()]
    return SimpleVocabulary(terms)
zope.interface.alsoProvides(modeVocabulary,
                            IVocabularyFactory)
