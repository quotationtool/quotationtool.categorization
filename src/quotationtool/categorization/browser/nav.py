import zope.interface
from z3c.menu.ready2go.item import SiteMenuItem
from zope.viewlet.manager import ViewletManager
from z3c.menu.ready2go import ISiteMenu, IContextMenu
from z3c.menu.ready2go.manager import MenuManager
from z3c.menu.ready2go.interfaces import IMenuManager

from quotationtool.skin.interfaces import IMainNav, ISubNavManager
from quotationtool.skin.browser.nav import MainNavItem


class ICategoriesContainerMainNavItem(zope.interface.Interface):
    pass


class CategoriesContainerMainNavItem(MainNavItem):
    zope.interface.implements(ICategoriesContainerMainNavItem)


class ICategorizationSubNav(ISubNavManager):
    pass


CategorizationSubNav = ViewletManager(
    'categorizationsubnav', 
    ISiteMenu,
    bases = (MenuManager,))


ICategorizationSubNav.implementedBy(CategorizationSubNav)
