from zope.interface import Interface


class IStatusMapFolderTree(Interface):
    """ Generates a statusmap tree based on the context.

    It returns a dict with items and its nodes:

    [{
        'url': '/foo'
        'nodes': [{
            'url': '/foo/bar'
            }]
        },
        'url': '/dummy'
    }]

    - The root object is the given context
    - The sorting is given trough the navtree-properties
    - The depth is unlimited

    """
