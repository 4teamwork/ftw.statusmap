from ftw.statusmap import _
from ftw.statusmap.interfaces import IStatusMapFolderTree
from ftw.statusmap.utils import executeTransition
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.i18n import translate
from zope.publisher.browser import BrowserView
import json


class StatusMap(BrowserView):

    template = ViewPageTemplateFile("statusmap.pt")
    template_recursive = ViewPageTemplateFile('statusmap_recurse.pt')

    def __call__(self):
        if self.request.get('abort') or self.request.get('back'):
                return self.request.RESPONSE.redirect(
                    self.context.absolute_url())

        if self.request.get('form.submitted'):
            self.change_states()

        self.update()
        return self.template()

    def update(self):
        self.tree = IStatusMapFolderTree(self.context)
        self.nodes = self.tree()
        self.transitions = self.tree.get_possible_transitions()
        self.has_transitions = self.tree.has_transitions()

    def render_status_map(self):
        return self.template_recursive(
            nodes=self.nodes,
            level=0,
            has_transitions=self.has_transitions)

    def change_states(self):
        """Changes review_state of multiple selected nodes
        """
        transition = self.request.get('transition', '')
        comment = self.request.get('comment', '')
        uids = self.request.get('uids', [])

        if not transition:
            msg = _(u'msg_no_transtion', default=u"Please select a Transition")
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return
        if not uids:
            msg = _(u'msg_no_uids', default=u"Please select at least one Item")
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return

        executeTransition(transition, uids, comment)

        msg = _(u'msg_transition_successful',
                default=u"Transition executed successfully.")
        IStatusMessage(self.request).addStatusMessage(msg, type='info')

        return self.request.RESPONSE.redirect(
            self.context.absolute_url() + '/statusmap')

    def possible_transitions(self):
        """ Loads all possible transitions for each object in javascript
        """
        return "var possible_transitions = %s;" % json.dumps(
            self.tree.get_possible_transitions_for_uids())

    def get_transition_title(self, transition):
        def _translate(request, msgid):
            return translate(
                msgid=msgid,
                domain="plone",
                context=request).encode('utf-8')

        return '{0} - {1} => {2}'.format(
            _translate(self.request, transition.get('id')),
            _translate(self.request, transition.get('old_review_state')),
            _translate(self.request, transition.get('new_review_state')))

    def get_translated_type(self, portal_type):
        portal_types = getToolByName(self.context, 'portal_types')
        fti = portal_types.get(portal_type, None)

        msgid = fti and fti.title or portal_type
        domain = fti and getattr(fti, 'i18n_domain', 'plone') or 'plone'

        return translate(msgid=msgid, domain=domain,
                         context=self.request)
