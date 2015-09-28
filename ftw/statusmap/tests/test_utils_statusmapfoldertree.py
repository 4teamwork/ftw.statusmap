from ftw.builder import Builder
from ftw.builder import create
from ftw.statusmap.interfaces import IStatusMapFolderTree
from ftw.statusmap.testing import FTW_STATUSMAP_FUNCTIONAL_TESTING
from unittest2 import TestCase
from plone import api


class TestStatusMapFolderTree(TestCase):

    layer = FTW_STATUSMAP_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_tree_on_empty_folder(self):
        folder = create(Builder('folder'))
        tree = IStatusMapFolderTree(folder)()

        self.assertEqual(
            1, len(tree),
            "There should be only one root element")

        self.assertEqual(
            folder.absolute_url(), tree[0].get('url'),
            "The root element should be the 'folder' at {0}".format(
                folder.absolute_url()))

    def test_tree_with_child_elements(self):
        folder = create(Builder('folder'))

        child1 = create(Builder('folder').within(folder))
        child1_child = create(Builder('folder').within(child1))

        child2 = create(Builder('folder').within(folder))

        tree = IStatusMapFolderTree(folder)()

        self.assertEqual(
            1, len(tree),
            "There should be only one root element")

        children = tree[0].get('nodes')

        self.assertEqual(
            2, len(children),
            "There should be two child nodes at: {0}, {1}".format(
                child1.absolute_url(), child2.absolute_url()))

        children_of_child_1 = children[0].get('nodes')

        self.assertEqual(
            1, len(children_of_child_1),
            "The child 1 should have one child nodes at {0}".format(
                child1_child.absolute_url()))

        children_of_child_2 = children[1].get('nodes')

        self.assertEqual(
            0, len(children_of_child_2),
            "The child 2 should have no child nodes")

    def test_sorting_throught_navtree_properties(self):
        folder = create(Builder('folder'))

        create(Builder('folder')
               .within(folder)
               .titled("Chuck"))

        bond = create(Builder('folder')
                      .within(folder)
                      .titled("Bond"))

        create(Builder('folder')
               .within(bond)
               .titled("Weapons"))

        create(Builder('folder')
               .within(bond)
               .titled("Gadgets"))

        p_tool = api.portal.get_tool('portal_properties')
        navtree_properties = getattr(p_tool, 'navtree_properties')

        setattr(navtree_properties, 'sortAttribute', 'sortable_title')

        tree = IStatusMapFolderTree(folder)()

        # 1st Level
        level1 = tree[0].get('nodes')
        self.assertEqual(
            ['Bond', 'Chuck'], [node.get('title') for node in level1],
            'The Element should be sorted by title')

        # 2nd Level
        level2 = tree[0].get('nodes')[0].get('nodes')
        self.assertEqual(
            ['Gadgets', 'Weapons'], [node.get('title') for node in level2],
            'The Element should be sorted by title')

    def test_empty_review_state_if_no_wf_is_defined(self):
        wf_tool = api.portal.get_tool('portal_workflow')
        wf_tool.setDefaultChain('')

        folder = create(Builder('folder'))

        tree = IStatusMapFolderTree(folder)()

        self.assertEqual(
            '', tree[0].get('review_state'),
            "The reviewstate should be an empty string if "
            "no worfklow is defined"
            )

    def test_show_possible_transitions_if_wf_is_defined(self):
            wf_tool = api.portal.get_tool('portal_workflow')
            wf_tool.setDefaultChain('simple_publication_workflow')

            folder = create(Builder('folder'))

            tree = IStatusMapFolderTree(folder)()
            self.assertEqual(
                'private', tree[0].get('review_state'),
                "The initialstate should be 'private'")

            self.assertEqual(
                ['publish', 'submit'],
                [action.get('id') for action in tree[0].get('transitions')],
                "Only possible actions from the initialstate should be listed"
                )
