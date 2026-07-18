# Validation

Rigwright has one complete evidence-producing offline gate plus individually runnable checks.

## Complete offline gate

Run in a disposable clone or worktree with Python 3.12 or newer:

```sh
python tools/run_all.py
git status --short
git diff --check
```

The gate optionally verifies configured source fingerprints, validates contracts and atomic responsibility, builds Claude Code and Codex candidate packages in both modes, compares deterministic tree and ZIP hashes, validates the frozen runtime fixtures, and runs the static and near-miss evals. It writes attempt and aggregate evidence under `artifacts/` (untracked); keep failed attempts and explain retries.

It does not install, activate, publish, or promote a generated package.

## Current gate result

A complete run of `python tools/run_all.py` on this tree produces:

```text
source fingerprint skipped: no config/sources.json
contract validation passed: 127 checks, 7 leaves, 32 eval cases
adapter build normal: 0 included, 7 excluded
adapter build candidate-sandbox: 7 included, 0 excluded
package validation passed: 224 checks
determinism passed: 2 surface packages
runtime fixtures passed: 6 tasks, 4 conditions, 3 replicates
offline evals passed: 59 assertions, 7 near misses, 6 fixed tasks
offline gate PASS: 8/8 commands
```

When a copy-only archive packet exists under `artifacts/archive-proposals/`, its restore report is verified as an additional assertion. These counts prove deterministic contract and fixture coverage only. They do not prove model superiority, installation safety, or promotion approval.

## Checkout-byte reproducibility

Automatic end-of-line conversion can change byte-level fixture hashes without changing the Git commit or tree. The repository therefore declares LF for text and binary treatment for ZIP archives in `.gitattributes`. Qualification must materialize the exact staged or committed tree under those attributes; a passing count with unexplained byte-hash drift is not sufficient.

## Optional source fingerprinting

When `config/sources.json` is configured (see [Configuration](configuration.md)), the gate's first step captures or verifies frozen upstream source roots and fails on drift. Do not refresh a baseline silently; document any new capture.

## Required launch checks

- complete offline gate from the exact candidate tree;
- independent replay in a fresh worktree;
- exact diff and tracked-file manifest;
- secret, home-path, private-project, and old-host scans;
- documentation and demo truth review;
- proof that no provider, marketplace, remote, tag, release, or publication action occurred.
