# Release and distribution readiness

Verified against the public GitLab project and PyPI on 2026-09-25:

- Rigwright source, tag `v0.2.0`, and its GitLab Release are public.
- PyPI publishes the offline CLI at `0.2.0`. Earlier `0.1.0` did not have a
  matching Git tag or GitLab Release; do not retro-tag it.
- `VERSION`, `pyproject.toml`, `tools/__init__.py`, and `config/release.json`
  declare `0.2.0`. The generated Claude Code and Codex plugin manifests derive
  that version from `config/release.json`.
- The seven skill and plugin records remain candidate-sandbox proposals.
  Publication of the CLI did not install, activate, promote, or publish them
  to a marketplace.
- The release tag and matching version strings do not by themselves establish
  byte-for-byte provenance of the uploaded Python artifact.

## Future release boundary

The `0.2.0` release added external-workspace skill authoring and validation
while preserving the proposal-only lifecycle boundary. Any later source,
CLI, or plugin release needs independent checks of the exact source and
artifacts, plus a separate owner decision for outward actions. The external
capability registry remains the authority for skill lifecycle and priority.
Never create a retroactive `v0.1.0` tag or Release.
