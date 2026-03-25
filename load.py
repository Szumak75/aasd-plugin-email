# -*- coding: UTF-8 -*-
"""
Email communication plugin entry point.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-24

Purpose: Provide the plugin manifest for the SMTP-based email communication
plugin.
"""

from libs.plugins import PluginCommonKeys, PluginKind, PluginSpec
from libs.templates import PluginConfigField, PluginConfigSchema

from .plugin import __version__
from .plugin.config import Keys
from .plugin.runtime import EmailRuntime


def get_plugin_spec() -> PluginSpec:
    """Return the plugin spec for the email communication plugin.

    ### Returns:
    PluginSpec - Plugin manifest.
    """
    schema = PluginConfigSchema(
        title="Email communication plugin.",
        description=(
            "SMTP-based communication plugin used to send notification "
            "messages by email."
        ),
        fields=[
            PluginConfigField(
                name=PluginCommonKeys.CHANNEL,
                field_type=int,
                default=1,
                required=True,
                description="Dispatcher channel consumed by the plugin.",
            ),
            PluginConfigField(
                name=Keys.STDOUT_PREFIX,
                field_type=str,
                default="[plugin-email]",
                required=True,
                description="Prefix added to runtime stdout diagnostic output.",
                example="[plugin-email]",
            ),
        ],
    )
    return PluginSpec(
        api_version=1,
        config_schema=schema,
        plugin_id="email.communication",
        plugin_kind=PluginKind.COMMUNICATION,
        plugin_name="plugin_email",
        runtime_factory=EmailRuntime,
        description="SMTP-based AASd communication plugin for email notifications.",
        plugin_version=__version__,
    )


# #[EOF]#######################################################################
