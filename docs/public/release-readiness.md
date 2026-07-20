# Release and distribution readiness

Rigwright's source repository and the offline Python CLI are public. PyPI carries version `0.1.0`, but there is no matching git tag, GitLab Release, or established artifact-to-commit provenance. The skill and plugin candidates have no approved marketplace distribution.

## Current facts

- `VERSION`, `pyproject.toml`, and both surface manifests use version `0.1.0`. PyPI records the offline CLI at that version; no matching tag or GitLab Release exists, and the uploaded artifact has not been tied to a source commit.
- Original Rigwright material uses the MIT license with Rahul Krishna as author and copyright holder; captured and imported materials retain their original terms and are retained privately.
- Package validation enforces an exact allowlist, byte-matches every ZIP member, and rejects machine-local home paths.
- The canonical source project is [`gitlab.com/krahul02004/Rigwright`](https://gitlab.com/krahul02004/Rigwright), and package metadata points Repository, Issues, and Changelog links there.
- No skill or plugin has been installed, activated, promoted, or published to a marketplace.

## Release preparation

`CHANGELOG.md` keeps current work under `[Unreleased]`. A later approved release lane must:

1. select and apply a new reviewed patch version instead of reusing the provenance-unknown `0.1.0` artifact;
2. build each distribution artifact from the exact committed tree;
3. inspect every archive member and rerun privacy, license, and secret checks;
4. align README, changelog, manifests, and release notes; and
5. independently qualify the committed candidate.

## Distribution channels

The implemented outputs are surface-native Claude Code and Codex plugin containers plus the `rigwright` Python package for the offline tools. The offline CLI `0.1.0` has been uploaded to PyPI. A corrected patch upload and any skill/plugin marketplace installation or publication remain separate owner-gated actions.

## Owner-only outward actions

The owner must separately approve and perform or authorize:

- selection of the next patch version and reconciliation of all version-bearing files;
- semantic tag and GitLab Release creation from the reviewed commit;
- build, inspection, clean-install verification, and publication of the new PyPI patch artifact;
- description, topics, avatar, visibility, and public verification; and
- skill/plugin marketplace publication, if that distinct distribution channel is selected.

No command in this document authorizes an outward action.
