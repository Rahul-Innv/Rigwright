# Changelog

All notable changes to Rigwright are recorded here. The project has no public semantic release yet.

## [Unreleased]

### Added

- Initial public staging of Rigwright `0.1.0`: seven atomic candidate leaves, neutral contracts, deterministic dual-surface adapter builds, offline evaluation gates, frozen runtime-eval fixtures, and governance documentation.
- Packaging metadata (`pyproject.toml`) exposing the offline tools as the `rigwright` package and CLI.
- An example source-capture configuration (`config/sources.example.json`); the provenance fingerprint tool is optional and skips cleanly when unconfigured.
- Ignore rules for generated `artifacts/` evidence, packaging output, and machine-local `config/sources.json`.

### Changed

- Renamed the project for public staging and removed private workspace evidence, raw provenance captures, provider records, and machine-local configuration from the source tree.
- Declared deterministic LF checkout behavior for text while retaining ZIP bytes as binary.

### Known limitations

- Runtime (provider-backed) evidence is not included. An internal blinded evaluation was run; it does not authorize promotion, and both evaluated candidate conditions retained critical-failure instances.
- Producing Codex plugin manifests that pass the native validator for a dual-surface plugin remains an open problem.
- No approved public security-reporting contact exists yet.
- No canonical host URL has been selected; `0.1.0` remains untagged and unreleased.
