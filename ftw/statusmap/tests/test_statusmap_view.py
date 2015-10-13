from ftw.builder import Builder
from ftw.builder import create
from ftw.statusmap.testing import FTW_STATUSMAP_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
import transaction


class TestStatusmapView(TestCase):

    layer = FTW_STATUSMAP_FUNCTIONAL_TESTING

    @browsing
    def test_calling_view_does_not_fail(self, browser):
        folder = create(Builder('folder'))
        browser.login().visit(folder, view="@@statusmap")

        self.assertEqual(1, len(browser.css('.statusMapForm')))

    @browsing
    def test_all_nodes_are_listed(self, browser):
        folder = create(Builder('folder'))
        create(Builder('folder').within(folder))
        create(Builder('page').within(folder))

        browser.login().visit(folder, view="@@statusmap")

        self.assertEqual(3, len(browser.css('.statusMapRow')))

    @browsing
    def test_change_state_with_no_transition_will_fail(self, browser):
        folder = create(Builder('folder'))

        browser.visit(folder, {'form.submitted': '1'}, view='@@statusmap')

        self.assertEqual(
            '"[ERROR] Please select a Transition"',
            statusmessages.as_string())

    @browsing
    def test_change_state_with_no_uids_will_fail(self, browser):
        folder = create(Builder('folder'))

        browser.login().visit(
            folder,
            {'form.submitted': '1', 'transition': 'publish'},
            view='@@statusmap')

        self.assertEqual(
            '"[ERROR] Please select at least one Item"',
            statusmessages.as_string())

    @browsing
    def test_change_state_will_effect_on_all_selected_elements(self, browser):
        wf_tool = api.portal.get_tool('portal_workflow')
        wf_tool.setDefaultChain('simple_publication_workflow')

        folder = create(Builder('folder').in_state('private'))
        doc1 = create(Builder('page').within(folder).in_state('private'))
        doc2 = create(Builder('page').within(folder).in_state('private'))

        browser.login().visit(
            folder,
            {
                'form.submitted': '1',
                'transition': 'publish',
                'uids': [folder.UID(), doc2.UID()],
            },
            view='@@statusmap')

        statusmessages.assert_no_error_messages()

        self.assertEqual(
            '"[INFO] Transition executed successfully."',
            statusmessages.as_string())

        self.assertEqual('published', api.content.get_state(folder))
        self.assertEqual('published', api.content.get_state(doc2))
        self.assertEqual('private', api.content.get_state(doc1))

    @browsing
    def test_redirect_to_default_view_on_abort(self, browser):
        folder = create(Builder('folder'))

        browser.visit(folder, {'abort': '1'}, view='@@statusmap')

        statusmessages.assert_no_error_messages()
        self.assertEqual(folder.absolute_url(), browser.url)

    @browsing
    def test_redirect_to_default_view_on_back(self, browser):
        folder = create(Builder('folder'))

        browser.visit(folder, {'back': '1'}, view='@@statusmap')

        statusmessages.assert_no_error_messages()
        self.assertEqual(folder.absolute_url(), browser.url)


class TestTranslateType(TestCase):

    layer = FTW_STATUSMAP_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_get_translated_type(self):
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de')
        transaction.commit()

        view = self.portal.restrictedTraverse('statusmap')
        msg = view.get_translated_type('Document')

        self.assertEqual(msg, u'Page')

    def test_get_translated_type_fallback(self):
        view = self.portal.restrictedTraverse('statusmap')
        msg = view.get_translated_type('DUMMY')

        self.assertEqual(msg, u'DUMMY')


class TestTranslateTransitionTitle(TestCase):

    layer = FTW_STATUSMAP_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    @browsing
    def test_transistions_with_translated_start_and_end_state(self, browser):
        wf_tool = api.portal.get_tool('portal_workflow')
        wf_tool.setDefaultChain('simple_publication_workflow')

        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        transaction.commit()

        folder = create(Builder('folder'))
        browser.login().visit(folder, view="@@statusmap")

        labels = browser.css('.transitionLabel')

        self.assertEqual(
            2, len(labels),
            "The default workflow has two transitions from the private state. "
            "So there should be two labels. One for each transition")

        self.assertIn(
            u'ver\xf6ffentlichen - privat => ver\xf6ffentlicht',
            [label.text for label in labels])

        self.assertIn(
            u'einreichen - privat => wartend',
            [label.text for label in labels])
