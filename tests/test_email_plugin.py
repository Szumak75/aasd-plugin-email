# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-25

Purpose: Provide unit coverage for the standalone email communication plugin.
"""

import unittest

from queue import Queue
from threading import Event
from typing import Dict, List, Tuple
from unittest.mock import MagicMock, patch

from jsktoolbox.configtool import Config as ConfigTool
from jsktoolbox.logstool import LoggerClient, LoggerQueue

from libs import AppName
from libs.com.message import Message, ThDispatcher
from libs.plugins import (
    DispatcherAdapter,
    PluginCommonKeys,
    PluginContext,
    PluginHealth,
    PluginKind,
    PluginState,
)
from plugins.email.load import get_plugin_spec
from plugins.email.plugin import __version__
from plugins.email.plugin.config import Keys
from plugins.email.plugin.runtime import EmailRuntime


class _FakeSmtpBase:
    """Base fake SMTP client used by email runtime tests."""

    instances: List["_FakeSmtpBase"] = []
    sent_messages: List[Dict[str, object]] = []
    starttls_ports: List[int] = []
    login_calls: List[Tuple[str, str, int]] = []

    def __init__(self, host: str, port: int, timeout: int, **kwargs) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.kwargs = kwargs
        type(self).instances.append(self)

    def __enter__(self) -> "_FakeSmtpBase":
        """Return the fake SMTP client context instance."""
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        """Close the fake context manager without suppressing exceptions."""
        return False

    def ehlo(self) -> None:
        """Simulate the EHLO command."""

    def login(self, user: str, password: str) -> None:
        """Record SMTP login parameters."""
        type(self).login_calls.append((user, password, self.port))

    def send_message(self, email_message, to_addrs=None) -> None:
        """Record the outgoing email message."""
        type(self).sent_messages.append(
            {
                "port": self.port,
                "subject": email_message["Subject"],
                "from": email_message["From"],
                "to": list(to_addrs or []),
                "reply_to": email_message.get("Reply-To"),
                "content_type": email_message.get_content_type(),
                "body": email_message.as_string(),
            }
        )

    @classmethod
    def reset(cls) -> None:
        """Clear accumulated fake SMTP call state."""
        cls.instances = []
        cls.sent_messages = []
        cls.starttls_ports = []
        cls.login_calls = []


class _FakeSMTP(_FakeSmtpBase):
    """Fake SMTP client used for plain or STARTTLS connections."""

    failure_ports: Dict[int, Exception] = {}

    def __init__(self, host: str, port: int, timeout: int, **kwargs) -> None:
        failure = type(self).failure_ports.get(port)
        if failure is not None:
            raise failure
        super().__init__(host=host, port=port, timeout=timeout, **kwargs)

    def starttls(self) -> None:
        """Record the STARTTLS negotiation."""
        type(self).starttls_ports.append(self.port)

    @classmethod
    def reset(cls) -> None:
        """Clear accumulated fake SMTP call state and configured failures."""
        super().reset()
        cls.failure_ports = {}


class _FakeSMTPSSL(_FakeSmtpBase):
    """Fake SMTP SSL client used for implicit TLS connections."""

    failure_ports: Dict[int, Exception] = {}

    def __init__(self, host: str, port: int, timeout: int, **kwargs) -> None:
        failure = type(self).failure_ports.get(port)
        if failure is not None:
            raise failure
        super().__init__(host=host, port=port, timeout=timeout, **kwargs)

    @classmethod
    def reset(cls) -> None:
        """Clear accumulated fake SMTP SSL call state and configured failures."""
        super().reset()
        cls.failure_ports = {}


class _ControlledEvent(Event):
    """Event with deterministic `is_set()` answers for runtime loop tests."""

    def __init__(self, states: List[bool]) -> None:
        """Initialize the controlled event state sequence.

        ### Arguments:
        * states: List[bool] - Sequential values returned by `is_set()`.
        """
        super().__init__()
        self._states = list(states)

    def is_set(self) -> bool:
        """Return the next configured event state."""
        if self._states:
            return self._states.pop(0)
        return True


class TestEmailPlugin(unittest.TestCase):
    """Provide unit coverage for the email communication plugin."""

    # #[CONSTRUCTOR]##################################################################
    def setUp(self) -> None:
        """Reset fake SMTP state before each test."""
        _FakeSMTP.reset()
        _FakeSMTPSSL.reset()
        EmailRuntime._REMEMBERED_PORT = None

    # #[PRIVATE METHODS]###############################################################
    def __build_context(self, smtp_server: str = "smtp.example.com") -> PluginContext:
        """Build a minimal runtime context for the email plugin.

        ### Arguments:
        * smtp_server: str - SMTP endpoint definition.

        ### Returns:
        PluginContext - Minimal context object accepted by the runtime factory.
        """
        qlog = LoggerQueue()
        qcom: Queue = Queue()
        dispatcher = ThDispatcher(
            qlog=qlog,
            qcom=qcom,
            debug=False,
            verbose=False,
        )
        adapter = DispatcherAdapter(qcom=qcom, dispatcher=dispatcher)
        config_handler = MagicMock(spec=ConfigTool)
        config_handler.get.return_value = 6
        return PluginContext(
            app_meta=AppName(app_name="AASd", app_version="0.0.0-TEST"),
            config={
                PluginCommonKeys.CHANNEL: 1,
                Keys.ADDRESS_FROM: "sender@example.com",
                Keys.ADDRESS_TO: ["admin@example.com", "ops@example.com"],
                Keys.SMTP_PASS: "encoded-secret",
                Keys.SMTP_SERVER: smtp_server,
                Keys.SMTP_USER: "mailer@example.com",
                Keys.STDOUT_PREFIX: "[plugin-email]",
            },
            config_handler=config_handler,
            debug=False,
            dispatcher=adapter,
            instance_name="email-test",
            logger=LoggerClient(queue=qlog, name="email-test"),
            plugin_id="email.communication",
            plugin_kind=PluginKind.COMMUNICATION,
            qlog=qlog,
            verbose=False,
        )

    # #[PUBLIC METHODS]################################################################
    def test_01_plugin_spec_should_expose_expected_manifest(self) -> None:
        """Expose the expected plugin manifest and schema fields."""
        spec = get_plugin_spec()

        field_names = [field.name for field in spec.config_schema.fields]

        self.assertEqual(spec.plugin_id, "email.communication")
        self.assertEqual(spec.plugin_kind, PluginKind.COMMUNICATION)
        self.assertEqual(spec.plugin_name, "plugin_email")
        self.assertEqual(spec.plugin_version, __version__)
        self.assertIs(spec.runtime_factory, EmailRuntime)
        self.assertEqual(
            field_names,
            [
                PluginCommonKeys.CHANNEL,
                Keys.STDOUT_PREFIX,
                Keys.SMTP_SERVER,
                Keys.SMTP_USER,
                Keys.SMTP_PASS,
                Keys.ADDRESS_FROM,
                Keys.ADDRESS_TO,
            ],
        )

    def test_02_config_keys_should_expose_expected_constants(self) -> None:
        """Expose the expected plugin-local configuration key names."""
        self.assertEqual(Keys.STDOUT_PREFIX, "stdout_prefix")
        self.assertEqual(Keys.SMTP_SERVER, "smtp_server")
        self.assertEqual(Keys.SMTP_USER, "smtp_user")
        self.assertEqual(Keys.SMTP_PASS, "smtp_pass")
        self.assertEqual(Keys.ADDRESS_FROM, "address_from")
        self.assertEqual(Keys.ADDRESS_TO, "address_to")

    @patch("plugins.email.plugin.runtime.smtplib.SMTP_SSL", new=_FakeSMTPSSL)
    @patch("plugins.email.plugin.runtime.smtplib.SMTP", new=_FakeSMTP)
    @patch("plugins.email.plugin.runtime.SimpleCrypto.multiple_decrypt")
    def test_03_runtime_should_send_via_explicit_port_and_decode_password(
        self,
        decrypt_mock: MagicMock,
    ) -> None:
        """Use the configured explicit port and decode the stored password."""
        decrypt_mock.return_value = "decoded-secret"
        context = self.__build_context("smtp.example.com:2525")
        runtime = EmailRuntime(context)
        message = Message()
        message.subject = "explicit-port"
        message.messages = ["hello"]

        runtime._EmailRuntime__send_message(context=context, message=message)

        self.assertEqual(_FakeSMTP.sent_messages[0]["port"], 2525)
        self.assertEqual(
            _FakeSMTP.login_calls[0],
            ("mailer@example.com", "decoded-secret", 2525),
        )
        decrypt_mock.assert_called_once_with(6, "encoded-secret")
        self.assertEqual(EmailRuntime._REMEMBERED_PORT, 2525)

    @patch("plugins.email.plugin.runtime.smtplib.SMTP_SSL", new=_FakeSMTPSSL)
    @patch("plugins.email.plugin.runtime.smtplib.SMTP", new=_FakeSMTP)
    @patch("plugins.email.plugin.runtime.SimpleCrypto.multiple_decrypt")
    def test_04_runtime_should_fail_over_ports_and_remember_successful_one(
        self,
        decrypt_mock: MagicMock,
    ) -> None:
        """Try default ports in order and remember the first successful port."""
        decrypt_mock.return_value = "decoded-secret"
        _FakeSMTP.failure_ports[587] = ConnectionRefusedError("587 down")
        context = self.__build_context("smtp.example.com")
        runtime = EmailRuntime(context)
        message = Message()
        message.subject = "failover"
        message.messages = ["hello"]

        runtime._EmailRuntime__send_message(context=context, message=message)

        self.assertEqual(_FakeSMTPSSL.sent_messages[0]["port"], 465)
        self.assertEqual(EmailRuntime._REMEMBERED_PORT, 465)

        _FakeSMTP.reset()
        _FakeSMTPSSL.reset()
        runtime._EmailRuntime__send_message(context=context, message=message)

        self.assertEqual(_FakeSMTPSSL.sent_messages[0]["port"], 465)

    @patch("plugins.email.plugin.runtime.smtplib.SMTP_SSL", new=_FakeSMTPSSL)
    @patch("plugins.email.plugin.runtime.smtplib.SMTP", new=_FakeSMTP)
    @patch("plugins.email.plugin.runtime.SimpleCrypto.multiple_decrypt")
    def test_05_runtime_should_use_starttls_and_login_on_port_587(
        self,
        decrypt_mock: MagicMock,
    ) -> None:
        """Negotiate STARTTLS and authenticate when port 587 is used."""
        decrypt_mock.return_value = "decoded-secret"
        context = self.__build_context("smtp.example.com")
        runtime = EmailRuntime(context)
        message = Message()
        message.subject = "tls"
        message.messages = ["hello"]

        runtime._EmailRuntime__send_message(context=context, message=message)

        self.assertIn(587, _FakeSMTP.starttls_ports)
        self.assertEqual(
            _FakeSMTP.login_calls[0],
            ("mailer@example.com", "decoded-secret", 587),
        )

    @patch("plugins.email.plugin.runtime.smtplib.SMTP_SSL", new=_FakeSMTPSSL)
    @patch("plugins.email.plugin.runtime.smtplib.SMTP", new=_FakeSMTP)
    @patch("plugins.email.plugin.runtime.SimpleCrypto.multiple_decrypt")
    def test_06_runtime_should_fall_back_to_configured_recipients(
        self,
        decrypt_mock: MagicMock,
    ) -> None:
        """Use `address_to` when the message does not define recipients."""
        decrypt_mock.return_value = "decoded-secret"
        context = self.__build_context("smtp.example.com:25")
        runtime = EmailRuntime(context)
        message = Message()
        message.subject = "recipients"
        message.messages = ["hello"]

        runtime._EmailRuntime__send_message(context=context, message=message)

        self.assertEqual(
            _FakeSMTP.sent_messages[0]["to"],
            ["admin@example.com", "ops@example.com"],
        )

    @patch("plugins.email.plugin.runtime.smtplib.SMTP_SSL", new=_FakeSMTPSSL)
    @patch("plugins.email.plugin.runtime.smtplib.SMTP", new=_FakeSMTP)
    def test_07_runtime_run_should_mark_health_unhealthy_on_delivery_error(
        self,
    ) -> None:
        """Record runtime delivery errors in the health and state snapshots."""
        _FakeSMTP.failure_ports[587] = ConnectionRefusedError("587 down")
        _FakeSMTP.failure_ports[25] = ConnectionRefusedError("25 down")
        _FakeSMTPSSL.failure_ports[465] = ConnectionRefusedError("465 down")
        context = self.__build_context("smtp.example.com")
        runtime = EmailRuntime(context)
        runtime.initialize()
        message = Message()
        message.subject = "broken"
        message.messages = ["hello"]
        runtime._stop_event = _ControlledEvent([False, True])
        runtime._queue.put(message)

        runtime.run()

        self.assertEqual(runtime.health().health, PluginHealth.UNHEALTHY)
        self.assertEqual(runtime.state().state, PluginState.STOPPED)
        self.assertIn("Email delivery failed", str(runtime.health().message))


# #[EOF]#######################################################################
