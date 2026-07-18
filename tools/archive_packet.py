"""Create and qualify a copy-only archive packet for a live skill directory.

The packet copies the source byte for byte, hashes every file, writes a
restore plan, and proves an isolated restore reproduces the exact manifest.
It never modifies the live source and never marks anything archived.

The source is path-configurable: pass ``--source`` explicitly. Without it the
tool skips cleanly so the offline gate can run on a clean public checkout.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

try:
    from .common import ROOT, file_manifest, safe_clear, write_json
except ImportError:  # direct script execution
    from common import ROOT, file_manifest, safe_clear, write_json


PACKET_ROOT = ROOT / "artifacts" / "archive-proposals"


def create_packet(source: Path, name: str | None = None, output: Path | None = None) -> dict:
    source = source.resolve()
    if not source.is_dir():
        raise SystemExit(f"archive source is not a directory: {source}")
    packet_name = name or f"{source.name}-copy-only"
    packet = (output or PACKET_ROOT / packet_name).resolve()
    safe_clear(packet, PACKET_ROOT)
    payload_root = packet / "payload" / source.name
    restore_root = packet / "restore-test" / source.name
    payload_root.mkdir(parents=True, exist_ok=True)
    for source_path in sorted((path for path in source.rglob("*") if path.is_file()), key=lambda p: p.as_posix().lower()):
        relative = source_path.relative_to(source)
        destination = payload_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination)
    payload_files, payload_sha, payload_bytes = file_manifest(payload_root)
    source_files, source_sha, source_bytes = file_manifest(source)
    if payload_files != source_files or payload_sha != source_sha or payload_bytes != source_bytes:
        raise SystemExit("copy-only archive payload does not match live source")

    write_json(packet / "manifest.json", {
        "schema_version": 1,
        "proposal_state": "copy-only-not-archived",
        "source_name": source.name,
        "live_source_modified": False,
        "file_count": len(payload_files),
        "total_bytes": payload_bytes,
        "payload_root_sha256": payload_sha,
        "files": payload_files,
    })
    (packet / "SHA256SUMS.txt").write_text(
        "".join(f"{item['sha256']}  payload/{source.name}/{item['path']}\n" for item in payload_files),
        encoding="utf-8",
        newline="\n",
    )

    shutil.copytree(payload_root, restore_root)
    restore_files, restore_sha, restore_bytes = file_manifest(restore_root)
    restore_ok = restore_files == payload_files and restore_sha == payload_sha and restore_bytes == payload_bytes
    restore_report = {
        "schema_version": 1,
        "status": "PASS" if restore_ok else "FAIL",
        "isolated_restore_root": restore_root.relative_to(ROOT).as_posix(),
        "file_count": len(restore_files),
        "total_bytes": restore_bytes,
        "root_sha256": restore_sha,
        "missing": [],
        "extra": [],
        "changed": []
    }
    write_json(packet / "restore-test" / "report.json", restore_report)
    (packet / "RESTORE-PLAN.md").write_text(
        "# Proposed restore procedure\n\n"
        "1. Select a new isolated destination; never overwrite a live skill during qualification.\n"
        f"2. Copy `payload/{source.name}` byte for byte.\n"
        "3. Compare every relative path, byte length, and SHA-256 with `manifest.json`.\n"
        "4. Fail on any missing, extra, or changed file.\n"
        "5. A later live restore requires separate approval and discovery-state readback.\n",
        encoding="utf-8",
        newline="\n",
    )
    if not restore_ok:
        raise SystemExit("archive restore qualification failed")
    return {"status": "PASS", "file_count": len(payload_files), "total_bytes": payload_bytes, "payload_root_sha256": payload_sha, "restore_root_sha256": restore_sha}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="live skill directory to copy (read-only)")
    parser.add_argument("--name", help="packet directory name (default: <source>-copy-only)")
    args = parser.parse_args()
    if args.source is None:
        print("archive packet skipped: pass --source <live-skill-directory> to create a copy-only packet")
        return
    result = create_packet(args.source, args.name)
    print(f"archive restore passed: {result['file_count']} files, {result['payload_root_sha256']}")


if __name__ == "__main__":
    main()
