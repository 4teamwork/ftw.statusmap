from ftw.upgrade import UpgradeStep


class UpdateAction(UpgradeStep):
    """Update action.
    """

    def __call__(self):
        self.install_upgrade_profile()
