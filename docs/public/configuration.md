# Configuration

Rigwright has no install command and no runtime end-user configuration. Two build-time surfaces exist: the build mode and the optional source-capture configuration.

## Build modes

| Mode | Eligible records | Intended use |
|---|---|---|
| `normal` | `current-authorized` only | Future accepted operation under an external lifecycle authority. The current source emits no Rigwright package in this mode. |
| `candidate-sandbox` | `current-authorized` plus explicitly named candidate records | Isolated validation and evaluation only. |

Candidate adapters must be built only with the explicit `candidate-sandbox` mode. Generated packages remain under `artifacts/` (untracked) and are not installed.

## Source capture configuration (optional)

The provenance fingerprint tool (`tools/source_fingerprint.py`, `rigwright fingerprint`) verifies that frozen upstream source roots have not drifted. It is disabled by default because source locations are machine-local:

1. Copy `config/sources.example.json` to `config/sources.json`.
2. Replace each `path` with a readable local source root and describe its authority, trust tier, and license.
3. Run the tool once to capture a stability baseline under `artifacts/provenance/stability-window.json`.
4. Later runs verify the live roots against the frozen baseline and fail on drift.

`config/sources.json` embeds machine-local paths and must never be committed; it is ignored by `.gitignore`. Without it the tool (and the offline gate step that calls it) skips cleanly.

## Authority

An external lifecycle authority remains the owner of lifecycle eligibility and routing priority. Rigwright configuration cannot promote a candidate, activate a folder, or override a canonical owner.
