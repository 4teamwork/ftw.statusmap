from ftw.statusmap.interfaces import IConstraintChecker
from plone.app.uuid.utils import uuidToObject
from zope.component import getUtilitiesFor


def getTransitionsForItem(wf_tool, brains, dicts):
    for index, brain in enumerate(brains):
        obj = brain.getObject()
        actions = wf_tool.listActionInfos(object=obj)
        old_review_state_title = ''
        avail_actions = []
        for action in actions:
            if action['category'] == 'workflow':
                transition = action.get('transition')

                # Construct a dict where the key is the id of the state
                # and its value is the human readable title of the state.
                review_state_titles = {}
                for state in transition.states.items():
                    review_state_titles[state[0]] = state[1].title

                old_review_state_title = review_state_titles[brain.review_state]

                avail_actions.append(
                    {
                        'id': action['id'],
                        'title': action['title'],
                        'old_review_state': old_review_state_title,
                        'new_review_state': review_state_titles[
                            action.get('transition').new_state_id
                        ],
                    }
                )
        dicts[index]['review_state'] = old_review_state_title
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

        if not is_transition_allowed(obj, transition):
            continue

        wf_tool.doActionFor(obj, transition, comment=comment)


def getInfos(context, cat, wf_tool):
    path = '/'.join(context.getPhysicalPath())
    brains = cat.searchResults({'path': path, 'sort_on': 'path'})
    items = getBaseInfo(path, brains)
    items = getTransitionsForItem(wf_tool, brains, items)
    return items


def is_transition_allowed(obj, transition):
    for name, checker in getUtilitiesFor(IConstraintChecker):
        if not checker.is_transition_allowed(obj, transition):
            return False

    return True
