"""
This script is a utility designed to automate the generation of reference documentation for
qsv commands supported by the qsv-toolkit.

Overview:
The script extracts help documentation directly from the qsv CLI and formats it into
Markdown for easy viewing and hosting.

Key Features:
- Documentation Extraction: Iterates through all commands registered in the QSV class
  and captures their standard help output.
- Individual Command Files: Generates a dedicated .md file for each command
  (e.g., count.md, stats.md) containing its full usage information.
- Consolidated Reference: Creates a single ALL.md file that aggregates the help text
  for every command into one searchable document.
- Customizable Output: Supports an --output argument to specify where the generated
  documentation should be saved (defaulting to the references/cmd directory).

Usage:
python utils/cmd_references.py --output ./docs/commands
"""
import argparse
import os

from dartfx.qsv.cmd import QSV

def main():
    all_in_one_md = "# QSV Commands\n\n"

    # collect all help outputs
    cmd_help = {}
    for cmd in QSV.commands():
        cmd_help[cmd.name()] = cmd.help()

    # write all help outputs to files
    for cmd_name, help_txt in cmd_help.items():
        cmd_filename = os.path.join(args.output, f"{cmd_name}.md")
        md = f"# {cmd_name}\n\n"
        md += f"```text\n"
        md += help_txt
        md += f"```\n"
        with open(cmd_filename, "w") as f:
            f.write(md)

    # write all help outputs to a single file
    all_in_one_md += "# QSV Commands\n\n"
    for cmd_name, help_txt in cmd_help.items():
        all_in_one_md += f"## {cmd_name}\n\n"
        all_in_one_md += f"```text\n"
        all_in_one_md += help_txt
        all_in_one_md += f"```\n"
    with open(os.path.join(args.output, "ALL.md"), "w") as f:
        f.write(all_in_one_md)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default=os.path.join(os.path.dirname(__file__), "..", "references", "cmd"), help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    main()
