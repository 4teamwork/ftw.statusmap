from ftw.builder import Builder
from ftw.builder import create
from ftw.statusmap.testing import FTW_STATUSMAP_PUBLISHER_FUNCTIONAL_TESTING
from ftw.statusmap.utils import executeTransition
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
import transaction


EXAMPLE_WF_ID = 'publisher-example-workflow'
EXAMPLE_WF_INTERNAL = 'publisher-example-workflow--STATUS--internal'
EXAMPLE_WF_PUBLISHED = 'publisher-example-workflow--STATUS--published'

EXAMPLE_WF_PUBLISH_ACTION = 'publisher-example-workflow--TRANSITION--publish--internal_published'


class TestFtwPublisherConstraintCheckerUtility(TestCase):

    layer = FTW_STATUSMAP_PUBLISHER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Reviewer'])
        login(self.portal, TEST_USER_NAME)

        self.wf_tool = getToolByName(self.portal, 'portal_workflow')
        self.wf_tool.setChainForPortalTypes(['Document', 'Folder', 'ContentPage'],
                                            EXAMPLE_WF_ID)

        transaction.commit()

    def test_do_not_publish_if_ftw_publisher_constraints_are_false(self):
        # Publishing an object if the parent object is not published
        # should not be possible with the publisher example workflow.
        # See ftw.publisher.sender test on github:
        # test_example_workflow_constraint_definition.py

        folder = create(Builder('folder')
                        .in_state(EXAMPLE_WF_INTERNAL))
        page = create(Builder('page')
                      .within(folder)
                      .in_state(EXAMPLE_WF_INTERNAL))

        uids = [page.UID(), ]

        executeTransition(
            self.portal, self.wf_tool, EXAMPLE_WF_PUBLISH_ACTION, uids, 'Lorem')

        self.assertEqual(
            EXAMPLE_WF_INTERNAL,
            api.content.get_state(obj=folder),
            'The page should still be private because the checker was false')

    def test_publish_if_ftw_publisher_constraints_are_true(self):
        # Publishing an object if the parent object is published
        # should be possible with the publisher example workflow.
        # See ftw.publisher.sender test on github:
        # test_example_workflow_constraint_definition.py

        folder = create(Builder('folder')
                        .in_state(EXAMPLE_WF_PUBLISHED))
        page = create(Builder('page')
                      .within(folder)
                      .in_state(EXAMPLE_WF_INTERNAL))

        uids = [page.UID(), ]

        executeTransition(
            self.portal, self.wf_tool, EXAMPLE_WF_PUBLISH_ACTION, uids, 'Lorem')

        self.assertEqual(
            EXAMPLE_WF_PUBLISHED,
            api.content.get_state(obj=folder),
            'The page should still be published because the checker was true')
