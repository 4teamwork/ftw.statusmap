from ftw.statusmap.testing import FTW_STATUSMAP_INTEGRATION_TESTING
from unittest2 import TestCase
from Products.CMFCore.utils import getToolByName
import json


class TestStatusmapView(TestCase):

    layer = FTW_STATUSMAP_INTEGRATION_TESTING

    def setUp(self):
        super(TestStatusmapView, self).setUp()
        self.portal = self.layer['portal']
        self.wf_tool = getToolByName(self.portal, 'portal_workflow')
        self.wf_tool.setDefaultChain('simple_publication_workflow')
        self.cat = getToolByName(self.portal, 'portal_catalog')

        doc1 = self.portal.get(self.portal.invokeFactory('Folder', 'folder1'))
        self.portal.invokeFactory('Document', 'document2')
        doc1.invokeFactory('Document', 'document3')

    def test_view(self):
        view = self.portal.restrictedTraverse('statusmap')
        view.request['ACTUAL_URL'] = self.portal.absolute_url() + '/statusmap'
        view()
        possible_trans = json.loads(view.get_json())
        self.assertEqual(len(possible_trans), 3)
        self.assertIn(view.infos[0]['uid'], possible_trans.keys())
        self.assertIn(view.infos[1]['uid'], possible_trans.keys())
        self.assertIn(view.infos[2]['uid'], possible_trans.keys())

        self.assertEqual(
            possible_trans[view.infos[0]['uid']], ['publish', 'submit'])
        self.assertEqual(
            possible_trans[view.infos[1]['uid']], ['publish', 'submit'])
        self.assertEqual(
            possible_trans[view.infos[2]['uid']], ['publish', 'submit'])

        all_trans = view.list_transitions()

        self.assertEqual(
            all_trans,
            [{'new_review_state': 'Published',
              'old_review_state': 'Private',
              'id': 'publish',
              'title': 'Publish'},
             {'new_review_state': 'Pending review',
              'old_review_state': 'Private',
              'id': 'submit',
              'title': 'Submit for publication'}])

    def test_get_translated_type(self):
        view = self.portal.restrictedTraverse('statusmap')
        msg = view.get_translated_type('Document')

        self.assertEquals(msg, u'Page')

    def test_get_translated_type_fallback(self):
        view = self.portal.restrictedTraverse('statusmap')
        msg = view.get_translated_type('DUMMY')

        self.assertEquals(msg, u'DUMMY')
