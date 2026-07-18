# Rigwright working agreements

- This tree is a candidate-sandbox proposal. Nothing in it is installed, enabled, published, or authoritative over any live capability registry.
- Lifecycle state and routing priority belong to an external lifecycle authority; this repository proposes records but never promotes them.
- Treat captured upstream skill sources as read-only. Never execute copied source scripts as part of provenance or archive inspection.
- Build candidate adapters only with an explicit `--mode candidate-sandbox`. A normal build must exclude candidate, alias, archived, quarantined, and rejected records.
- Keep each skill leaf atomic: one intent owner, one independently measurable outcome, explicit non-goals, and its own eval set.
- Do not add MCP, agent, hook, command, or app authoring to the initial seven leaves. Those are separately gated future leaves.
- Use Python 3.12+ standard-library tools in `tools/`. Run `python tools/run_all.py` for the offline proposal gate.
- Preserve raw validator/eval output under `artifacts/` (untracked); do not replace a failed report with an undocumented retry.
