# Compatibility and migration proposal

No step in this document is executed by the current proposal phase.

## Successor map

| `authoring-skills` responsibility | Rigwright successor |
|---|---|
| Entry/routing | `rigwright-route` |
| Create or improve one skill | `rigwright-author-skill` |
| Plugin container/package guidance | `rigwright-author-plugin` |
| Lightweight/full/trigger/regression evaluation | `rigwright-evaluate` |
| Cross-surface conversion and compatibility planning | `rigwright-migrate` |
| Canonical ownership and collision decisions | `rigwright-prioritize` |
| Snapshot, checksum, restore, and removal proposal | `rigwright-archive` |
| Claude dynamic `LESSONS.md` injection | No shared successor; retain as a Claude-only optional migration decision after security review. |

## Exact later sequence

1. Approve the Rigwright repository root and commit separately.
2. Build candidate packages from that exact commit and verify hashes match this proposal or explain every delta.
3. Run owner-approved same-model paired Claude Code and Codex forward tests. Provider execution is a distinct gate.
4. Promote the neutral records in a reviewed lifecycle-authority change; confirm only one current canonical owner for the authoring intents.
5. Install or expose one surface at a time under a separate exact approval.
6. Read back the installed package, lifecycle record, discovery metadata, and trigger behavior.
7. Only after both surfaces pass, approve creation of the live `authoring-skills` archive snapshot and removal from normal discovery as separate operations.
8. Retain the old name as a time-bounded alias only if a real legacy invocation fails without it and collision tests pass. Otherwise rely on the retained archive.
9. Test rollback by restoring the exact prior bytes and discovery state, then return to the promoted state only with approval.

## Compatibility alias proposal

If justified, `authoring-skills` becomes a thin routing-only alias to `rigwright-route`. It contains no authoring procedure, has lower priority than the successor, declares an expiry/review date, and is never allowed to intercept direct `rigwright-*` invocations. A junction is not assumed; the physical mechanism requires a separate owner choice because Claude and Codex coexistence must be preserved.

## Rollback

Rollback inputs are the pre-cutover lifecycle record, exact live file manifest, retained packet, and installation/discovery evidence. A rollback is incomplete until bytes, adapter metadata, and trigger visibility are read back successfully.
