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

## Current Scope

The plugin is currently a communication runtime scaffold prepared for an SMTP
notification implementation. The runtime still exposes placeholder processing
logic and diagnostic stdout output, but the repository naming, metadata, and
module documentation now target the email plugin instead of the generic
template.

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
