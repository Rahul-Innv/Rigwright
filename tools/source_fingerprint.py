"""Optional provenance fingerprinting for frozen upstream source roots.

This tool is path-configurable and disabled by default. To enable it, copy
``config/sources.example.json`` to ``config/sources.json`` and point each
``path`` at a readable local source root. The first run captures a stability
baseline under ``artifacts/provenance/stability-window.json``; later runs
verify the live roots against that frozen baseline and fail on drift.

Without ``config/sources.json`` the tool skips cleanly so the offline gate can
run on a clean public checkout.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

try:
    from .common import ROOT, file_manifest, load_json, write_json
except ImportError:  # direct script execution
    from common import ROOT, file_manifest, load_json, write_json


CONFIG = ROOT / "config" / "sources.json"
STABILITY = ROOT / "artifacts" / "provenance" / "stability-window.json"
ALGORITHM = "sha256 over 'path|bytes|sha256' rows (posix relative paths)"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _capture(sources: list[dict]) -> dict:
    roots = []
    for source in sources:
        source_root = Path(source["path"])
        if not source_root.is_dir():
            raise FileNotFoundError(f"source root missing: {source_root}")
        files, root_sha, total_bytes = file_manifest(source_root)
        roots.append({
            "id": source["id"],
            "file_count": len(files),
            "total_bytes": total_bytes,
            "sha256": root_sha,
        })
    payload = {
        "schema_version": 1,
        "captured_utc": _utc_now(),
        "algorithm": ALGORITHM,
        "roots": roots,
    }
    write_json(STABILITY, payload)
    return payload


def generate(output: Path | None = None) -> dict | None:
    if not CONFIG.is_file():
        print("source fingerprint skipped: no config/sources.json (copy config/sources.example.json and set local paths)")
        return None
    config = load_json(CONFIG)
    if not STABILITY.is_file():
        baseline = _capture(config["sources"])
        print(f"source fingerprint baseline captured: {len(baseline['roots'])} roots -> {STABILITY.relative_to(ROOT).as_posix()}")
        return baseline
    stability = load_json(STABILITY)
    stable_by_id = {item["id"]: item for item in stability["roots"]}
    sources = []
    mismatches = []
    for source in config["sources"]:
        source_root = Path(source["path"])
        if not source_root.is_dir():
            raise FileNotFoundError(f"source root missing: {source_root}")
        files, root_sha, total_bytes = file_manifest(source_root)
        stable = stable_by_id.get(source["id"])
        if stable is None:
            mismatches.append({"id": source["id"], "expected": None, "actual": {"file_count": len(files), "total_bytes": total_bytes, "sha256": root_sha}})
        elif (len(files), total_bytes, root_sha) != (stable["file_count"], stable["total_bytes"], stable["sha256"]):
            mismatches.append({"id": source["id"], "expected": stable, "actual": {"file_count": len(files), "total_bytes": total_bytes, "sha256": root_sha}})
        sources.append({
            **source,
            "file_count": len(files),
            "total_bytes": total_bytes,
            "root_sha256": root_sha,
            "files": files,
        })
    payload = {
        "schema_version": 1,
        "captured_utc": _utc_now(),
        "algorithm": stability.get("algorithm", ALGORITHM),
        "stability_status": "stable" if not mismatches else "CONCURRENTLY-CHANGING",
        "mismatches": mismatches,
        "sources": sources,
    }
    target = output or ROOT / "artifacts" / "provenance" / "source-manifest.json"
    write_json(target, payload)
    if mismatches:
        raise SystemExit(f"source drift detected in {len(mismatches)} root(s); see {target}")
    return payload


if __name__ == "__main__":
    result = generate()
    if result is not None and "sources" in result:
        print(f"source fingerprint passed: {len(result['sources'])} stable roots")
