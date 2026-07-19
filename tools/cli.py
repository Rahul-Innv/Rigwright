"""Rigwright command-line interface.

Exposes the offline proposal tools as subcommands of one ``rigwright``
entry point. Every subcommand operates on the repository tree resolved by
``common.ROOT`` (override with the ``RIGWRIGHT_ROOT`` environment variable).
"""
from __future__ import annotations

import sys

try:
    from .common import require_repository_root
except ImportError:  # direct script execution
    from common import require_repository_root

try:
    from . import (
        archive_packet,
        build_adapters,
        run_all,
        run_evals,
        source_fingerprint,
        validate_contract,
        validate_packages,
        validate_runtime_fixtures,
        verify_determinism,
        workspace_manifest,
    )
except ImportError:  # direct script execution
    import archive_packet
    import build_adapters
    import run_all
    import run_evals
    import source_fingerprint
    import validate_contract
    import validate_packages
    import validate_runtime_fixtures
    import verify_determinism
    import workspace_manifest


def _evals() -> None:
    result = run_evals.run()
    print(f"offline evals passed: {result['assertions']} assertions, {result['near_miss_cases']} near misses, {result['fixed_task_count']} fixed tasks")


def _contract() -> None:
    result = validate_contract.validate_all()
    print(f"contract validation passed: {result['checks']} checks, {result['leaf_count']} leaves, {result['eval_case_count']} eval cases")


def _packages() -> None:
    result = validate_packages.validate()
    print(f"package validation passed: {result['checks']} checks")


def _determinism() -> None:
    result = verify_determinism.verify()
    print(f"determinism passed: {len(result['comparisons'])} surface packages")


def _fixtures() -> None:
    result = validate_runtime_fixtures.validate()
    print(
        "runtime fixtures passed: "
        f"{result['task_count']} tasks, {result['condition_count']} conditions, "
        f"{result['replicates_per_condition']} replicates, {result['fixture_sha256']}"
    )


def _manifest() -> None:
    result = workspace_manifest.generate()
    print(f"workspace manifest written: {result['file_count']} files, {result['aggregate_sha256']}")


def _fingerprint() -> None:
    result = source_fingerprint.generate()
    if result is not None and "sources" in result:
        print(f"source fingerprint passed: {len(result['sources'])} stable roots")


COMMANDS: dict[str, tuple[str, object]] = {
    "gate": ("run the complete offline proposal gate", run_all.main),
    "validate-contract": ("validate contracts, leaves, and eval sets", _contract),
    "build-adapters": ("build surface adapter packages (pass --mode)", build_adapters.main),
    "validate-packages": ("validate generated candidate packages", _packages),
    "determinism": ("prove byte-identical rebuilds", _determinism),
    "validate-fixtures": ("validate frozen runtime eval fixtures", _fixtures),
    "run-evals": ("run the deterministic offline evals", _evals),
    "fingerprint": ("capture or verify configured source fingerprints", _fingerprint),
    "archive-packet": ("create a copy-only archive packet (pass --source)", archive_packet.main),
    "manifest": ("write the workspace file manifest", _manifest),
}


def _usage() -> str:
    lines = ["usage: rigwright <command> [args]", "", "commands:"]
    lines.extend(f"  {name:<20} {help_text}" for name, (help_text, _) in COMMANDS.items())
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help", "help"}:
        print(_usage())
        return 0
    command = args[0]
    if command not in COMMANDS:
        print(f"unknown command: {command}\n\n{_usage()}", file=sys.stderr)
        return 2
    try:
        require_repository_root()
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    sys.argv = [f"rigwright {command}", *args[1:]]
    _, handler = COMMANDS[command]
    try:
        handler()  # type: ignore[operator]
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        print(code, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
