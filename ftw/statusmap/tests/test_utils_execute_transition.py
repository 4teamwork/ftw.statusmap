from ftw.builder import Builder
from ftw.builder import create
from ftw.statusmap.testing import FTW_STATUSMAP_INTEGRATION_TESTING
from ftw.statusmap.utils import executeTransition
from plone import api
from Products.CMFCore.WorkflowCore import WorkflowException
from unittest2 import TestCase


class TestTransitionExecution(TestCase):

    layer = FTW_STATUSMAP_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        wf_tool = api.portal.get_tool('portal_workflow')
        wf_tool.setDefaultChain('simple_publication_workflow')

    def test_execute_one_element(self):
        folder = create(Builder('folder').in_state('private'))

        executeTransition('publish', [folder.UID(), ])

        self.assertEqual('published', api.content.get_state(folder))

    def test_execution_with_multiple_elements(self):
        folder1 = create(Builder('folder').in_state('private'))
        folder2 = create(Builder('folder').in_state('private'))

        uids = [
            folder1.UID(),
            folder2.UID()
            ]

        executeTransition('publish', uids)

        self.assertEqual('published', api.content.get_state(folder1))
        self.assertEqual('published', api.content.get_state(folder2))

    def test_execution_with_no_elements_does_nothing(self):
        self.assertIsNone(executeTransition('publish', []))

    def test_bad_transition_raises_an_error(self):
        folder = create(Builder('folder').in_state('private'))

        with self.assertRaises(WorkflowException):
            executeTransition('retract', [folder.UID(), ])

    def test_add_comment_to_version_history(self):
        wf_tool = api.portal.get_tool('portal_workflow')

        folder = create(Builder('folder').in_state('private'))

        executeTransition('publish', [folder.UID(), ], 'Chuck Norris')
        review_history = wf_tool.getInfoFor(folder, 'review_history')[-1]

        self.assertEqual('Chuck Norris', review_history.get('comments'))
