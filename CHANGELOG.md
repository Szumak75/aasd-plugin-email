# Changelog

All notable changes to this plugin repository are documented in this file.

## [0.0.9] - 2026-03-26

### Added
- Added optional `footer_template` plugin configuration in
  `plugins/email/load.py` and `plugins/email/plugin/config.py`.
- Added footer rendering based on the local system hostname in
  `plugins/email/plugin/runtime.py`.
- Added unit coverage for default, disabled, and custom footer templates in
  `plugins/email/tests/test_email_plugin.py`.

### Changed
- Appended the configured plugin footer after `message.footer` in the final
  plain-text email body.

### Versioning
- Bumped local plugin version to `0.0.9` in `plugins/email/plugin/__init__.py`.

## [0.0.8] - 2026-03-25

### Changed
- Replaced remaining builtin generic collection annotations with
  `Tuple[...]`, `List[...]`, and `Dict[...]` across the local email plugin
  repository.

### Versioning
- Bumped local plugin version to `0.0.8` in `plugins/email/plugin/__init__.py`.

## [0.0.7] - 2026-03-25

### Changed
- Replaced the remaining `float | None` argument annotation with
  `Optional[float]` in `plugins/email/plugin/runtime.py`.

### Versioning
- Bumped local plugin version to `0.0.7` in `plugins/email/plugin/__init__.py`.

## [0.0.6] - 2026-03-25

### Added
- Added plugin-local unit tests in `plugins/email/tests/test_email_plugin.py`.
- Documented the standalone plugin test scope in `plugins/email/README.md`.

### Versioning
- Bumped local plugin version to `0.0.6` in `plugins/email/plugin/__init__.py`.

## [0.0.5] - 2026-03-25

### Added
- Added SMTP port failover in `plugins/email/plugin/runtime.py` for
  implicit-port configurations using `587`, `465`, and `25`.
- Added runtime password decoding with `SimpleCrypto.multiple_decrypt` in
  `plugins/email/plugin/runtime.py`.
- Documented SMTP failover and password decoding in `plugins/email/README.md`.

### Changed
- Added class-level remembered SMTP port reuse for future connections in
  `plugins/email/plugin/runtime.py`.

### Versioning
- Bumped local plugin version to `0.0.5` in `plugins/email/plugin/__init__.py`.

## [0.0.4] - 2026-03-25

### Added
- Added SMTP email delivery logic to `plugins/email/plugin/runtime.py`.
- Added message-to-email mapping documentation to `plugins/email/README.md`.

### Changed
- Added support for `smtp_server` values in `host` and `host:port` form.

### Versioning
- Bumped local plugin version to `0.0.4` in `plugins/email/plugin/__init__.py`.

## [0.0.3] - 2026-03-25

### Added
- Added local SMTP configuration keys in `plugins/email/plugin/config.py`:
  `smtp_server`, `smtp_user`, `smtp_pass`, `address_from`, `address_to`.
- Added SMTP-related schema fields in `plugins/email/load.py`.
- Documented the current plugin configuration fields in `plugins/email/README.md`.

### Versioning
- Bumped local plugin version to `0.0.3` in `plugins/email/plugin/__init__.py`.

## [0.0.2] - 2026-03-25

### Changed
- Added `plugins/email/__init__.py` so static analysis tools can resolve
  package-relative imports from `plugins/email/load.py`.

### Versioning
- Bumped local plugin version to `0.0.2` in `plugins/email/plugin/__init__.py`.

## [0.0.1] - 2026-03-25

### Changed
- Updated plugin repository description in `plugins/email/README.md`.
- Updated module, class, and method docstrings in `plugins/email/load.py`.
- Updated package and module docstrings in `plugins/email/plugin/__init__.py`.
- Updated module and class docstrings in `plugins/email/plugin/config.py`.
- Updated module, class, and method docstrings in `plugins/email/plugin/runtime.py`.

### Versioning
- Initialized local plugin version to `0.0.1` in `plugins/email/plugin/__init__.py`.
