from django.utils.translation import gettext_lazy as _

from utilities.choices import ChoiceSet


__all__ = (
    "ZoneStatusChoices",
    "ZoneEPPStatusChoices",
)


class ZoneStatusChoices(ChoiceSet):
    key = "Zone.status"

    STATUS_ACTIVE = "active"
    STATUS_RESERVED = "reserved"
    STATUS_DEPRECATED = "deprecated"
    STATUS_PARKED = "parked"
    STATUS_DYNAMIC = "dynamic"

    CHOICES = [
        (STATUS_ACTIVE, _("Active"), "blue"),
        (STATUS_RESERVED, _("Reserved"), "cyan"),
        (STATUS_DEPRECATED, _("Deprecated"), "red"),
        (STATUS_PARKED, _("Parked"), "gray"),
        (STATUS_DYNAMIC, _("Dynamic"), "orange"),
    ]


class ZoneEPPStatusChoices(ChoiceSet):
    """
    Reflects the EPP status of a zone registered as a domain. See
    https://www.icann.org/resources/pages/epp-status-codes-2014-06-16-en
    for details.
    """

    key = "Zone.epp_status"

    EPP_STATUS_ADD_PERIOD = "addPeriod"
    EPP_STATUS_AUTO_RENEW_PERIOD = "autoRenewPeriod"
    EPP_STATUS_INACTIVE = "inactive"
    EPP_STATUS_OK = "ok"
    EPP_STATUS_PENDING_CREATE = "pendingCreate"
    EPP_STATUS_PENDING_DELETE = "pendingDelete"
    EPP_STATUS_PENDING_RENEW = "pendingRenew"
    EPP_STATUS_PENDING_RESTORE = "pendingRestore"
    EPP_STATUS_PENDING_TRANSFER = "pendingTransfer"
    EPP_STATUS_PENDING_UPDATE = "pendingUpdate"
    EPP_STATUS_REDEMPTION_PERIOD = "redemptionPeriod"
    EPP_STATUS_RENEW_PERIOD = "renewPeriod"
    EPP_STATUS_SERVER_DELETE_PROHIBITED = "serverDeleteProhibited"
    EPP_STATUS_SERVER_HOLD = "serverHold"
    EPP_STATUS_SERVER_RENER_PROHIBITED = "serverRenewProhibited"
    EPP_STATUS_SERVER_TRANSFER_PROHIBITED = "serverTransferProhibited"
    EPP_STATUS_SERVER_UPDATE_PROHIBITED = "serverUpdateProhibited"
    EPP_STATUS_TRANSFER_PERIOD = "transferPeriod"
    EPP_STATUS_CLIENT_DELETE_PROHIBITED = "clientDeleteProhibited"
    EPP_STATUS_CLIENT_HOLD = "clientHold"
    EPP_STATUS_CLIENT_RENEW_PROHIBITED = "clientRenewProhibited"
    EPP_STATUS_CLIENT_TRANSFER_PROHIBITED = "clientTransferProhibited"
    EPP_STATUS_CLIENT_UPDATE_PROHIBITED = "clientUpdateProhibited"

    CHOICES = [
        (EPP_STATUS_ADD_PERIOD, EPP_STATUS_ADD_PERIOD, "blue"),
        (EPP_STATUS_AUTO_RENEW_PERIOD, EPP_STATUS_AUTO_RENEW_PERIOD, "blue"),
        (EPP_STATUS_INACTIVE, EPP_STATUS_INACTIVE, "blue"),
        (EPP_STATUS_OK, EPP_STATUS_OK, "blue"),
        (EPP_STATUS_PENDING_CREATE, EPP_STATUS_PENDING_CREATE, "blue"),
        (EPP_STATUS_PENDING_DELETE, EPP_STATUS_PENDING_DELETE, "blue"),
        (EPP_STATUS_PENDING_RENEW, EPP_STATUS_PENDING_RENEW, "blue"),
        (EPP_STATUS_PENDING_RESTORE, EPP_STATUS_PENDING_RESTORE, "blue"),
        (EPP_STATUS_PENDING_TRANSFER, EPP_STATUS_PENDING_TRANSFER, "blue"),
        (EPP_STATUS_PENDING_UPDATE, EPP_STATUS_PENDING_UPDATE, "blue"),
        (EPP_STATUS_REDEMPTION_PERIOD, EPP_STATUS_REDEMPTION_PERIOD, "blue"),
        (EPP_STATUS_RENEW_PERIOD, EPP_STATUS_RENEW_PERIOD, "blue"),
        (
            EPP_STATUS_SERVER_DELETE_PROHIBITED,
            EPP_STATUS_SERVER_DELETE_PROHIBITED,
            "blue",
        ),
        (EPP_STATUS_SERVER_HOLD, EPP_STATUS_SERVER_HOLD, "blue"),
        (
            EPP_STATUS_SERVER_RENER_PROHIBITED,
            EPP_STATUS_SERVER_RENER_PROHIBITED,
            "blue",
        ),
        (
            EPP_STATUS_SERVER_TRANSFER_PROHIBITED,
            EPP_STATUS_SERVER_TRANSFER_PROHIBITED,
            "blue",
        ),
        (
            EPP_STATUS_SERVER_UPDATE_PROHIBITED,
            EPP_STATUS_SERVER_UPDATE_PROHIBITED,
            "blue",
        ),
        (EPP_STATUS_TRANSFER_PERIOD, EPP_STATUS_TRANSFER_PERIOD, "blue"),
        (
            EPP_STATUS_CLIENT_DELETE_PROHIBITED,
            EPP_STATUS_CLIENT_DELETE_PROHIBITED,
            "cyan",
        ),
        (EPP_STATUS_CLIENT_HOLD, EPP_STATUS_CLIENT_HOLD, "cyan"),
        (
            EPP_STATUS_CLIENT_RENEW_PROHIBITED,
            EPP_STATUS_CLIENT_RENEW_PROHIBITED,
            "cyan",
        ),
        (
            EPP_STATUS_CLIENT_TRANSFER_PROHIBITED,
            EPP_STATUS_CLIENT_TRANSFER_PROHIBITED,
            "cyan",
        ),
        (
            EPP_STATUS_CLIENT_UPDATE_PROHIBITED,
            EPP_STATUS_CLIENT_UPDATE_PROHIBITED,
            "cyan",
        ),
    ]
