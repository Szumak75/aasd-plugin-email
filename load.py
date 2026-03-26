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
            PluginConfigField(
                name=Keys.SMTP_SERVER,
                field_type=str,
                default="smtp.example.com",
                required=True,
                description="SMTP server hostname used to send notifications.",
                example="smtp.example.com",
            ),
            PluginConfigField(
                name=Keys.SMTP_USER,
                field_type=str,
                default="user@example.com",
                required=True,
                description="SMTP account username used for authentication.",
                example="user@example.com",
            ),
            PluginConfigField(
                name=Keys.SMTP_PASS,
                field_type=str,
                default="",
                required=True,
                description="SMTP account password used for authentication.",
                secret=True,
                example="change-me",
            ),
            PluginConfigField(
                name=Keys.ADDRESS_FROM,
                field_type=str,
                default="aasd@example.com",
                required=True,
                description="Sender email address used in notification messages.",
                example="aasd@example.com",
            ),
            PluginConfigField(
                name=Keys.ADDRESS_TO,
                field_type=list,
                default=["admin@example.com"],
                required=True,
                description="Recipient email address list used for notifications.",
                example=["admin@example.com", "ops@example.com"],
            ),
            PluginConfigField(
                name=Keys.FOOTER_TEMPLATE,
                field_type=str,
                default="hostmaster at {hostname}",
                required=False,
                description=(
                    "Optional footer template appended to outbound emails. "
                    "Use an empty string to disable it."
                ),
                example="hostmaster at {hostname}",
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
