# Architecture

Rigwright uses one neutral source and two generated delivery surfaces. The neutral record owns intent, outcome, non-goals, inputs, outputs, permission class, triggers, lifecycle metadata, instructions, eval location, and provenance. It contains no Claude-only shell injection and no Codex-only UI metadata.

```text
contracts + source records + evals
                 |
        deterministic validator
                 |
       explicit candidate build
          /              \
 Claude Code package   Codex package
 .claude-plugin/       .codex-plugin/
 surface frontmatter   agents/openai.yaml
```

An external lifecycle authority remains authoritative for lifecycle state and routing priority. Folder presence is not activation. The builder therefore has two modes:

- `normal`: emit only `current-authorized` records.
- `candidate-sandbox`: emit `current-authorized` plus `candidate-sandbox` records and add a prominent candidate notice.

The initial source contains only candidate records, so a normal build intentionally emits no Rigwright package. Generated candidate packages under `artifacts/` are disposable evaluation artifacts, not installations.

## Source layout

```text
src/skills/<leaf>/
  skill.json
  evals/evals.json
```

Every leaf record validates against `contracts/authoring-contract.schema.json`. Lifecycle records align with the proposed `capability-policy.schema.json`; eval sets align with `evaluation.schema.json`.

## Adapter boundaries

- Claude Code receives `.claude-plugin/plugin.json`, `skills/<id>/SKILL.md`, and only Claude-compatible frontmatter. The proposal uses an explicit in-body side-effect gate so the router can delegate; no dynamic lesson command is emitted.
- Codex receives `.codex-plugin/plugin.json`, `skills/<id>/SKILL.md` with only `name` and `description`, and `skills/<id>/agents/openai.yaml` for UI and implicit-invocation policy.
- Plugin manifests are surface-native. They are not translated by renaming keys.
- Marketplaces, hooks, MCP servers, apps, agents, and commands are not generated.

## Determinism

The builder sorts inputs and output paths, uses UTF-8 with LF, excludes wall-clock values from generated packages, and creates ZIP archives with fixed timestamps and permissions. Two isolated builds must have identical tree and ZIP SHA-256 values.
