from ftw.statusmap.interfaces import IConstraintChecker
from zope.component import getGlobalSiteManager
from zope.component import getUtilitiesFor
from zope.interface import implements


class DummyCheckerTrue(object):
    implements(IConstraintChecker)

    def is_transition_allowed(self, obj, transition):
        return True


class DummyCheckerFalse(object):
    implements(IConstraintChecker)

    def is_transition_allowed(self, obj, transition):
        return False


def unregister_constraint_checkers():
    for name, klass in getUtilitiesFor(IConstraintChecker):
        getGlobalSiteManager().unregisterUtility(
            provided=IConstraintChecker, name=name)
