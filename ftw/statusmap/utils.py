from plone import api
from plone.app.uuid.utils import uuidToObject
from Products.CMFPlone.browser.navigation import get_view_url
import os.path


def getTransitionsForItem(wf_tool, brains, dicts):
    for index, brain in enumerate(brains):
        obj = brain.getObject()
        actions = wf_tool.listActionInfos(object=obj)
        avail_actions = []
        for action in actions:
            if action['category'] == 'workflow':
                avail_actions.append({
                    'id': action['id'],
                    'title': action['title'],
                    'old_review_state': brain.review_state,
                    'new_review_state': action.get('transition').new_state_id,
                    })
        dicts[index]['transitions'] = avail_actions
    return dicts


def getBaseInfo(base_path, brains):
    dicts = []
    for brain in brains:
        relative_path = brain.getPath()[len(base_path):]
        level = len(relative_path.split('/')) - 1
        dicts.append(
            {'path': brain.getPath(),
             'review_state': brain.review_state,
             'type': brain.portal_type,
             'level': level,
             'icon': brain.getIcon,
             'title': brain.pretty_title_or_id(),
             'brain': brain,
             'uid': brain.UID}
            )
    return dicts


def executeTransition(context, wf_tool, transition, uids, comment):
    for uid in uids:
        obj = uuidToObject(uid)
        wf_tool.doActionFor(obj, transition, comment=comment)


def getInfos(context, cat, wf_tool):
    path = '/'.join(context.getPhysicalPath())
    brains = cat.searchResults({'path': path, 'sort_on': 'path'})
    items = getBaseInfo(path, brains)
    items = getTransitionsForItem(wf_tool, brains, items)
    return items


class StatusMapFolderTree(object):

    def __init__(self, context):
        self.context = context
        self.wf_tool = api.portal.get_tool('portal_workflow')
        self.catalog = api.portal.get_tool('portal_catalog')
        self.portal_properties = api.portal.get_tool('portal_properties')

    def __call__(self):
        return self.generate_tree()

    def generate_tree(self):
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

    def _action_item(self, action):
        """Converts a workflow action object into
        an item
        """
        return dict(
            id=action['id'],
            title=action['title'],
            new_review_state=action.get('transition').new_state_id,
        )

    def _get_transitions_of_brain(self, brain):
        """Returns a dict of all possible workflowactions of the brains
        object

        TODO: This function makes it slow. We need the object.
        Perhaps we shouldn't render the whole tree?
        """
        obj = brain.getObject()
        actions = self.wf_tool.listActionInfos(object=obj)
        actions = filter(lambda x: x['category'] == 'workflow', actions)
        return map(self._action_item, actions)

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

        sort_attribute = navtree_properties.getProperty('sortAttribute', None)
        if sort_attribute is None:
            return

        query['sort_on'] = sort_attribute
        sort_order = navtree_properties.getProperty('sortOrder', None)

        if sort_order is not None:
            query['sort_order'] = sort_order
