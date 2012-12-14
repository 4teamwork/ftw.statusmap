def getTransitionsForItem(wf_tool, brains, dicts):
    for index, brain in enumerate(brains):
        obj = brain.getObject()
        actions = wf_tool.listActionInfos(object=obj)
        avail_actions = []
        for action in actions:
            if action['category'] == 'workflow':
                avail_actions.append([action['id'], action['title']])
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
        obj = context.reference_catalog.lookupObject(uid)
        wf_tool.doActionFor(obj, transition, comment=comment)


def getInfos(context, cat, wf_tool):
    path = '/'.join(context.getPhysicalPath())
    brains = cat.searchResults({'path': path})
    items = getBaseInfo(path, brains)
    items = getTransitionsForItem(wf_tool, brains, items)
    return items
