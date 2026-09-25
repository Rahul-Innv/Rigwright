# Security policy

Rigwright's offline CLI version `0.2.0` is public on PyPI. This policy does not designate a
publicly supported version. No generated skill or plugin package is approved for installation or
marketplace distribution.

## Reporting

Do not disclose a suspected vulnerability, credential, private path, or raw provider record in a public issue. The project does not yet have a dedicated public security-reporting channel; until one is designated, use the repository host's private vulnerability-reporting feature or a private channel with the repository owner.

The absence of a public reporting contact is a launch blocker, not permission to publish sensitive details.

## Security boundaries

- Source extraction is static. Copied source and archive scripts are never executed for provenance inspection.
- Candidate output is limited to the repository's own `artifacts/` tree.
- Normal builds exclude candidate and inactive lifecycle states.
- Generated packages do not pre-authorize broad shell, provider, authentication, marketplace, hook, MCP, app, agent, or command behavior.
- Archive creation, discovery removal, lifecycle transition, replacement, deletion, and restore are separate operations with separate approvals.
- An external lifecycle authority owns lifecycle and routing priority; Rigwright does not mutate that authority.

## Include in a private report

- the affected leaf, adapter, contract, or validator;
- the exact commit and minimal reproduction;
- expected and observed behavior;
- whether credentials, private data, egress, automatic execution, or permission bypass is involved; and
- any temporary containment already applied.

Do not include live credentials. Revoke or rotate an exposed credential through its provider rather than transmitting it with the report.
