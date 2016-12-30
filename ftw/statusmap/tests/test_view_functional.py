from DateTime import DateTime
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
            'Publish (Private =&gt; Published)</label>',
            browser.contents)
        self.assertIn(
            '<label class="transitionLabel" for="submit">'
            'Submit for publication (Private =&gt; Pending review)</label>',
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
            u'Ver\xf6ffentlichen (Privat => Ver\xf6ffentlicht)',
            [label.text for label in labels])

        self.assertIn(
            u'Zur Ver\xf6ffentlichung einreichen (Privat => Zur Redaktion eingereicht)',
            [label.text for label in labels])

    @browsing
    def test_statusmap_on_objects_having_inactive_content(self, browser):
        # Create a container which will hold the content used for this test.
        # The container does not play an important role in the test.
        folder = create(Builder('folder').titled('Container'))

        # Create some content used in this test.
        create(Builder('folder')
               .titled('Active Folder')
               .within(folder))
        create(Builder('folder')
               .titled('Inactive Folder')
               .having(effectiveDate=DateTime() + 10)
               .within(folder))

        # A user not having the permission to access inactive content can only
        # change the state of the container and the active folder inside the
        # container, but not the inactive folder inside the container.
        # Thus the inactive folder must not be visible in the statusmap view.
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        transaction.commit()
        browser.login().visit(folder, view="@@statusmap")
        self.assertEqual(
            ['Container', 'Active Folder'],
            browser.css('.listing tr td span').text
        )

        # A manager can also change the state of the inactive folder.
        # Thus the inactive folder must be visible in the statusmap view too.
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        transaction.commit()
        browser.login().visit(folder, view="@@statusmap")
        self.assertEqual(
            ['Container', 'Active Folder', 'Inactive Folder'],
            browser.css('.listing tr td span').text
        )

    @browsing
    def test_statusmap_on_inactive_content(self, browser):
        inactive_folder = create(Builder('folder')
                                 .titled('Inactive Folder')
                                 .having(effectiveDate=DateTime() + 10)
                                 .within(self.portal))

        create(Builder('folder')
               .titled('Active Folder')
               .within(inactive_folder))

        # A user not having the permission to access inactive content must
        # be able to change the state of the inactive content itself, i.e.
        # calling the statusmap view on an inactive context.
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        transaction.commit()
        browser.login().visit(inactive_folder, view="@@statusmap")
        self.assertEqual(
            ['Inactive Folder', 'Active Folder'],
            browser.css('.listing tr td span').text
        )

        # The same applies to a user having the permission to access inactive
        # content.
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        transaction.commit()
        browser.login().visit(inactive_folder, view="@@statusmap")
        self.assertEqual(
            ['Inactive Folder', 'Active Folder'],
            browser.css('.listing tr td span').text
        )
