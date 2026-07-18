# Atomic responsibility matrix

| Leaf | Sole intent owner | Independently measurable outcome | Explicit non-goals |
|---|---|---|---|
| `rigwright-route` | Select a Rigwright leaf. | Returns exactly one eligible leaf or a bounded clarification/block. | Does not author, package, evaluate, migrate, prioritize, archive, install, or execute a selected leaf's procedure. |
| `rigwright-author-skill` | Author or improve one atomic neutral skill. | Produces one contract-valid source plus requested surface adapters and evals. | Does not build plugin containers, run promotion evaluation, install, activate, or archive. |
| `rigwright-author-plugin` | Author one plugin container. | Produces valid surface-native manifests and delegates any contained skill authoring. | Does not author MCPs, agents, hooks, commands, apps, marketplaces, or duplicate skill-authoring logic. |
| `rigwright-evaluate` | Evaluate a frozen skill/plugin candidate. | Produces baseline/candidate/old-version results with metrics, review artifacts, and regressions. | Does not rewrite, promote, install, or activate the candidate. |
| `rigwright-migrate` | Produce a compatibility-preserving migration proposal. | Classifies shared/surface-only behavior and emits a successor and rollback map. | Does not cut over, move live files, create junctions, or remove discovery entries. |
| `rigwright-prioritize` | Classify lifecycle eligibility and deterministic routing priority. | Selects at most one eligible canonical owner or reports a collision. | Does not install, enable, discover by folder order, or promote a candidate. |
| `rigwright-archive` | Create and qualify a retained copy packet. | Produces immutable hashes, provenance, successor mapping, and a verified restore. | Does not delete, remove from discovery, mark live state archived, or cut over. |

## Future leaf boundary

| Future leaf | Separate outcome required before implementation | Why it cannot be folded into current leaves |
|---|---|---|
| `rigwright-author-mcp` | Produce one validated MCP server/config with transport, auth, data, tool, and rollback evidence. | Network, auth, server lifecycle, and tool exposure require their own security/eval contract. |
| `rigwright-author-agent` | Produce one bounded agent definition with context and permission policy. | Delegation and permission modes fail independently from skill authoring. |
| `rigwright-author-hook` | Produce one event hook with termination, timeout, and side-effect tests. | Automatic execution has a materially different risk boundary. |
| `rigwright-author-command` | Produce one explicit command interface and argument contract. | User-invoked command semantics differ from implicit skill routing. |
| `rigwright-author-app` | Produce one app manifest/UI integration with auth and privacy evidence. | UI, identity, external data, and app lifecycle are separate concerns. |

No future leaf directory exists in the proposal source. The validator fails if one appears before its gate is opened.
