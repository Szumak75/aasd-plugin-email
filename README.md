# AASd Email Communication Plugin

This directory contains a standalone AASd communication plugin repository
responsible for SMTP-based email notifications.

## Included Files

- `load.py` - required daemon entry point exposing `get_plugin_spec()`
- `plugin/__init__.py` - plugin package marker and local plugin version
- `plugin/config.py` - plugin-specific configuration keys
- `plugin/runtime.py` - thread-based communication runtime implementation
- `requirements.txt` - plugin-local runtime dependencies
- `CHANGELOG.md` - local plugin change history
- `tests/` - plugin-local unit tests

## Current Scope

The plugin is currently a communication runtime scaffold prepared for an SMTP
notification implementation. The runtime still exposes placeholder processing
logic and diagnostic stdout output, but the repository naming, metadata, and
module documentation now target the email plugin instead of the generic
template.

## Configuration

The plugin currently exposes the following configuration fields:

- `channel` - dispatcher channel consumed by the plugin runtime
- `stdout_prefix` - diagnostic prefix used in stdout output
- `smtp_server` - SMTP server hostname
- `smtp_server` supports both `host` and `host:port` forms
- `smtp_user` - SMTP authentication username
- `smtp_pass` - SMTP authentication password encoded with
  `SimpleCrypto.multiple_decrypt`
- `address_from` - sender email address
- `address_to` - recipient email address list

## Runtime Behavior

The current runtime consumes dispatcher messages from the configured channel,
builds an `EmailMessage`, and sends it through the configured SMTP server.

When `smtp_server` does not define a port, the runtime tries `587`, `465`,
and `25` with failover and remembers the first working port for future
connections during the process lifetime.

- `message.subject` overrides the default generated subject
- `message.sender` overrides `address_from`
- `message.to` overrides `address_to`
- `message.reply_to` is mapped to the `Reply-To` header
- `message.messages` and `message.footer` are merged into the plain-text body
- `message.mmessages["plain"]` and `message.mmessages["html"]` are used for
  multipart email payloads when present
- `smtp_pass` is decoded with `SimpleCrypto.multiple_decrypt` using the daemon
  main-section `salt`

## Tests

Unit tests for the standalone plugin repository are stored in `plugins/email/tests`.
They cover plugin manifest exports, local configuration keys, SMTP transport
selection, port failover, remembered port reuse, password decoding, recipient
fallbacks, and runtime error handling.

## Design Notes

The plugin follows the current recommended communication plugin pattern:

- `PluginSpec` and `PluginContext` from the public runtime API
- `PluginKind.COMMUNICATION` with dispatcher consumer registration
- package-relative imports inside `load.py` and `plugin/*`
- `ThPluginMixin` for typed runtime-owned storage
- local private key constants based on `ReadOnlyClass`
- explicit narrowing of `Optional[...]` runtime properties
- `PluginStateSnapshot` and `PluginHealthSnapshot` fallbacks for guard paths

For broader project guidance, see:

- `docs/PluginAPI.md`
- `docs/PluginChecklist.md`
- `docs/PluginRepositoryModel.md`
