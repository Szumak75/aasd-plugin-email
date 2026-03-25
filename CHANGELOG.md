# Changelog

All notable changes to this plugin repository are documented in this file.

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
