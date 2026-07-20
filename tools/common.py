from __future__ import annotations

import hashlib
import json
import os
import shutil
import zipfile
from pathlib import Path
from typing import Any, Iterable


def _resolve_root() -> Path:
    """Resolve the repository root the tools operate on.

    Precedence: the RIGWRIGHT_ROOT environment variable, then the tree that
    contains this file (repository checkout layout), then the current working
    directory when it looks like a Rigwright tree. This keeps the tools working
    both as in-repo scripts and as the installed ``rigwright`` package.
    """
    env = os.environ.get("RIGWRIGHT_ROOT")
    if env:
        return Path(env).resolve()
    here = Path(__file__).resolve().parents[1]
    if (here / "src" / "skills").is_dir():
        return here
    cwd = Path.cwd().resolve()
    if (cwd / "src" / "skills").is_dir():
        return cwd
    # An installed package does not contain the repository inputs. Point at
    # the user's actual working directory so validation can fail before any
    # artifact path is created inside site-packages.
    return cwd


ROOT = _resolve_root()


def is_repository_root(path: Path = ROOT) -> bool:
    """Return whether *path* contains the inputs required by repo commands."""
    resolved = path.resolve()
    return all(
        (
            (resolved / "src" / "skills").is_dir(),
            (resolved / "contracts" / "authoring-contract.schema.json").is_file(),
            (resolved / "config" / "release.json").is_file(),
        )
    )


def require_repository_root(path: Path = ROOT) -> Path:
    """Validate a full checkout without creating files or directories."""
    resolved = path.resolve()
    if not is_repository_root(resolved):
        raise ValueError(
            f"Rigwright repository not found at {resolved}. "
            "Run this command from a full Rigwright checkout or set "
            "RIGWRIGHT_ROOT to its absolute path."
        )
    return resolved


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def iter_files(root: Path) -> list[Path]:
    return sorted((path for path in root.rglob("*") if path.is_file()), key=lambda p: p.as_posix().lower())


def file_manifest(root: Path, *, windows_rows: bool = False) -> tuple[list[dict[str, Any]], str, int]:
    rows: list[str] = []
    entries: list[dict[str, Any]] = []
    total_bytes = 0
    for path in iter_files(root):
        rel_posix = path.relative_to(root).as_posix()
        size = path.stat().st_size
        digest = sha256_file(path)
        entries.append({"path": rel_posix, "bytes": size, "sha256": digest})
        rel_for_hash = rel_posix.replace("/", "\\") if windows_rows else rel_posix
        rows.append(f"{rel_for_hash}|{size}|{digest}")
        total_bytes += size
    root_digest = sha256_bytes("\n".join(rows).encode("utf-8"))
    return entries, root_digest, total_bytes


def safe_clear(path: Path, allowed_parent: Path) -> None:
    resolved = path.resolve()
    parent = allowed_parent.resolve()
    if resolved == parent or not resolved.is_relative_to(parent):
        raise ValueError(f"refusing to clear path outside allowed parent: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def deterministic_zip(source_root: Path, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in iter_files(source_root):
            rel = path.relative_to(source_root).as_posix()
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    return sha256_file(destination)


def ensure_unique(values: Iterable[str], label: str) -> None:
    materialized = list(values)
    if len(materialized) != len(set(materialized)):
        raise ValueError(f"duplicate {label}: {materialized}")
