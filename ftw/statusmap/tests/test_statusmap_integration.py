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

    def test_getInfos_amount_of_items(self):
        result = getInfos(self.portal, self.cat, self.wf_tool)
        self.assertEqual(len(result), 3)

    def test_getInfos_transitions_and_review_state(self):
        result = getInfos(self.portal, self.cat, self.wf_tool)

        for item in result:
            self.assertEqual(
                item['transitions'],
                [{'new_review_state': 'Published',
                  'old_review_state': 'Private',
                  'id': 'publish',
                  'title': 'Publish'},
                 {'new_review_state': 'Pending review',
                  'old_review_state': 'Private',
                  'id': 'submit',
                  'title': 'Submit for publication'}])
            self.assertEqual(item['review_state'], 'Private')

    def test_getInfos_order(self):
        result = getInfos(self.portal, self.cat, self.wf_tool)

        self.assertEqual(result[0]['path'], '/plone/document2')
        self.assertEqual(result[1]['path'], '/plone/folder1')
        self.assertEqual(result[2]['path'], '/plone/folder1/document3')

    def test_getInfos_level(self):
        result = getInfos(self.portal, self.cat, self.wf_tool)
        self.assertEqual(result[0]['level'], 1)
        self.assertEqual(result[1]['level'], 1)
        self.assertEqual(result[2]['level'], 2)

    def test_executeTransition(self):
        brains = self.cat.searchResults({})

        executeTransition(self.portal,
                          self.wf_tool,
                          'publish',
                          [brains[2].UID],
                          comment="Bla Bla Bla Mr. Freeman")

        brains = self.cat.searchResults({})
        self.assertEqual(brains[2].review_state, 'published')
