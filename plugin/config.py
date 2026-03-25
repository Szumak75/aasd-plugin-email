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
    STDOUT_PREFIX: str = "stdout_prefix"


# #[EOF]#######################################################################
