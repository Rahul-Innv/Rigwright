# Contributing to Rigwright

Rigwright is currently a private candidate-sandbox proposal. Contributions must preserve the separation between neutral skill records, surface adapters, lifecycle authority, and live installations.

## Before proposing a change

1. Define one intent owner and one independently measurable outcome.
2. State explicit non-goals and the side-effect class.
3. Add at least three positive eval cases and one realistic near miss.
4. Keep Claude Code and Codex metadata surface-native; do not create a second cross-surface metadata authority.
5. Treat lifecycle state and routing priority as owned by an external lifecycle authority, not this repository.

Do not add installation, activation, provider, marketplace, remote, MCP, agent, hook, command, or app behavior to an existing leaf. Those outcomes require separate gates or separate atomic leaves.

## Validation

Use Python 3.12 or newer. Run the complete gate in a disposable clone or worktree because it writes preserved evidence under `artifacts/`:

```powershell
python tools/run_all.py
git status --short
git diff --check
```

Keep the first failed report and any retry evidence. Do not replace a failure with an undocumented passing rerun. Generated candidate packages must remain uninstalled.

## Change hygiene

- Use UTF-8 with LF line endings.
- Do not commit caches, local environments, credentials, tokens, or machine-local home paths.
- Do not paste private raw provider output into an issue or merge request.
- Preserve provenance and restore evidence; deletion and archive state are separate approvals.
- Update public claims only when the same candidate bytes have deterministic evidence.

## Review checklist

- The changed leaf remains atomic.
- Trigger and near-miss behavior is covered.
- Normal mode excludes inactive lifecycle states.
- Candidate builds require explicit `candidate-sandbox` mode.
- No live skill, lifecycle record, provider, marketplace, remote, or archive state changed.
- Privacy and security scans cover the exact proposed tree.
