# Release and distribution readiness

Rigwright's source repository and offline Python CLI are public. Source version `0.2.0` is prepared
for review, while PyPI still carries `0.1.0` without a matching git tag, GitLab Release, or
established artifact-to-commit provenance. The skill and plugin candidates have no approved
marketplace distribution.

## Current facts

- `VERSION`, `pyproject.toml`, `tools/__init__.py`, and `config/release.json` use `0.2.0`. Both
  generated plugin manifests derive their version from `config/release.json`; generated artifacts
  are not checked in.
- PyPI records the offline CLI at `0.1.0`; no matching tag or GitLab Release exists, and the uploaded
  artifact has not been tied to a source commit.
- Original Rigwright material uses the MIT license with Rahul Krishna as author and copyright holder; captured and imported materials retain their original terms and are retained privately.
- Package validation enforces an exact allowlist, byte-matches every ZIP member, and rejects machine-local home paths.
- The canonical source project is [`gitlab.com/krahul02004/Rigwright`](https://gitlab.com/krahul02004/Rigwright), and package metadata points Repository, Issues, and Changelog links there.
- No skill or plugin has been installed, activated, promoted, or published to a marketplace.

## Release preparation

`0.2.0` is a MINOR candidate because it adds supported external-workspace skill authoring and
validation while preserving the proposal-only lifecycle boundary. `CHANGELOG.md` cuts the audited
work under `0.2.0` on 2026-07-19 and starts a fresh empty `[Unreleased]` section. It intentionally
has no compare link against nonexistent `v0.1.0`.

Before an outward release, a separately approved lane must:

1. independently qualify the exact committed `0.2.0` tree;
2. build each distribution artifact from that exact commit;
3. inspect every archive member and rerun privacy, license, and secret checks;
4. verify README, changelog, generated manifests, and release notes remain aligned; and
5. obtain separate approval for each tag, GitLab Release, package publication, or marketplace action.

## Distribution channels

The implemented outputs are surface-native Claude Code and Codex plugin containers plus the
`rigwright` Python package for the offline tools. The offline CLI `0.1.0` has been uploaded to PyPI;
`0.2.0` is only a local source candidate. A new CLI publication and any skill/plugin marketplace
installation or publication remain separate owner-gated actions.

## Owner-only outward actions

The owner must separately approve and perform or authorize:

- semantic tag `v0.2.0` and matching GitLab Release creation from the reviewed commit;
- build, inspection, clean-install verification, and publication of a new PyPI 0.2.0 artifact;
- description, topics, avatar, visibility, and public verification; and
- skill/plugin marketplace publication, if that distinct distribution channel is selected.

No command in this document authorizes an outward action.

## Prepared commands, not authorization

Only after independent acceptance of the exact merged commit and a new exact owner approval:

```powershell
$releaseVersion = Get-Content -LiteralPath VERSION -Raw
$releaseVersion = $releaseVersion.Trim()
if ($releaseVersion -ne '0.2.0') { throw 'The accepted source is not the prepared 0.2.0 candidate.' }
git tag -a "v$releaseVersion" -m "Rigwright $releaseVersion: external workspace authoring and safety hardening"
git push origin "v$releaseVersion"
```

Create one matching GitLab Release named `Rigwright 0.2.0` from `v0.2.0`. Package publication is a
separate action. Never create a retroactive `v0.1.0` tag or Release.
