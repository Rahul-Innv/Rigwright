# Proposed lifecycle and priority schema

This is a proposal only. It does not change any live capability registry.

## Lifecycle states

| State | Eligibility | Generated adapters | Transition requirement |
|---|---|---|---|
| `current-authorized` | Normal discovery and routing. | Included in normal and sandbox builds. | Owner approval, paired evidence, rollback, unique canonical owner, readback. |
| `candidate-sandbox` | Only an explicitly named evaluation sandbox; always below a matching current owner. | Excluded from normal builds; included only with explicit candidate mode. | Complete evaluation and separate promotion approval. |
| `compatibility-alias` | Legacy invocation only when the authorized successor cannot satisfy it. | Excluded by default; separately generated only after collision tests and expiry are approved. | Named successor, expiry/review date, collision test, owner approval. |
| `archived-retained` | Never eligible. | Never generated. | Hashes, provenance, successor mapping, removal approval, tested restore. |
| `quarantined-untrusted` | Never eligible or executable. | Never generated. | Trust/provenance/security review before any normalization. |
| `rejected` | Never eligible. | Never generated. | Retain reason and evidence; a new candidate requires a new record/eval. |

Deletion is not a state. Archive retention has no automatic deletion path.

## Required record fields

Every record declares `state`, `canonical_owner`, `intent_key`, `scope`, `surfaces`, `routing_priority`, `specificity`, `supersedes`, `evidence_date`, and `promotion_gate`. Runtime state axes such as installed/enabled/exposed/authorized remain orthogonal and must not be inferred from lifecycle state.

## Deterministic selection

1. Reject archived, quarantined, rejected, unavailable, unauthorized, or wrong-surface records.
2. Prefer an exact explicit owner invocation only when that owner is `current-authorized`.
3. Prefer a matching authorized project/domain-specific record.
4. Prefer the canonical `current-authorized` cross-platform record.
5. Admit `candidate-sandbox` only in an explicitly named sandbox; keep it below a matching current owner.
6. Admit a `compatibility-alias` only for a legacy invocation that the successor cannot satisfy.
7. Within the same eligible class, prefer higher specificity, then fresher evidence, then lower context/tool cost, then stable ID only as a deterministic final tie break.
8. Fail closed if more than one `current-authorized` record owns the same intent, scope, and surface.

`routing_priority` records the class-level policy and is validated for consistency; it is not a number that can make an inactive state eligible.

## Required proofs

The offline suite includes adversarial records with artificially high numeric priority for candidate, alias, archived, quarantined, and rejected states. None may outrank the current owner in normal mode. A sandbox candidate remains below the current owner. An alias can win only when the legacy invocation is explicit and the successor is marked unable to satisfy it.
