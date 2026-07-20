# Changelog

All notable changes to Rigwright are recorded here. PyPI publication, source tags, host Releases,
and skill lifecycle state are separate facts and are recorded separately.

## [Unreleased]

## [0.2.0] - 2026-07-19

### Added

- Initial public staging of seven atomic candidate leaves, neutral contracts, deterministic dual-surface adapter builds, offline evaluation gates, frozen runtime-eval fixtures, and governance documentation.
- Packaging metadata (`pyproject.toml`) exposing the offline tools as the `rigwright` package and CLI.
- An example source-capture configuration (`config/sources.example.json`); the provenance fingerprint tool is optional and skips cleanly when unconfigured.
- Ignore rules for generated `artifacts/` evidence, packaging output, and machine-local `config/sources.json`.
- Supported `init-skill` and `validate-workspace` commands for creating and validating generic skill
  workspaces outside the Rigwright vendor tree, with deterministic fixtures and end-to-end tests.

### Changed

- Renamed the project for public staging and removed private workspace evidence, raw provenance captures, provider records, and machine-local configuration from the source tree.
- Declared deterministic LF checkout behavior for text while retaining ZIP bytes as binary.
- Made evaluation replay self-contained on a pristine checkout, improved outside-checkout CLI
  diagnostics, and added GitLab project URLs to package metadata.
- Added merge-request CI coverage for the complete offline gate and recorded the canonical public
  source and historical PyPI state without inventing source provenance.

### Fixed

- Fail before writing when a requested workspace root is invalid, indirect, or escapes through a
  symlink or junction; reject indirect ancestors and nested validation-manifest indirection.

### Known limitations

- Runtime (provider-backed) evidence is not included. An internal blinded evaluation was run; it does not authorize promotion, and both evaluated candidate conditions retained critical-failure instances.
- Producing Codex plugin manifests that pass the native validator for a dual-surface plugin remains an open problem.
- No approved public security-reporting contact exists yet.
- The canonical source host is [`gitlab.com/krahul02004/Rigwright`](https://gitlab.com/krahul02004/Rigwright). PyPI `0.1.0` has no matching git tag or GitLab Release, so artifact-to-commit provenance has not been established.

This minor release has no compare link because the published `0.1.0` package has no matching source
tag. The historical package must not be retro-tagged to manufacture provenance.

## [0.1.0] - 2026-07-18

- PyPI records publication of `rigwright` version `0.1.0` for the offline Python CLI.
- This entry records registry state only. No matching git tag or GitLab Release exists, artifact-to-commit provenance has not been established, and no skill or plugin was installed, activated, promoted, or published by that package publication.
