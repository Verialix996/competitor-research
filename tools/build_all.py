#!/usr/bin/env python3
"""Run the canonical validation -> XLSX -> site -> validation flow."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script, *args):
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / script), *args],
        cwd=ROOT,
        check=True,
    )


def main():
    run("validate_data.py", "--pre-build")
    run("build_xlsx.py")
    run("build_substitute_reports.py")
    run("generate_site.py")
    run("validate_data.py")
    print("Canonical Phase 0 + Phase 1 build completed successfully")


if __name__ == "__main__":
    main()
