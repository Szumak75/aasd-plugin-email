# -*- coding: UTF-8 -*-
"""
Email communication plugin runtime.

Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2026-03-24

Purpose: Provide the thread-based runtime used by the SMTP email
communication plugin.
"""

import time
import smtplib
import ssl

from email.message import EmailMessage
from queue import Empty, Queue
from threading import Event, Thread
from typing import Any, Dict, List, Optional, Tuple

from jsktoolbox.stringtool import SimpleCrypto
from libs.com.message import Message, Multipart
from libs.plugins import (
    PluginCommonKeys,
    PluginContext,
    PluginHealth,
    PluginHealthSnapshot,
    PluginState,
    PluginStateSnapshot,
    ThPluginMixin,
)

from .config import Keys


class EmailRuntime(Thread, ThPluginMixin):
    """Provide the runtime responsible for email notification delivery."""

    # #[CONSTANTS]####################################################################
    _DEFAULT_PORTS: List[int] = [587, 465, 25]
    _REMEMBERED_PORT: Optional[int] = None

    # #[CONSTRUCTOR]##################################################################
    def __init__(self, context: PluginContext) -> None:
        """Initialize the email communication runtime.

        ### Arguments:
        * context: PluginContext - Plugin runtime context.
        """
        Thread.__init__(self, name=context.instance_name)
        self.daemon = True
        self._context = context
        self._health = PluginHealthSnapshot(health=PluginHealth.UNKNOWN)
        self._queue = None
        self._state = PluginStateSnapshot(state=PluginState.CREATED)
        self._stop_event = Event()

    # #[PUBLIC METHODS]################################################################
    def health(self) -> PluginHealthSnapshot:
        """Return the current health snapshot.

        ### Returns:
        PluginHealthSnapshot - Current plugin health snapshot.
        """
        health: Optional[PluginHealthSnapshot] = self._health
        if health is None:
            return PluginHealthSnapshot(
                health=PluginHealth.UNKNOWN,
                message="Health snapshot is not initialized.",
            )
        return health

    def initialize(self) -> None:
        """Prepare the runtime before startup."""
        context: Optional[PluginContext] = self._context
        if context is None:
            self._health = PluginHealthSnapshot(
                health=PluginHealth.UNHEALTHY,
                last_error_at=int(time.time()),
                message="Plugin context is not initialized.",
            )
            self._state = PluginStateSnapshot(
                state=PluginState.FAILED,
                failure_count=1,
                message="Plugin context is not initialized.",
                stopped_at=int(time.time()),
            )
            return None
        self._queue = context.dispatcher.register_consumer(
            int(context.config[PluginCommonKeys.CHANNEL])
        )
        self._state = PluginStateSnapshot(state=PluginState.INITIALIZED)

    def run(self) -> None:
        """Consume messages from the configured dispatcher channel."""
        stop_event: Optional[Event] = self._stop_event
        if stop_event is None:
            self._health = PluginHealthSnapshot(
                health=PluginHealth.UNHEALTHY,
                last_error_at=int(time.time()),
                message="Stop event is not initialized.",
            )
            self._state = PluginStateSnapshot(
                state=PluginState.FAILED,
                failure_count=1,
                message="Stop event is not initialized.",
                stopped_at=int(time.time()),
            )
            return None
        queue: Optional[Queue] = self._queue
        if queue is None:
            self._health = PluginHealthSnapshot(
                health=PluginHealth.UNHEALTHY,
                last_error_at=int(time.time()),
                message="Consumer queue is not initialized.",
            )
            self._state = PluginStateSnapshot(
                state=PluginState.FAILED,
                failure_count=1,
                message="Consumer queue is not initialized.",
                stopped_at=int(time.time()),
            )
            return None
        context: Optional[PluginContext] = self._context
        if context is None:
            self._health = PluginHealthSnapshot(
                health=PluginHealth.UNHEALTHY,
                last_error_at=int(time.time()),
                message="Plugin context is not initialized.",
            )
            self._state = PluginStateSnapshot(
                state=PluginState.FAILED,
                failure_count=1,
                message="Plugin context is not initialized.",
                stopped_at=int(time.time()),
            )
            return None
        while not stop_event.is_set():
            task_received = False
            try:
                message: Message = queue.get(block=True, timeout=0.1)
                task_received = True
                self.__send_message(context=context, message=message)
                now = int(time.time())
                context.logger.message_info = (
                    f"Email notification sent from channel "
                    f"{context.config[PluginCommonKeys.CHANNEL]}"
                )
                self._health = PluginHealthSnapshot(
                    health=PluginHealth.HEALTHY,
                    last_ok_at=now,
                    message="Email notification sent successfully.",
                )
            except Empty:
                time.sleep(0.05)
            except Exception as ex:
                now = int(time.time())
                context.logger.message_error = f"Email delivery failed: {ex}"
                self._health = PluginHealthSnapshot(
                    health=PluginHealth.UNHEALTHY,
                    last_error_at=now,
                    message=f"Email delivery failed: {ex}",
                )
                state = self._state
                self._state = PluginStateSnapshot(
                    state=PluginState.RUNNING,
                    failure_count=(
                        (state.failure_count if state is not None else 0) + 1
                    ),
                    message=f"Email delivery failed: {ex}",
                    started_at=state.started_at if state is not None else now,
                )
            finally:
                if task_received:
                    queue.task_done()
        state: Optional[PluginStateSnapshot] = self._state
        self._state = PluginStateSnapshot(
            state=PluginState.STOPPED,
            started_at=state.started_at if state is not None else None,
            stopped_at=int(time.time()),
        )

    def start(self) -> None:
        """Start the runtime thread."""
        self._state = PluginStateSnapshot(
            state=PluginState.STARTING,
            started_at=int(time.time()),
        )
        Thread.start(self)

    def state(self) -> PluginStateSnapshot:
        """Return the current lifecycle snapshot.

        ### Returns:
        PluginStateSnapshot - Current plugin lifecycle snapshot.
        """
        state: Optional[PluginStateSnapshot] = self._state
        if state is None:
            return PluginStateSnapshot(
                state=PluginState.FAILED,
                failure_count=1,
                message="Lifecycle snapshot is not initialized.",
            )
        if self.is_alive() and state.state == PluginState.STARTING:
            state = PluginStateSnapshot(
                state=PluginState.RUNNING,
                started_at=state.started_at,
            )
            self._state = state
        return state

    def stop(self, timeout: Optional[float] = None) -> None:
        """Request plugin shutdown.

        ### Arguments:
        * timeout: Optional[float] - Optional join timeout.
        """
        stop_event: Optional[Event] = self._stop_event
        if stop_event is None:
            self._health = PluginHealthSnapshot(
                health=PluginHealth.UNHEALTHY,
                last_error_at=int(time.time()),
                message="Stop event is not initialized.",
            )
            self._state = PluginStateSnapshot(
                state=PluginState.FAILED,
                failure_count=1,
                message="Stop event is not initialized.",
                stopped_at=int(time.time()),
            )
            return None
        state: Optional[PluginStateSnapshot] = self._state
        if state is None:
            self._state = PluginStateSnapshot(
                state=PluginState.FAILED,
                failure_count=1,
                message="Lifecycle snapshot is not initialized.",
                stopped_at=int(time.time()),
            )
            return None
        if state.state not in (PluginState.STOPPED, PluginState.FAILED):
            self._state = PluginStateSnapshot(
                state=PluginState.STOPPING,
                started_at=state.started_at,
            )
        stop_event.set()
        if self.is_alive():
            self.join(timeout=timeout)
        state = self._state
        self._state = PluginStateSnapshot(
            state=PluginState.STOPPED,
            started_at=state.started_at if state is not None else None,
            stopped_at=int(time.time()),
        )

    # #[PRIVATE METHODS]###############################################################
    def __build_body(self, message: Message) -> str:
        """Build the plain-text email body from the message container.

        ### Arguments:
        * message: Message - Message container consumed by the plugin.

        ### Returns:
        str - Plain-text message body.
        """
        body_parts: List[str] = [str(item) for item in message.messages if str(item)]
        if message.footer:
            body_parts.append(str(message.footer))
        return "\n".join(body_parts).strip()

    def __build_email_message(
        self, context: PluginContext, message: Message
    ) -> Tuple[EmailMessage, List[str]]:
        """Build an `EmailMessage` instance from the plugin message payload.

        ### Arguments:
        * context: PluginContext - Plugin runtime context.
        * message: Message - Message container consumed by the plugin.

        ### Returns:
        Tuple[EmailMessage, List[str]] - Built email message and recipient list.
        """
        email_message = EmailMessage()
        sender = str(message.sender or context.config[Keys.ADDRESS_FROM])
        recipients = self.__get_recipients(context=context, message=message)
        subject = (
            str(message.subject)
            if message.subject
            else f"[{context.app_meta.app_name}:{context.instance_name}] notification"
        )
        body = self.__build_body(message=message)
        multipart: Optional[Dict[str, Any]] = message.mmessages

        email_message["From"] = sender
        email_message["To"] = ", ".join(recipients)
        email_message["Subject"] = subject
        if message.reply_to:
            email_message["Reply-To"] = str(message.reply_to)

        if multipart is not None and Multipart.PLAIN in multipart:
            email_message.set_content(str(multipart[Multipart.PLAIN]))
        else:
            email_message.set_content(body)

        if multipart is not None and Multipart.HTML in multipart:
            email_message.add_alternative(
                str(multipart[Multipart.HTML]), subtype="html"
            )

        return email_message, recipients

    def __get_recipients(self, context: PluginContext, message: Message) -> List[str]:
        """Return the final recipient list for the outbound email.

        ### Arguments:
        * context: PluginContext - Plugin runtime context.
        * message: Message - Message container consumed by the plugin.

        ### Returns:
        List[str] - Recipient email addresses.

        ### Raises:
        * ValueError: If no recipients are configured for the message.
        """
        recipients: List[str] = []
        raw_recipients = message.to

        if isinstance(raw_recipients, str):
            recipients = [raw_recipients]
        elif isinstance(raw_recipients, list):
            recipients = [str(item) for item in raw_recipients if str(item)]
        else:
            config_recipients = context.config[Keys.ADDRESS_TO]
            if isinstance(config_recipients, list):
                recipients = [str(item) for item in config_recipients if str(item)]

        if not recipients:
            raise ValueError("Recipient list is empty.")
        return recipients

    def __send_message(self, context: PluginContext, message: Message) -> None:
        """Deliver one message through the configured SMTP server.

        ### Arguments:
        * context: PluginContext - Plugin runtime context.
        * message: Message - Message container consumed by the plugin.
        """
        email_message, recipients = self.__build_email_message(
            context=context,
            message=message,
        )
        host, configured_port = self.__smtp_endpoint(
            str(context.config[Keys.SMTP_SERVER])
        )
        smtp_user = str(context.config[Keys.SMTP_USER])
        smtp_pass = self.__smtp_password(context=context)
        prefix = str(context.config[Keys.STDOUT_PREFIX])
        ports = self.__smtp_ports(configured_port=configured_port)
        last_error: Exception | None = None

        for port in ports:
            try:
                self.__send_via_port(
                    host=host,
                    port=port,
                    smtp_user=smtp_user,
                    smtp_pass=smtp_pass,
                    email_message=email_message,
                    recipients=recipients,
                )
                type(self)._REMEMBERED_PORT = port
                break
            except Exception as ex:
                last_error = ex
                context.logger.message_warning = (
                    f"SMTP delivery attempt via {host}:{port} failed: {ex}"
                )
        else:
            raise RuntimeError(
                f"All SMTP delivery attempts failed for host '{host}'. Last error: {last_error}"
            )

        print(
            f"{prefix} subject={email_message['Subject']} recipients={recipients}",
            flush=True,
        )

    def __smtp_endpoint(self, server: str) -> Tuple[str, int]:
        """Parse the configured SMTP server definition.

        ### Arguments:
        * server: str - SMTP endpoint in `host` or `host:port` form.

        ### Returns:
        Tuple[str, int] - SMTP host and port pair.
        """
        if ":" not in server:
            return server, 0
        host, port = server.rsplit(":", 1)
        return host, int(port)

    def __smtp_password(self, context: PluginContext) -> str:
        """Return the decoded SMTP password from plugin configuration.

        ### Arguments:
        * context: PluginContext - Plugin runtime context.

        ### Returns:
        str - Decoded SMTP password.
        """
        raw_password = str(context.config[Keys.SMTP_PASS])
        main_section = context.app_meta.app_name.lower()
        salt: int = context.config_handler.get(main_section, "salt")
        if salt is None:
            return raw_password
        if not isinstance(salt, int):
            context.logger.message_warning = (
                f"Invalid salt value '{salt}' in configuration. "
                f"Salt should be a numeric value. Using raw password without decryption."
            )
            return raw_password
        return str(SimpleCrypto.multiple_decrypt(salt, raw_password))

    def __smtp_ports(self, configured_port: int) -> List[int]:
        """Return the ordered list of SMTP ports to try for the next delivery.

        ### Arguments:
        * configured_port: int - Explicit SMTP port from configuration or `0`.

        ### Returns:
        List[int] - Ordered SMTP ports for connection attempts.
        """
        if configured_port > 0:
            return [configured_port]

        ports: List[int] = []
        remembered_port = type(self)._REMEMBERED_PORT
        if remembered_port is not None:
            ports.append(remembered_port)
        for port in self._DEFAULT_PORTS:
            if port not in ports:
                ports.append(port)
        return ports

    def __send_via_port(
        self,
        host: str,
        port: int,
        smtp_user: str,
        smtp_pass: str,
        email_message: EmailMessage,
        recipients: List[str],
    ) -> None:
        """Send one email using a single SMTP backend configuration.

        ### Arguments:
        * host: str - SMTP host name.
        * port: int - SMTP port.
        * smtp_user: str - SMTP username.
        * smtp_pass: str - Decoded SMTP password.
        * email_message: EmailMessage - Prepared email message.
        * recipients: List[str] - Recipient list.
        """
        if port == 465:
            with smtplib.SMTP_SSL(
                host=host,
                port=port,
                timeout=15,
                context=ssl.create_default_context(),
            ) as client:
                client.ehlo()
                if smtp_user:
                    client.login(smtp_user, smtp_pass)
                client.send_message(email_message, to_addrs=recipients)
            return

        with smtplib.SMTP(host=host, port=port, timeout=15) as client:
            client.ehlo()
            if port == 587:
                client.starttls()
                client.ehlo()
            if port != 25 and smtp_user:
                client.login(smtp_user, smtp_pass)
            client.send_message(email_message, to_addrs=recipients)


# #[EOF]#######################################################################
