"""
Utility script to check, synchronize, and update dartfx-qsv when a new version of QSV is available.

Usage:
    uv run python utils/sync_qsv.py          # Check status (dry run)
    uv run python utils/sync_qsv.py --check  # Check status (dry run)
    uv run python utils/sync_qsv.py --update # Update cmd.py, references, and version
    uv run python utils/sync_qsv.py --all    # Full update + rebuild docs + run test suite
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def get_installed_qsv_version() -> tuple[str, str]:
    """Returns (version_number, full_version_string)."""
    if shutil.which("qsv") is None:
        raise RuntimeError("qsv executable not found in PATH.")
    output = subprocess.run(["qsv", "--version"], capture_output=True, text=True, check=True).stdout.strip()
    match = re.search(r"qsv\s+([\d\.]+)", output)
    version_num = match.group(1) if match else "unknown"
    return version_num, output


def get_current_package_version(repo_root: Path) -> str:
    about_path = repo_root / "src" / "dartfx" / "qsv" / "__about__.py"
    if not about_path.exists():
        return "unknown"
    content = about_path.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    return match.group(1) if match else "unknown"


def get_qsv_commands_from_cli() -> dict[str, str]:
    """Returns a dict mapping command_name -> short_description from `qsv --list`."""
    output = subprocess.run(["qsv", "--list"], capture_output=True, text=True, check=True).stdout
    commands = {}
    started = False
    for line in output.splitlines():
        if "Installed commands" in line:
            started = True
            continue
        if started and line.startswith("    "):
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                commands[parts[0]] = parts[1]
        elif started and line.strip() == "":
            if commands:
                break
    return commands


def get_wrapped_classes() -> dict[str, type]:
    """Imports dartfx.qsv.cmd and returns wrapped command classes."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
    from dartfx.qsv.cmd import QSV, QSVCommand

    subclasses = {cls.name(): cls for cls in QSVCommand.__subclasses__() if cls is not QSV}
    return subclasses


def check_status(repo_root: Path) -> dict:
    version_num, full_version = get_installed_qsv_version()
    pkg_version = get_current_package_version(repo_root)
    cli_commands = get_qsv_commands_from_cli()
    wrapped_classes = get_wrapped_classes()

    missing_wrappers = sorted(set(cli_commands.keys()) - set(wrapped_classes.keys()))
    extra_wrappers = sorted(set(wrapped_classes.keys()) - set(cli_commands.keys()))

    docstring_diffs = {}
    for name, desc in cli_commands.items():
        if name in wrapped_classes:
            cls = wrapped_classes[name]
            cls_doc = (cls.__doc__ or "").strip().rstrip(".")
            cli_doc = desc.strip().rstrip(".")
            if cls_doc != cli_doc:
                docstring_diffs[name] = {"class_doc": cls.__doc__, "cli_desc": desc}

    return {
        "installed_version": version_num,
        "full_installed_version": full_version,
        "pkg_version": pkg_version,
        "version_mismatch": version_num != pkg_version,
        "cli_command_count": len(cli_commands),
        "wrapped_class_count": len(wrapped_classes),
        "missing_wrappers": missing_wrappers,
        "extra_wrappers": extra_wrappers,
        "docstring_diffs": docstring_diffs,
    }


def print_report(status: dict) -> None:
    print("=" * 60)
    print(" QSV Toolkit Sync Status Report")
    print("=" * 60)
    print(f"Installed QSV Version : {status['installed_version']}")
    print(f"Toolkit Package Version: {status['pkg_version']}")
    if status["version_mismatch"]:
        print("  -> VERSION MISMATCH: Package should be updated!")
    else:
        print("  -> Version matches.")

    print(f"\nInstalled QSV Commands: {status['cli_command_count']}")
    print(f"Wrapped Python Classes: {status['wrapped_class_count']}")

    if status["missing_wrappers"]:
        print(f"\n[!] Missing command wrappers ({len(status['missing_wrappers'])}):")
        for cmd in status["missing_wrappers"]:
            print(f"    - {cmd}")
    else:
        print("\n[✓] All installed QSV commands have Python wrappers.")

    if status["extra_wrappers"]:
        print(f"\n[-] Extra / Legacy wrappers not in current QSV binary ({len(status['extra_wrappers'])}):")
        for cmd in status["extra_wrappers"]:
            print(f"    - {cmd} (retained for backward compatibility)")

    if status["docstring_diffs"]:
        print(f"\n[~] Commands with updated descriptions ({len(status['docstring_diffs'])}):")
        for cmd, diff in status["docstring_diffs"].items():
            print(f"    - {cmd}: '{diff['class_doc']}' -> '{diff['cli_desc']}'")

    print("=" * 60)


def update_package_version(repo_root: Path, new_version: str) -> None:
    about_path = repo_root / "src" / "dartfx" / "qsv" / "__about__.py"
    content = about_path.read_text(encoding="utf-8")
    new_content = re.sub(
        r'__version__\s*=\s*["\']([^"\']+)["\']',
        f'__version__ = "{new_version}"',
        content,
    )
    about_path.write_text(new_content, encoding="utf-8")
    print(f"Updated {about_path} version to {new_version}")


def update_references(repo_root: Path) -> None:
    print("Regenerating references in references/cmd/...")
    cmd_ref_script = repo_root / "utils" / "cmd_references.py"
    subprocess.run([sys.executable, str(cmd_ref_script)], check=True)


def rebuild_docs(repo_root: Path) -> None:
    print("Rebuilding Sphinx HTML documentation...")
    docs_source = repo_root / "docs" / "source"
    docs_build = repo_root / "docs" / "build" / "html"
    subprocess.run(["sphinx-build", "-b", "html", str(docs_source), str(docs_build)], check=True)


def run_tests(repo_root: Path) -> None:
    print("Running pytest test suite...")
    subprocess.run(["pytest"], cwd=repo_root, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check or sync QSV toolkit with installed QSV CLI version.")
    parser.add_argument("--check", action="store_true", help="Check status and report diffs without making changes.")
    parser.add_argument("--update", action="store_true", help="Update version, command references, and docs.")
    parser.add_argument("--test", action="store_true", help="Run pytest after sync.")
    parser.add_argument("--docs", action="store_true", help="Rebuild Sphinx documentation.")
    parser.add_argument(
        "--all", action="store_true", help="Perform full sync: update version, references, docs, format, and test."
    )

    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent

    # Default action if no arguments provided is --check
    if not any([args.check, args.update, args.test, args.docs, args.all]):
        args.check = True

    status = check_status(repo_root)
    print_report(status)

    if args.check and not (args.update or args.all or args.docs or args.test):
        if status["version_mismatch"] or status["missing_wrappers"]:
            print("\nTip: Run with '--update' or '--all' to synchronize automatically.")
            sys.exit(1)
        else:
            print("\nToolkit is up to date!")
            sys.exit(0)

    if args.update or args.all:
        if status["version_mismatch"]:
            update_package_version(repo_root, status["installed_version"])
        update_references(repo_root)

    if args.docs or args.all:
        rebuild_docs(repo_root)

    if args.all:
        print("Formatting code with ruff...")
        subprocess.run(["ruff", "format"], check=False)

    if args.test or args.all:
        run_tests(repo_root)

    print("\n[✓] QSV synchronization complete!")


if __name__ == "__main__":
    main()
