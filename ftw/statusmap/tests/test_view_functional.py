from ftw.statusmap.testing import FTW_STATUSMAP_INTEGRATION_TESTING
from unittest2 import TestCase
from Products.CMFCore.utils import getToolByName
from plone.testing.z2 import Browser
import transaction
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD

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
        transaction.commit()

    def test_view_browser(self):
        browser = Browser(self.layer['app'])
        browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))
        browser.open(self.portal.absolute_url()+'/statusmap')
        self.assertIn('<a href="http://nohost/plone/folder1/document3"', browser.contents)
        self.assertIn('<a href="http://nohost/plone/document2"', browser.contents)
        self.assertIn('<a href="http://nohost/plone/folder1"', browser.contents)
        self.assertIn('<label for="publish">Publish</label>', browser.contents)
        self.assertIn('<label for="submit">Submit for publication</label>', browser.contents)

        browser.post('statusmap', data="form.submitted=1&uids='445i85-556986-55969'")
        import pdb; pdb.set_trace()
