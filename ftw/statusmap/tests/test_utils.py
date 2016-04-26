from ftw.builder import Builder
from ftw.builder import create
from ftw.statusmap.interfaces import IConstraintChecker
from ftw.statusmap.testing import FTW_STATUSMAP_INTEGRATION_TESTING
from ftw.statusmap.tests.helpers import DummyCheckerFalse
from ftw.statusmap.tests.helpers import DummyCheckerTrue
from ftw.statusmap.tests.helpers import unregister_constraint_checkers
from ftw.statusmap.utils import executeTransition
from ftw.statusmap.utils import is_transition_allowed
from plone import api
from unittest2 import TestCase
from zope.component import getGlobalSiteManager


class TestIsTransitionAllowed(TestCase):

    layer = FTW_STATUSMAP_INTEGRATION_TESTING

    def setUp(self):
        super(TestIsTransitionAllowed, self).setUp()
        self.site_manager = getGlobalSiteManager()

    def test_return_true_if_no_utilities_are_registered(self):
        self.assertTrue(is_transition_allowed(object, "transition"))

    def test_return_true_if_all_utilities_returns_true(self):
        self.site_manager.registerUtility(
            DummyCheckerTrue(), IConstraintChecker, name=u'checker1: True')

        self.site_manager.registerUtility(
            DummyCheckerTrue(), IConstraintChecker, name=u'checker2: True')

        self.assertTrue(is_transition_allowed(object, "transition"))

    def test_return_false_if_at_least_one_utility_returns_false(self):
        self.site_manager.registerUtility(
            DummyCheckerTrue(), IConstraintChecker, name=u'checker1: True')

        self.site_manager.registerUtility(
            DummyCheckerFalse(), IConstraintChecker, name=u'checker2: False')

        self.site_manager.registerUtility(
            DummyCheckerTrue(), IConstraintChecker, name=u'checker3: True')

        self.assertFalse(is_transition_allowed(object, "transition"))

    def tearDown(self):
        super(TestIsTransitionAllowed, self).tearDown()
        unregister_constraint_checkers()


class TestExecuteTransition(TestCase):

    layer = FTW_STATUSMAP_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.wf_tool = api.portal.get_tool('portal_workflow')
        self.wf_tool.setDefaultChain('simple_publication_workflow')
        self.site_manager = getGlobalSiteManager()

    def test_execution(self):
        catalog = api.portal.get_tool('portal_catalog')

        folder1 = create(Builder('folder'))
        folder2 = create(Builder('folder'))

        uids = [
            folder1.UID(),
            folder2.UID()
            ]

        executeTransition(self.portal, self.wf_tool, 'publish', uids, 'Lorem')

        self.assertEqual(
            len(catalog.searchResults({'review_state': 'published'})), 2)

    def test_execute_transition_if_transition_is_allowed(self):
        self.site_manager.registerUtility(
            DummyCheckerTrue(), IConstraintChecker, name=u'checker1: True')

        folder = create(Builder('folder'))

        uids = [folder.UID(), ]

        executeTransition(self.portal, self.wf_tool, 'publish', uids, 'Lorem')

        self.assertEqual(
            'published',
            api.content.get_state(obj=folder),
            'The folder should be published because the checker was true')

    def test_do_not_execute_transition_if_transition_is_not_allowed(self):
        self.site_manager.registerUtility(
            DummyCheckerFalse(), IConstraintChecker, name=u'checker1: False')

        folder = create(Builder('folder'))

        uids = [folder.UID(), ]

        executeTransition(self.portal, self.wf_tool, 'publish', uids, 'Lorem')

        self.assertEqual(
            'private',
            api.content.get_state(obj=folder),
            'The folder should still be private because the checker was false')

    def tearDown(self):
        super(TestExecuteTransition, self).tearDown()
        unregister_constraint_checkers()
