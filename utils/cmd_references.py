"""
This script is a utility designed to automate the generation of reference documentation for
all commands available in the current QSV binary.

Overview:
The script extracts help documentation directly from the qsv CLI and formats it into
Markdown for easy viewing and hosting.

Key Features:
- Documentation Extraction: Iterates through all commands reported by `qsv --list`
  (via QSV.list()) and captures their standard help output.
- Version Alignment: Automatically extracts the current QSV version for documentation headers.
- Individual Command Files: Generates a dedicated .md file for each command
  (e.g., count.md, stats.md) containing its full usage information.
- Consolidated Reference: Creates a single ALL.md file that aggregates the help text
  for every command into one searchable document.
- Customizable Output: Supports an --output argument to specify where the generated
  documentation should be saved (defaulting to the references/cmd directory).

Usage:
PYTHONPATH=src python utils/cmd_references.py
PYTHONPATH=src python utils/cmd_references.py --output ./docs/commands
"""

import argparse
import os

from dartfx.qsv.cmd import QSV


def main(args: argparse.Namespace) -> None:

    # Version
    qsv_version = QSV.version_number()

    # collect all help outputs
    print(f"Collecting all help outputs for {qsv_version}")
    cmd_help: dict[str, str] = {}
    import subprocess

    for cmd_info in QSV.list():
        name = cmd_info["name"]
        help_txt = subprocess.run(["qsv", name, "--help"], capture_output=True, text=True).stdout
        cmd_help[name] = help_txt

    # write all help outputs to files
    print(f"Writing all help outputs to files in {args.output}")
    for cmd_name, help_txt in cmd_help.items():
        cmd_filename = os.path.join(args.output, f"{cmd_name}.md")
        md = f"# qsv {cmd_name}\n\n"
        md += f"<small>v{qsv_version}</small>\n\n"
        md += "```text\n"
        md += help_txt
        md += "```\n"
        with open(cmd_filename, "w") as f:
            f.write(md)

    # write all help outputs to a single file
    print(f"Writing all help outputs to a single file: {os.path.join(args.output, 'ALL.md')}")
    all_in_one_md = "# QSV Commands\n\n"
    all_in_one_md += f"<small>v{qsv_version}</small>\n\n"
    for cmd_name, help_txt in cmd_help.items():
        all_in_one_md += f"## qsv {cmd_name}\n\n"
        all_in_one_md += "```text\n"
        all_in_one_md += help_txt
        all_in_one_md += "```\n"
    with open(os.path.join(args.output, "ALL.md"), "w") as f:
        f.write(all_in_one_md)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        default=os.path.join(os.path.dirname(__file__), "..", "references", "cmd"),
        help="Output directory",
    )
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    main(args)
