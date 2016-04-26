from zope.component import queryMultiAdapter


class FtwPublisherConstraintChecker(object):
    """Check ftw.publisher.sender constraints.
    """

    modify_status_view = 'publisher-modify-status'

    def is_transition_allowed(self, obj, transition):
        constraint_checker = queryMultiAdapter(
            (obj, obj.REQUEST), name=self.modify_status_view)

        if not constraint_checker:
            return True

        return constraint_checker.is_transition_allowed(transition)
