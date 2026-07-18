# Privacy and retained evidence

Rigwright's offline gates write raw build, validation, and (when configured) provenance and archive records under `artifacts/`. Preservation supports audit and rollback, but retained evidence is not automatically safe for public distribution.

## Boundary

The public source tree contains no raw provider records, no source captures, and no machine-local paths. Raw private evidence from the project's development — provider envelopes, blinded-review records, source-capture manifests, and restoration records — is retained privately by the owner and is deliberately excluded from this repository. `artifacts/` is untracked so locally generated evidence never lands in version control by accident.

## Candidate package exclusion gate

The local package builder emits only an explicit allowlist: the candidate notice, MIT license, one surface-native plugin manifest, and generated atomic skill, eval, and Codex UI files. The package validator rejects any other member, compares every ZIP member byte with the approved build tree, and fails on Windows or macOS home-path patterns. Raw `artifacts/`, source captures, provider records, imported packages, and private provenance are never package inputs.

Passing that gate makes a package a locally qualified candidate only. It does not authorize publication, installation, promotion, or exposure.

## Retention classes

| Class | Meaning | Public treatment |
|---|---|---|
| Raw private evidence | Original logs, provider envelopes, source manifests, and restoration records. | Retain privately; do not publish. |
| Sanitized derivative | Deterministically transformed proof with private paths and data removed. | Publish only with a transformation manifest and independent scan. |
| Public-safe fixture | Generic input created for public evaluation. | Publish after exact-byte privacy and license review. |
| Distribution artifact | Package built from an accepted public-safe source tree. | Publish only after package-content dry-run and owner approval. |

## Rules

- Never replace a raw record with a sanitized derivative; preserve both with a documented relationship.
- Never interpret `.gitignore` as removal of already tracked private material.
- Record transformation code, input and output hashes, redaction classes, and validation results.
- Scan the complete proposed public tree and every package archive, not only README-visible files.
- Do not expose provider credentials, raw personal data, unbounded transcripts, or machine-local paths.
- Treat archive deletion, live discovery changes, and lifecycle transitions as separate approvals.
