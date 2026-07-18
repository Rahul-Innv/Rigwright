# Conflicts, safety gates, and open problems

## Resolved in the proposal

- Some upstream examples place `version` in skill frontmatter; neutral and generated Rigwright skills omit it so no second version authority exists.
- The Codex plugin-creator prose shows `hooks` in an illustrative manifest while its native validator rejects `hooks`; validator behavior is selected and hooks remain a future leaf.
- Dynamic lesson injection through shell loading is useful on Claude but unsafe and non-portable as shared core behavior; verified lessons become reviewed source and eval changes instead.
- Codex plugin validation requires strict semver while pre-1.0 Claude guidance omits plugin version. Each surface gets its own valid distribution rule.

## Owner-gated work

- Same-model, same-effort provider-backed forward tests on both surfaces.
- Integration with an external lifecycle authority and any promotion decision.
- Plugin installation, activation, auth, marketplace, hooks, MCP, app, agent, or command work.
- Any live cutover from an existing authoring tool, compatibility alias, or removal from discovery.

## Runtime evaluation status

An internal blinded evaluation of candidate and baseline conditions was run on
both surfaces with per-row dispositions and no computed global winner.
Condition identities remained sealed during grading, and the closeout
authorized no activation, promotion, or lifecycle change. Raw records are
retained privately and are not part of this repository.

Two findings remain binding on future work:

- **Dual-surface Codex-manifest native validation is an open problem.** In the
  evaluated dual-surface plugin row, no condition produced a Codex manifest
  that passed the current native validator, so that row closed as a tie with
  both conditions blocked. Rigwright's own generated Codex package passing the
  captured native validators is candidate-local evidence only; it does not
  resolve that row and must not be presented as solving it.
- Generated `agents/openai.yaml` and `.codex-plugin/plugin.json` must keep
  passing the current native validators before any live use.

Shared cross-surface `SKILL.md` frontmatter remains restricted to `name` and
`description`; Codex UI and invocation policy stay only in
`agents/openai.yaml`; trigger and input scope stay narrow instead of widening
pasted-text work into arbitrary file workflows; and unsafe-extension requests
are refused transparently with a safe opt-in, least-privilege, local-first
alternative offered when one exists.
