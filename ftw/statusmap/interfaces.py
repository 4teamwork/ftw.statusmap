from zope.interface import Interface


class IConstraintChecker(Interface):
    """Utility interface to check if a transition is allowed
    on an object or not.
    """

    def is_transition_allowed(obj, transition):
        """Checks if the given transition is allowed on the object
        """
