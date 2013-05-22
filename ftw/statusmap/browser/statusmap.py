from ftw.statusmap import _
from ftw.statusmap.utils import executeTransition
from ftw.statusmap.utils import getInfos
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.i18n import translate
from zope.publisher.browser import BrowserView
import json


class StatusMap(BrowserView):

    template = ViewPageTemplateFile("statusmap.pt")

    def __init__(self, context, request):
        self.cat = None
        self.wf_tool = None
        self.infos = None
        super(StatusMap, self).__init__(context, request)

    def __call__(self):
        self.cat = getToolByName(self.context, 'portal_catalog')
        self.wf_tool = getToolByName(self.context, 'portal_workflow')
        self.infos = getInfos(self.context, self.cat, self.wf_tool)
        if self.request.get('form.submitted'):
            if self.request.get('abort') or self.request.get('back'):
                return self.request.RESPONSE.redirect(
                    self.context.absolute_url())
            self.change_states()
        return self.template()

    def change_states(self):
        transition = self.request.get('transition', '')
        comment = self.request.get('comment', '')
        uids = self.request.get('uids', [])
        error = False

        if not transition:
            msg = _(u'msg_no_transtion', default=u"Please select a Transition")
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            error = True
        if len(uids) == 0:
            msg = _(u'msg_no_uids', default=u"Please select at least one Item")
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            error = True
        if error:
            return
        executeTransition(
            self.context, self.wf_tool, transition, uids, comment)
        msg = _(u'msg_transition_successful',
                default=u"Transition executed successfully.")
        IStatusMessage(self.request).addStatusMessage(msg, type='Information')
        return self.request.RESPONSE.redirect(
            self.context.absolute_url() + '/statusmap')

    def list_transitions(self):
        transitions = []
        for item in self.infos:
            for transition in item.get('transitions'):
                if transition not in transitions:
                    transitions.append(transition)
        return transitions

    def get_json(self):
        result = {}
        for item in self.infos:
            result[item['uid']] = [transition[0]
                                   for transition in item['transitions']]
        return json.dumps(result)

    def get_allowed_transitions(self):
        return "var possible_transitions = %s;" % self.get_json()

    def get_translated_type(self, portal_type):
        portal_types = getToolByName(self.context, 'portal_types')
        fti = portal_types.get(portal_type, None)
        if fti is None or not fti.i18n_domain:
            domain = 'plone'
        else:
            domain = fti.i18n_domain

        return translate(msgid=portal_type, domain=domain,
                         context=self.request)
