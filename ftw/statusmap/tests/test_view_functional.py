from ftw.statusmap.testing import FTW_STATUSMAP_FUNCTIONAL_TESTING
from unittest2 import TestCase
from Products.CMFCore.utils import getToolByName
from plone.testing.z2 import Browser
import transaction
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD

class TestStatusmapViewFunctional(TestCase):

    layer = FTW_STATUSMAP_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestStatusmapViewFunctional, self).setUp()
        self.portal = self.layer['portal']
        self.wf_tool = getToolByName(self.portal, 'portal_workflow')
        self.wf_tool.setDefaultChain('simple_publication_workflow')
        self.cat = getToolByName(self.portal, 'portal_catalog')

        doc1 = self.portal.get(self.portal.invokeFactory('Folder', 'folder1'))
        self.portal.invokeFactory('Document', 'document2')
        self.doc2 = doc1.get(doc1.invokeFactory('Document', 'document3'))
        transaction.commit()

    def test_view_browser(self):
        browser = Browser(self.layer['app'])
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))
        browser.open(self.portal.absolute_url()+'/statusmap')
        self.assertIn('<a href="http://nohost/plone/folder1/document3"', browser.contents)
        self.assertIn('<a href="http://nohost/plone/document2"', browser.contents)
        self.assertIn('<a href="http://nohost/plone/folder1"', browser.contents)
        self.assertIn('<label for="publish">Publish</label>', browser.contents)
        self.assertIn('<label for="submit">Submit for publication</label>', browser.contents)

        browser.post('statusmap', data="form.submitted=1&uids:list=445i85-556986-55969")
        self.assertIn('Please select a Transition', browser.contents)

        browser.post('statusmap', data="form.submitted=1&transition=publish")
        self.assertIn('Please select at least one Item', browser.contents)

        browser.post('statusmap', data="form.submitted=1")
        self.assertIn('Please select at least one Item', browser.contents)
        self.assertIn('Please select a Transition', browser.contents)

        data = "form.submitted=1&uids:list=%s&transition=publish" % self.doc2.UID()
        browser.post('statusmap', data=data)
        self.assertIn('Transition executed successfully.', browser.contents)
