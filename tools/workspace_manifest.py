from __future__ import annotations

from pathlib import Path

try:
    from .common import ROOT, file_manifest, write_json
except ImportError:  # direct script execution
    from common import ROOT, file_manifest, write_json


OUTPUT = ROOT / "artifacts" / "validation" / "changed-files.json"
TREE = ROOT / "artifacts" / "validation" / "proposal-tree.txt"


def generate() -> dict:
    output_rel = OUTPUT.relative_to(ROOT).as_posix()
    tree_rel = TREE.relative_to(ROOT).as_posix()
    tree_paths = sorted(
        {
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file() and path != OUTPUT and ".git" not in path.relative_to(ROOT).parts
        }
        | {tree_rel},
        key=str.lower,
    )
    TREE.parent.mkdir(parents=True, exist_ok=True)
    TREE.write_text("\n".join(tree_paths) + "\n", encoding="utf-8", newline="\n")

    entries, _, _ = file_manifest(ROOT)
    entries = [
        item
        for item in entries
        if item["path"] != output_rel and not item["path"].startswith(".git/")
    ]
    rows = "\n".join(f"{item['path']}|{item['bytes']}|{item['sha256']}" for item in entries)
    import hashlib
    digest = hashlib.sha256(rows.encode("utf-8")).hexdigest()
    payload = {
        "schema_version": 1,
        "root": ROOT.name,
        "self_excluded": output_rel,
        "proposal_tree": tree_rel,
        "file_count": len(entries),
        "total_bytes": sum(item["bytes"] for item in entries),
        "aggregate_sha256": digest,
        "files": entries,
    }
    write_json(OUTPUT, payload)
    return payload


if __name__ == "__main__":
    result = generate()
    print(f"workspace manifest written: {result['file_count']} files, {result['aggregate_sha256']}")
