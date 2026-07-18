# Evaluation contract

## Offline tier

The default tier is deterministic and provider-free. It measures:

- contract and atomicity validation;
- source-practice coverage baselines for no creator, the author's prior `authoring-skills` skill, the Anthropic creator, the OpenAI creator, and Rigwright;
- fixed task artifacts: simple skill, bloated-skill improvement, trigger collision, Claude-to-Codex migration, dual-surface plugin, and unsafe plugin rejection;
- at least three positive cases and one realistic near miss per leaf;
- lifecycle priority, alias collision, inactive-state exclusion, and candidate-build exclusion;
- Claude and Codex package structure and native/static validators;
- deterministic rebuild tree and ZIP hashes; and
- copy-only archive hash and restore qualification when a packet exists.

Offline static coverage is not a claim that a model executed the workflow better. It proves the contract contains and validates the required practices.

## Separately approved runtime tier

Provider execution requires a separate approval. Candidate and baseline must use the same model, effort, prompt artifact, repository state, tools, permissions, and timing window. Run with-skill and baseline in the same turn where the surface supports it. Capture correctness, critical omissions, trigger precision/recall, safety decision, tokens, model-visible and raw tool bytes, latency, retries, and variance.

Use at least three runs per configuration for promotion decisions. Compare against no creator and the strongest applicable source; use an old snapshot when improving. Generate human-review artifacts before evaluator-driven revision. Blind comparisons must hide source identity and intended rationale. Fresh agents receive raw artifacts and the task, not the expected answer or suspected fix.

Promotion requires no critical safety regression, no canonical-owner collision, demonstrated rollback, and owner approval. An absent provider run remains `BLOCKED_OWNER_GATE`, never `PASS`.

`evals/runtime/` is the frozen provider packet for that tier. Each condition uses three fresh replicates. The model sees the public prompt, exact input bytes, one condition-specific invocation line, and the common response contract; it never sees private rubric criteria or expected outcomes. Raw provider envelopes are retained before grading. Candidate revision from evaluator output stays outside the tier.

One internal blinded execution of this tier has been run. Identity-blind model grading favored the candidate on both surfaces, but both candidate conditions retained critical-failure instances and owner human review is incomplete, so the recorded status is executed-with-limitations and nothing was promoted. Raw records, costs, and per-row metrics are retained privately and are not part of this repository.
