from ftw.builder import Builder
from ftw.builder import create
from ftw.statusmap.testing import FTW_STATUSMAP_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
import transaction


class TestStatusmapViewFunctional(TestCase):

    layer = FTW_STATUSMAP_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestStatusmapViewFunctional, self).setUp()
        self.portal = self.layer['portal']
        self.wf_tool = getToolByName(self.portal, 'portal_workflow')
        self.wf_tool.setDefaultChain('simple_publication_workflow')
        self.cat = getToolByName(self.portal, 'portal_catalog')

        regtool = getToolByName(self.portal, 'portal_registration')
        regtool.addMember('user2', 'user2',
                          properties={'username': 'user2',
                                      'fullname': 'f\xc3\xbcllname2',
                                      'email': 'user2@email.com'})
        doc1 = self.portal.get(self.portal.invokeFactory('Folder', 'folder1'))
        self.portal.invokeFactory('Document', 'document2')
        self.doc2 = doc1.get(doc1.invokeFactory('Document', 'document3'))
        transaction.commit()

    def test_view_browser(self):
        browser = Browser(self.layer['app'])
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % (
            TEST_USER_NAME, TEST_USER_PASSWORD,))
        browser.open(self.portal.absolute_url() + '/statusmap')
        self.assertIn('<a href="http://nohost/plone/folder1/document3"',
            browser.contents)
        self.assertIn('<a href="http://nohost/plone/document2"',
            browser.contents)
        self.assertIn('<a href="http://nohost/plone/folder1"',
            browser.contents)
        self.assertIn(
            '<label class="transitionLabel" for="publish">'
            'publish - private =&gt; published</label>',
            browser.contents)
        self.assertIn(
            '<label class="transitionLabel" for="submit">'
            'submit - private =&gt; pending</label>',
            browser.contents)

        browser.post(
            'statusmap', data="form.submitted=1&uids:list=445i85-556986-55969")
        self.assertIn('Please select a Transition', browser.contents)

        browser.post('statusmap', data="form.submitted=1&transition=publish")
        self.assertIn('Please select at least one Item', browser.contents)

        browser.post('statusmap', data="form.submitted=1")
        self.assertIn('Please select at least one Item', browser.contents)
        self.assertIn('Please select a Transition', browser.contents)

        data = "form.submitted=1&uids:list=%s&transition=publish" % (
            self.doc2.UID())
        browser.post('statusmap', data=data)
        self.assertIn('Transition executed successfully.', browser.contents)

        browser.open(self.portal.absolute_url() + '/statusmap')
        browser.getControl(name='abort').click()
        self.assertEqual(browser.url.strip('/'), self.portal.absolute_url())

    def test_view_reader(self):
        setRoles(self.portal, 'user2', ['Reader'])
        transaction.commit()
        browser = Browser(self.layer['app'])
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % ('user2', 'user2',))
        browser.open(self.portal.absolute_url() + '/statusmap')
        self.assertNotIn('name="submit"', browser.contents)
        self.assertNotIn(
            '<input type="checkbox" name="uids:list" class="statusmap-uids"',
            browser.contents)
        browser.getControl(name="back").click()
        self.assertEqual(browser.url.strip('/'), self.portal.absolute_url())

    @browsing
    def test_transistions_with_translated_start_and_end_state(self, browser):
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
