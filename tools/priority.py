from __future__ import annotations

from datetime import date
from typing import Any


INELIGIBLE_STATES = {"archived-retained", "quarantined-untrusted", "rejected"}


def _date_rank(raw: str) -> int:
    return date.fromisoformat(raw).toordinal()


def _matches(record: dict[str, Any], context: dict[str, Any]) -> bool:
    return (
        record.get("intent_key") == context.get("intent_key")
        and context.get("surface") in record.get("surfaces", [])
        and record.get("available", True)
        and record.get("authorized", True)
    )


def select_owner(records: list[dict[str, Any]], context: dict[str, Any]) -> dict[str, Any]:
    matching = [record for record in records if _matches(record, context)]
    current_keys: dict[tuple[str, str, str], list[str]] = {}
    for record in matching:
        if record.get("state") == "current-authorized":
            key = (record["intent_key"], record.get("scope", "cross-platform"), context["surface"])
            current_keys.setdefault(key, []).append(record["id"])
    collisions = {"|".join(key): ids for key, ids in current_keys.items() if len(ids) > 1}
    if collisions:
        return {"status": "COLLISION", "selected": None, "collisions": collisions, "excluded": []}

    sandbox_target = context.get("sandbox_target")
    if context.get("sandbox") and sandbox_target:
        target = next((record for record in matching if record["id"] == sandbox_target and record.get("state") == "candidate-sandbox"), None)
        if target:
            return {"status": "SELECTED_SANDBOX_TARGET", "selected": target["id"], "reason": "explicit candidate sandbox target", "excluded": []}

    ranked: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    excluded: list[dict[str, str]] = []
    for record in matching:
        state = record.get("state")
        reason = None
        category = None
        if state in INELIGIBLE_STATES:
            reason = f"state {state} is never eligible"
        elif state == "candidate-sandbox":
            reason = "candidate requires explicit sandbox_target and cannot auto-rank"
        elif state == "compatibility-alias":
            if not context.get("legacy_invocation"):
                reason = "alias requires explicit legacy invocation"
            elif context.get("successor_satisfiable", True):
                reason = "authorized successor satisfies legacy invocation"
            else:
                category = 4
        elif state == "current-authorized":
            if record["id"] == context.get("explicit_owner"):
                category = 0
            elif record.get("project_match"):
                category = 1
            else:
                category = 2
        else:
            reason = f"unknown lifecycle state {state}"
        if reason:
            excluded.append({"id": record["id"], "reason": reason})
            continue
        rank = (
            category,
            -int(record.get("specificity", 0)),
            -_date_rank(record.get("evidence_date", "1970-01-01")),
            int(record.get("context_cost", 0)),
            record["id"],
        )
        ranked.append((rank, record))
    if not ranked:
        return {"status": "NO_ELIGIBLE_OWNER", "selected": None, "excluded": excluded}
    ranked.sort(key=lambda item: item[0])
    winner = ranked[0][1]
    return {"status": "SELECTED", "selected": winner["id"], "rank": list(ranked[0][0]), "excluded": excluded}
