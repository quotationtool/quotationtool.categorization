import zope.interface
from persistent import Persistent
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.container.contained import Contained

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


class Categorizable(Persistent, Contained):
    """ A dummy class that is categorizable."""
    zope.interface.implements(IAttributeAnnotatable, ICategorizable)


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



import random

import BTrees
from persistent import Persistent
from zope.interface import implements
from zope.location.interfaces import ILocation
from zope.security.proxy import removeSecurityProxy

from zope.intid.interfaces import IIntIds, IIntIdEvent



class DummyIntIds(object):

    implements(IIntIds)

    _v_nextid = None

    _randrange = random.randrange

    family = BTrees.family32

    def __init__(self, family=None):
        if family is not None:
            self.family = family
        self.ids = self.family.OI.BTree()
        self.refs = self.family.IO.BTree()

    def __len__(self):
        return len(self.ids)

    def items(self):
        return list(self.refs.items())

    def __iter__(self):
        return self.refs.iterkeys()

    def getObject(self, id):
        return self.refs[id]

    def queryObject(self, id, default=None):
        r = self.refs.get(id)
        if r is not None:
            return r
        return default

    def getId(self, ob):
        try:
            return self.ids[ob]
        except KeyError:
            raise KeyError(ob)

    def queryId(self, ob, default=None):
        try:
            return self.getId(ob)
        except KeyError:
            return default

    def _generateId(self):
        """Generate an id which is not yet taken.

        This tries to allocate sequential ids so they fall into the
        same BTree bucket, and randomizes if it stumbles upon a
        used one.
        """
        while True:
            if self._v_nextid is None:
                self._v_nextid = self._randrange(0, self.family.maxint)
            uid = self._v_nextid
            self._v_nextid += 1
            if uid not in self.refs:
                return uid
            self._v_nextid = None

    def register(self, ob):
        # Note that we'll still need to keep this proxy removal.
        ob = removeSecurityProxy(ob)
        key = ob

        if key in self.ids:
            return self.ids[key]
        uid = self._generateId()
        self.refs[uid] = key
        self.ids[key] = uid
        return uid

    def unregister(self, ob):
        # Note that we'll still need to keep this proxy removal.
        ob = removeSecurityProxy(ob)
        key = ob
        if key is None:
            return

        uid = self.ids[key]
        del self.refs[uid]
        del self.ids[key]

@zope.component.adapter(ILocation, IObjectRemovedEvent)
def removeIntIdSubscriber(ob, event):
    """A subscriber to ObjectRemovedEvent

    Removes the unique ids registered for the object in all the unique
    id utilities.
    """
    utilities = tuple(zope.component.getAllUtilitiesRegisteredFor(IIntIds))
    if utilities:
        # Notify the catalogs that this object is about to be removed.
        zope.event.notify(IntIdRemovedEvent(ob, event))
        for utility in utilities:
            try:
                utility.unregister(ob)
            except KeyError:
                pass


@zope.component.adapter(ILocation, IObjectAddedEvent)
def addIntIdSubscriber(ob, event):
    """A subscriber to ObjectAddedEvent

    Registers the object added in all unique id utilities and fires
    an event for the catalogs.
    """
    utilities = tuple(zope.component.getAllUtilitiesRegisteredFor(IIntIds))
    if utilities: # assert that there are any utilites
        idmap = {}
        for utility in utilities:
            idmap[utility] = utility.register(ob)
        # Notify the catalogs that this object was added.
        zope.event.notify(IntIdAddedEvent(ob, event, idmap))


