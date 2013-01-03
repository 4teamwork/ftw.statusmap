from ftw.statusmap.testing import FTW_STATUSMAP_INTEGRATION_TESTING
from unittest2 import TestCase
from ftw.statusmap.utils import executeTransition
from Products.CMFCore.utils import getToolByName

class TestTransitionExecution(TestCase):

    layer = FTW_STATUSMAP_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.wf_tool = getToolByName(self.portal, 'portal_workflow')
        self.wf_tool.setDefaultChain('simple_publication_workflow')
        self.cat = getToolByName(self.portal, 'portal_catalog')

    def test_execution(self):
        self.portal.invokeFactory('Document', 'brain1')
        brain1 = self.portal['brain1']
        brain1.invokeFactory('Document', 'brain2')
        brain2 = brain1['brain2']

        uids = [
            brain1.UID(),
            brain2.UID()
            ]
        executeTransition(self.portal, self.wf_tool, 'publish', uids, 'Lorem')
        self.assertEqual(len(self.cat.searchResults({'review_state':'published'})), 2)
