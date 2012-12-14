from plone.mocktestcase import MockTestCase
from ftw.statusmap.utils import getTransitionsForItem, getInfos
from mocker import ANY

class TestGetWorkflowInfo(MockTestCase):

    def setUp(self):
        super(TestGetWorkflowInfo, self).setUp()
        self.wf_tool = self.mocker.mock()
        self.expect(self.wf_tool).listAction
        self.obj = self.mocker.mock()
        brain1 = self.mocker.mock()
        self.expect(brain1.getPath()).result("/plone/brain1").count(0, None)
        self.expect(brain1.review_state).result("published").count(0, None)
        self.expect(brain1.portal_type).result("Document").count(0, None)
        self.expect(brain1.getIcon).result('Icon').count(0, None)
        self.expect(brain1.pretty_title_or_id()).result('brain1').count(0, None)
        self.expect(brain1.UID).result('1234').count(0, None)
        self.expect(brain1.getObject()).result(self.obj).count(0, None)

        brain2 = self.mocker.mock()
        self.expect(brain2.getPath()).result("/plone/brain2").count(0, None)
        self.expect(brain2.review_state).result("published").count(0, None)
        self.expect(brain2.portal_type).result("Document").count(0, None)
        self.expect(brain2.getIcon).result('Icon').count(0, None)
        self.expect(brain2.pretty_title_or_id()).result('brain2')
        self.expect(brain2.UID).result('2345')
        self.expect(brain2.getObject()).result(self.obj).count(0, None)

        brain3 = self.mocker.mock()
        self.expect(brain3.getPath()).result("/plone/brain1/brain3").count(0, None)
        self.expect(brain3.review_state).result("published").count(0, None)
        self.expect(brain3.portal_type).result("Discussion Item").count(0, None)
        self.expect(brain3.getIcon).result('Icon').count(0, None)
        self.expect(brain3.pretty_title_or_id()).result('brain3')
        self.expect(brain3.UID).result('3456')
        self.expect(brain3.getObject()).result(self.obj).count(0, None)

        self.brains = [brain1,brain2,brain3]

        self.context = self.mocker.mock()
        self.expect(self.context.getPhysicalPath()).result(("", "Plone")).count(0, None)

        self.cat = self.mocker.mock()
        self.expect(self.cat.searchResults(ANY)).result(self.brains).count(0, None)

    def test_getinfos(self):
        self.replay()

        result = getInfos(self.context, self.cat, self.wf_tool)

        self.assertEqual(result[0]['workflow'], 'simple_publication_workflow')
        self.assertEqual(result[1]['workflow'], 'simple_publication_workflow')
        self.assertEqual(result[2]['workflow'], 'one_state_workflow')

    def test_gettransitions(self):
        dicts = [
            {'path':'/plone/brain1',
             'review_state':'private',
             'type': 'Document',
             'workflow': 'simple_publication_workflow',
             },
            {'path':'/plone/brain2',
             'review_state':'published',
             'type': 'Document',
             'workflow': 'simple_publication_workflow',
             },
            {'path':'/plone/brain1/brain3',
             'review_state':'published',
             'type': 'Discussion Item',
             'workflow': 'one_state_workflow',
             }
        ]
        result = getTransitionsForItem(self.wf_tool, dicts)
        self.assertEqual(result[0]['transitions'], ['publish','submit'])
        self.assertEqual(result[1]['transitions'], ['retract','reject'])
        self.assertEqual(result[2]['transitions'], [])
