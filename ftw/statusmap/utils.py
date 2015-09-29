from functools import partial
from plone import api
from plone.app.uuid.utils import uuidToObject
from Products.CMFPlone.browser.navigation import get_view_url
import os.path


def executeTransition(transition, uids, comment=''):
    wf_tool = api.portal.get_tool('portal_workflow')
    for uid in uids:
        obj = uuidToObject(uid)
        wf_tool.doActionFor(obj, transition, comment=comment)


class StatusMapFolderTree(object):

    def __init__(self, context):
        self.context = context
        self.wf_tool = api.portal.get_tool('portal_workflow')
        self.catalog = api.portal.get_tool('portal_catalog')
        self.portal_properties = api.portal.get_tool('portal_properties')

    def __call__(self):
        return self.get_tree()

    def get_tree(self):
        """Returns the generated tree
        """
        if not getattr(self, '_tree', None):
            setattr(self, '_tree', self._generate_tree())

        return getattr(self, '_tree')

    def has_transitions(self):
        """Checkt wheter there are possible transitions in the tree nodes
        """
        return bool(self.get_possible_transitions())

    def get_possible_transitions(self):
        """Returns all possible transitions of all nodes in the tree in a list

        [
            'transitionId1',
            'transitionId2',
        ]
        """
        def _get_transitions_recursive(result, node):
            for transition in node.get('transitions'):
                if transition not in result:
                    result.append(transition)

            map(partial(_get_transitions_recursive, result), node.get('nodes'))

        result = []
        map(partial(_get_transitions_recursive, result), self.get_tree())

        return result

    def get_possible_transitions_for_uids(self):
        """Returns all possible transitions for each node in a dict.

        key = UID of object
        value = list with possible transitions

        {
            'uid1': ['transitionId1', 'transitionId2'],
            'uid2': ['transitionId1', 'transitionId3'],
        }
        """
        def _get_transitions_recursive(result, node):
            result[node['uid']] = [t.get('id') for t in node['transitions']]
            map(partial(_get_transitions_recursive, result), node.get('nodes'))

        result = {}
        map(partial(_get_transitions_recursive, result), self.get_tree())

        return result

    def _generate_tree(self):
        """Generates a nested tree.
        - The root of the tree will be the context
        - The sorting is the plonenavigation sorting

        [{
        'url': '/foo'
        'nodes': [{
            'url': '/foo/bar'
            }]
        },
        'url': '/dummy'
        }]
        """
        nodes = map(self._node, self._brains())
        return self._make_tree_by_url(nodes)

    def _node(self, brain):
        """Converts a brain into a statusmap node
        """
        return dict(
            url=get_view_url(brain)[1],
            review_state=brain.review_state or '',
            type=brain.portal_type,
            icon=brain.getIcon,
            title=brain.pretty_title_or_id(),
            uid=brain.UID,
            transitions=self._get_transitions_of_brain(brain),
        )

    def _action_item(self, review_state, action):
        """Converts a workflow action object into
        an item
        """
        return dict(
            id=action['id'],
            title=action['title'],
            new_review_state=action.get('transition').new_state_id,
            old_review_state=review_state,
        )

    def _get_transitions_of_brain(self, brain):
        """Returns a dict of all possible workflowactions of the brains
        object
        """
        obj = brain.getObject()
        actions = self.wf_tool.listActionInfos(object=obj)
        actions = filter(lambda x: x['category'] == 'workflow', actions)

        return map(partial(self._action_item, brain.review_state), actions)

    def _make_tree_by_url(self, nodes):
        """Creates a nested tree of nodes from a flat list-like object of nodes.
        Each node is expected to be a dict with a url-like string stored
        under the key ``url``.
        Each node will end up with a ``nodes`` key, containing a list
        of children nodes.
        The nodes are changed in place, be sure to make copies first when
        necessary.
        """
        for node in nodes:
            node['nodes'] = []

        nodes_by_url = dict((node['url'], node) for node in nodes)
        root = []

        for node in nodes:
            parent_url = os.path.dirname(node['url'])
            if parent_url in nodes_by_url:
                nodes_by_url[parent_url]['nodes'].append(node)
            else:
                root.append(node)

        return root

    def _brains(self):
        return self.catalog.searchResults(self._query())

    def _query(self):
        query = {}

        self._extend_query_with_path(query)
        self._extend_query_with_sorting(query)

        return query

    def _extend_query_with_path(self, query):
        query['path'] = '/'.join(self.context.getPhysicalPath())

    def _extend_query_with_sorting(self, query):
        navtree_properties = getattr(
            self.portal_properties, 'navtree_properties')

        query['sort_on'] = navtree_properties.getProperty(
            'sortAttribute', 'getObjPositionInParent')

        query['sort_order'] = navtree_properties.getProperty(
            'sortOrder', 'asc')
