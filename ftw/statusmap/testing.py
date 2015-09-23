from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles, TEST_USER_ID, TEST_USER_NAME, login
from zope.configuration import xmlconfig


class FtwStatusmapLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ftw.statusmap
        xmlconfig.file('configure.zcml', ftw.statusmap,
                       context=configurationContext)

        # installProduct() is *only* necessary for packages outside
        # the Products.* namespace which are also declared as Zope 2
        # products, using <five:registerPackage /> in ZCML.

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
