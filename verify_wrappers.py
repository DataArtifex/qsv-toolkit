"""
Verify QSV wrappers against installed QSV binary.
Referenced in AGENTS.md.
"""

from pathlib import Path

from utils.sync_qsv import check_status, print_report

if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent
    status = check_status(repo_root)
    print_report(status)
    if status["version_mismatch"] or status["missing_wrappers"]:
        exit(1)
