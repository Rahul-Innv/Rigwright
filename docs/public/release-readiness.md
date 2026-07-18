# Release and distribution readiness

Rigwright has a selected pre-release version but no public semantic release, host Release object, registry package, or approved marketplace distribution.

## Current facts

- `VERSION`, `pyproject.toml`, and both surface manifests use the pre-release version `0.1.0`. No tag or host Release exists.
- Original Rigwright material uses the MIT license with Rahul Krishna as author and copyright holder; captured and imported materials retain their original terms and are retained privately.
- Package validation enforces an exact allowlist, byte-matches every ZIP member, and rejects machine-local home paths.
- No canonical host owner, project path, URL, or remote is configured.

## Release preparation

`CHANGELOG.md` keeps current work under `[Unreleased]`. A later approved release lane must:

1. preserve `0.1.0` consistently unless a later owner decision changes it;
2. build each distribution artifact from the exact committed tree;
3. inspect every archive member and rerun privacy, license, and secret checks;
4. align README, changelog, manifests, and release notes; and
5. independently qualify the committed candidate.

## Distribution channels

The implemented outputs are surface-native Claude Code and Codex plugin containers plus the `rigwright` Python package for the offline tools. Marketplace installation or publication remains a separate owner-gated action, and no registry upload has been performed.

## Owner-only outward actions

The owner must separately approve and perform or authorize:

- creation or confirmation of the canonical host project and remote;
- first push;
- semantic tag and host Release creation;
- description, topics, avatar, visibility, and public verification; and
- marketplace or package-registry publication, if a distribution channel is selected.

No command in this document authorizes an outward action.
