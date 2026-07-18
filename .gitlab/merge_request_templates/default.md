## Outcome

Describe the single outcome this change owns.

## Scope

- Changed leaves or public documents:
- Explicit non-goals:
- Exact base commit:

## Validation

- [ ] `python tools/run_all.py` passed in a disposable worktree.
- [ ] Failed attempts and retries remain documented.
- [ ] `git diff --check` passed.
- [ ] The exact proposed tree was scanned for secrets and home paths.
- [ ] Trigger positives and near misses pass for every changed leaf.
- [ ] Normal mode excludes candidate and inactive lifecycle states.
- [ ] Generated packages remain uninstalled.

## Authority and privacy

- [ ] The external lifecycle authority remains the lifecycle and routing-priority owner.
- [ ] No live skill, provider, marketplace, remote, tag, release, or archive state changed.
- [ ] No credentials, raw private records, or machine-local paths were added.
- [ ] Public claims are supported by the attached deterministic evidence.
