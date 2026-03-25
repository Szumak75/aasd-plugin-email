# -*- coding: UTF-8 -*-
"""
Email communication plugin configuration keys.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-24

Purpose: Provide plugin-specific configuration keys for the SMTP email
communication plugin.
"""

from jsktoolbox.attribtool import ReadOnlyClass


class Keys(object, metaclass=ReadOnlyClass):
    """Define plugin-specific configuration keys for email delivery."""

    # #[CONSTANTS]####################################################################
    ADDRESS_FROM: str = "address_from"
    ADDRESS_TO: str = "address_to"
    SMTP_PASS: str = "smtp_pass"
    SMTP_SERVER: str = "smtp_server"
    SMTP_USER: str = "smtp_user"
    STDOUT_PREFIX: str = "stdout_prefix"


# #[EOF]#######################################################################
