# Security and approval model

- Default all source extraction to static reads. Never execute scripts from creator sources, quarantine, or the copy-only archive packet.
- Give every leaf a neutral `side_effect_class`. Proposal writes are limited to an owner-selected proposal root. Live writes require a separate exact approval.
- Do not treat `allowed-tools` as a sandbox. Generated packages pre-authorize no broad shell or provider tools.
- Keep the shared core free of dynamic shell injection. Any future Claude-only lesson injection requires a separate threat review and opt-in adapter decision.
- Reject unsafe or deceptive plugin requests, unauthorized access, exfiltration, fetch-and-execute, bypass-permission modes, broad hooks, and silent marketplace/config edits.
- Break the private-data + untrusted-input + egress trifecta by design. This proposal uses no network, provider, private-data connector, or browser.
- Plugin manifests include no MCP, app, hook, command, agent, auth, or marketplace field unless a separately gated future leaf owns and validates it.
- Archive creation, removal from discovery, lifecycle transition, compatibility alias, live replacement, deletion, and restore are distinct approvals.
- Preserve raw validation failures and record retries. Never convert an unavailable runtime test into a pass.
