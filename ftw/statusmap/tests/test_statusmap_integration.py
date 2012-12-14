from ftw.statusmap.testing import FTW_STATUSMAP_INTEGRATION_TESTING
from unittest2 import TestCase
from ftw.statusmap.utils import getInfos, executeTransition
from Products.CMFCore.utils import getToolByName

class TestStatusmap(TestCase):

    layer = FTW_STATUSMAP_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.wf_tool = getToolByName(self.portal, 'portal_workflow')
        self.wf_tool.setDefaultChain('simple_publication_workflow')
        self.cat = getToolByName(self.portal, 'portal_catalog')

        doc1 = self.portal.get(self.portal.invokeFactory('Folder', 'folder1'))
        self.portal.invokeFactory('Document', 'document2')
        doc1.invokeFactory('Document', 'document3')

    def test_getInfos(self):
        result = getInfos(self.portal, self.cat, self.wf_tool)
        self.assertEqual(len(result), 3)
        for item in result:
            self.assertEqual(item['transitions'], [['publish', 'Publish'],
                  ['submit', 'Submit for publication']])
            self.assertEqual(item['review_state'], 'private')
        self.assertEqual(result[0]['level'], 1)
        self.assertEqual(result[1]['level'], 1)
        self.assertEqual(result[2]['level'], 2)

    def test_executeTransition(self):
        brains = self.cat.searchResults({})
        executeTransition(self.portal, self.wf_tool, 'publish', [brains[2].UID], comment="Bla Bla Bla Mr. Freeman")
        brains = self.cat.searchResults({})
        self.assertEqual(brains[2].review_state, 'published')
