from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from zope.configuration import xmlconfig


class FtwStatusmapLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.statusmap:default')

        setRoles(portal, TEST_USER_ID, ['Manager', 'Contributor'])
        login(portal, TEST_USER_NAME)


FTW_STATUSMAP_FIXTURE = FtwStatusmapLayer()
FTW_STATUSMAP_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_STATUSMAP_FIXTURE, ), name="FtwStatusmap:Integration")
FTW_STATUSMAP_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(
        FTW_STATUSMAP_FIXTURE,
        set_builder_session_factory(functional_session_factory)),
    name="FtwStatusmap:Functional")


class FtwStatusmapPublisherLayer(FtwStatusmapLayer):

    def setUpPloneSite(self, portal):
        super(FtwStatusmapPublisherLayer, self).setUpPloneSite(portal)
        applyProfile(portal, 'ftw.publisher.sender:default')
        applyProfile(portal, 'ftw.publisher.sender:example-workflow')


FTW_STATUSMAP_PUBLISHER_FIXTURE = FtwStatusmapPublisherLayer()
FTW_STATUSMAP_PUBLISHER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_STATUSMAP_PUBLISHER_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.statusmap publisher:functional")
