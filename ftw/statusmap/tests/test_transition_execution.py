from ftw.statusmap.testing import FTW_STATUSMAP_INTEGRATION_TESTING
from unittest2 import TestCase
from ftw.statusmap.utils import executeTransition


class TestTransitionExecution(TestCase):

    layer = FTW_STATUSMAP_INTEGRATION_TESTING


    def test_execution(self):
        portal = self.layer['portal']
        portal.invokeFactory('Document', 'brain1')
        brain1 = portal['brain1']
        brain1.invokeFactory('Document', 'brain2')
        dicts = [
            {'path':'/Plone/brain1',
             'review_state':'private',
             'type': 'Document',
             'workflow': 'simple_publication_workflow',
             },
            {'path':'/Plone/brain1/brain2',
             'review_state':'published',
             'type': 'Document',
             'workflow': 'simple_publication_workflow',
             }
            ]
        executeTransition(portal.portal_workflow, 'publish', dicts)
        self.assertEqual(len(portal.portal_catalog.searchResults({'review_state':'published'})), 2)
