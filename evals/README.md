# Evaluation coverage

- Leaf-owned evals live beside each neutral source under `src/skills/<leaf>/evals/evals.json`.
- `fixed-tasks/tasks.json` maps the six required fixed tasks to concrete leaf cases.
- `baselines/static-practice-baselines.json` measures documented practice coverage only; it is not runtime model quality.
- `lifecycle-priority/cases.json` contains adversarial candidate, alias, archive, quarantine, rejection, duplicate-owner, and project-specific priority cases.
- `runtime/` contains the frozen runtime-tier public prompts, input artifacts, private rubrics, response schema, paired controls, and three-replicate protocol. Models receive only the public prompt, named input bytes, invocation line, and response contract; graders remain out of prompt context.
- `artifacts/validation/offline-evals.json` is the deterministic offline result.
- Provider-backed execution requires a separate approval. Installation, candidate revision, promotion, lifecycle-authority integration, and cutover remain forbidden.
