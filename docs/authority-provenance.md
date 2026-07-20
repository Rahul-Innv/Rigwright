# Authority provenance and practice decisions

Classification values are `shared`, `claude-only`, `codex-only`, `rejected`, and `superseded`.

## Authorities

| Authority | Role retained |
|---|---|
| Author `authoring-skills` | Evals before prose, explicit no-skill baseline, lightweight/full/trigger tiers, security posture, reviewable learning, portable linters, one-level references, altitude by fragility. |
| Anthropic official `skill-creator` | Intent interview, realistic prompts, same-turn candidate/baseline runs, timing capture, formal grading, aggregate benchmark, analyst pass, human viewer, blind comparison, held-out trigger optimization. |
| OpenAI system `skill-creator` | Concise anatomy, progressive disclosure, deterministic scaffold/validation, tested scripts, non-leaking fresh-agent forward tests, `agents/openai.yaml`, explicit implicit-invocation policy. |
| Anthropic `plugin-dev` (`skill-development` + `plugin-structure`) | Root-level Claude component layout, `.claude-plugin/plugin.json`, auto-discovery, `${CLAUDE_PLUGIN_ROOT}`, portable paths, and component-specific authoring. |
| OpenAI system `plugin-creator` | `.codex-plugin/plugin.json`, strict validation, deterministic scaffolding, optional companion-file rules, and marketplace/update behavior as Codex-only knowledge. |

## Practice decision matrix

| Conflict/practice | Selected neutral rule | Class | Source evidence retained | Alternative rejected or bounded | Rationale |
|---|---|---|---|---|---|
| Skill frontmatter | Neutral source is structured JSON; generated Codex `SKILL.md` has only `name` and `description`; Claude adapter may add supported Claude-only fields when necessary. | shared + surface adapters | OpenAI creator; author frontmatter reference | Claude plugin-dev `version` in skill frontmatter is rejected. | Avoid unsupported cross-surface fields and keep version out of skill metadata. |
| Skill version | Contract schema carries its version. Skill frontmatter never does. Distribution version is surface/package specific. | shared | author standard; OpenAI creator | Plugin-dev skill `version: 0.1.0` examples are superseded for Rigwright output. | Prevent two version authorities. |
| Description | Third-person WHAT + concrete WHEN/triggers, <=1024 characters; negatives are tested rather than packed into prose when that would harm clarity. | shared | All three creators | Vague or body-only triggering is rejected. | Both surfaces route from metadata. |
| Body size | Keep essential procedure under 500 lines; move variant/detail to directly linked references. | shared | Author, Anthropic, OpenAI | Fixed 1,500-2,000 word target is advisory, not a requirement. | Line and token economy is safer across surfaces. |
| References | One level from `SKILL.md`; long references get a table of contents; state whether each resource is read or run. | shared | Author and OpenAI | Deep reference chains are rejected. | Preserves discovery and bounded context. |
| Scripts | Use source-visible, dependency-minimal scripts for fragile deterministic behavior; test them directly; never execute untrusted source scripts during extraction. | shared | All three creators; the lifecycle authority | Fetch-and-execute and hidden dependencies are rejected. | Reliability without expanding trust. |
| Dynamic lessons | No dynamic shell injection in neutral output. Verified lessons become reviewed source changes and regression evals. Claude-only injection remains a separately approved adapter feature. | rejected for shared core; claude-only future option | Author `LESSONS.md` loop | Automatic `!` shell loading is not emitted. | It is Claude-specific, executes before normal permission review, and is unsupported by Codex. |
| Side effects | Declare a neutral side-effect class and explicit owner gates. Use an in-body gate when a router must delegate. | shared | author security posture; the lifecycle authority | Broad `allowed-tools`, bypass modes, and silent writes are rejected. | Keeps routing possible without weakening approval boundaries. |
| Evals before prose | Define baseline gap and eval cases before final instructions; at least three positive task cases and one realistic near miss per leaf. | shared | Author; Anthropic | “Vibe only” is not accepted for this cross-surface system. | Atomic outcomes must be independently measurable. |
| Runtime evaluation | Candidate and baseline share model, effort, task artifact, repo state, and timing window; capture tokens, bytes, latency, retries, variance, and safety. | shared, owner-gated | Anthropic; project plan | Provider execution is not performed in the initial phase. | The initial phase forbids providers; offline evidence must not be mislabeled as runtime proof. |
| Human review | Produce review artifacts before evaluator-led revision; blind comparison is optional when independent agents are allowed. | shared | Anthropic | Hidden self-grading is rejected. | Prevents evaluation-driven overfitting. |
| Fresh-agent tests | Pass raw artifacts and task-local context; do not leak intended answer, diagnosis, or rationale. | shared | OpenAI creator | Review prompts that reveal the fix are rejected. | Tests generalization. |
| Claude plugin layout | Use root-level `skills/` and `.claude-plugin/plugin.json`; use `${CLAUDE_PLUGIN_ROOT}` only for Claude runtime paths. | claude-only | Anthropic plugin-dev | Applying the layout to Codex is rejected. | Surface-native discovery. |
| Codex skill UI | Put display metadata and `allow_implicit_invocation` in `agents/openai.yaml`. | codex-only | OpenAI creator | Adding these keys to neutral skill frontmatter is rejected. | Keeps Codex SKILL frontmatter minimal. |
| Codex plugin manifest | Use `.codex-plugin/plugin.json`, strict semver, required interface metadata, and companion fields only when files exist. | codex-only | OpenAI plugin-creator validator | The reference's illustrative `hooks` key is rejected because the same native validator rejects it. | Executable validator behavior wins over contradictory prose. |
| Marketplace behavior | Preserve as Codex-only knowledge but do not generate or update a marketplace in this phase. | codex-only, gated | OpenAI plugin-creator | Default personal-marketplace mutation is rejected for the initial phase. | The initial phase forbids marketplace changes. |
| Claude plugin version | Emit the selected distribution version from `config/release.json` in the generated plugin manifest; never put it in skill frontmatter. | claude-only | author standard | Plugin-dev's immediate per-skill version is rejected. | One reviewed release source drives generated package metadata. |
| Codex plugin version | Emit the same strict-semver value from `config/release.json`; do not use cachebusters in proposal builds. | codex-only | OpenAI plugin-creator | Reinstall/cachebuster flow is deferred. | Both generated surfaces derive from one reviewed version authority. |
| Atomicity | One intent owner, one measurable outcome, explicit non-goals, bounded I/O, and independent evals. Split when two outcomes can fail independently. | shared | Master plan; lifecycle-authority ownership rules | One giant creator skill is rejected. | Prevents routing collision and context bloat. |
| Lifecycle and priority | Registry state controls eligibility; the folder tree never does. Current authorized owners outrank candidates and aliases; inactive states are ineligible. | shared authority | the lifecycle authority and project plan | Alphabetical/folder discovery order is rejected. | One canonical owner per intent/scope/surface. |

No source was copied wholesale into neutral instructions. The matrix records behavioral synthesis and preserves source hashes separately.
