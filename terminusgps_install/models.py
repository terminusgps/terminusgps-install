from django.contrib.auth import get_user_model
from django.db import models


class WialonAccount(models.Model):
    """
    A Wialon resource/account.

    `Wialon account reference <https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/account/account>`_

    """

    id = models.PositiveIntegerField(primary_key=True)
    """Wialon account id."""
    name = models.CharField(max_length=128)
    """Wialon account name."""


class WialonAsset(models.Model):
    """
    A Wialon unit.

    `Wialon unit reference <https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/unit/unit>`_

    """

    id = models.PositiveIntegerField(primary_key=True)
    """Wialon unit id."""
    name = models.CharField(max_length=128)
    """Wialon unit name."""
    account = models.ForeignKey(
        "terminusgps_install.WialonAccount",
        on_delete=models.CASCADE,
        related_name="assets",
    )


class Installer(models.Model):
    """
    A human that installs GPS tracking hardware into vehicles.

    `Wialon user reference <https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/user/user>`_

    """

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """A django user."""
    accounts = models.ManyToManyField(
        "terminusgps_install.WialonAccount",
        related_name="installers",
    )
    """Wialon accounts the installer has access to."""
