#!/usr/bin/env python3
"""Phase 0 integrity checks for canonical data and generated artifacts."""

import argparse
import ast
import csv
import hashlib
import html
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from urllib.parse import urlparse

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "competitive-research-tracker.csv"
XLSX_PATH = ROOT / "data" / "competitive-research-tracker.xlsx"
GENERATOR = ROOT / "tools" / "generate_site.py"
RECONCILIATION_SCRIPT = ROOT / "tools" / "apply_reconciliation.py"
EXPECTED_ROWS = 36
EXPECTED_COLUMNS = 65
LEGACY_FIELDS = {
    "product_overlap_score",
    "feature_maturity_score",
    "market_traction_score",
    "funding_strength_score",
    "ai_depth_score",
    "nda_security_strength_score",
    "network_moat_score",
    "direct_threat_score",
}
RECONCILED_FIELDS = {
    ("Comatch", "total_funding"),
    ("FounderCloud", "hq_country"),
    ("FounderCloud", "notes"),
    ("Gust", "users_traction"),
    ("OpenVC", "users_traction"),
    ("Visible.vc", "hq_country"),
    ("Visible.vc", "total_funding"),
    ("Peachscore", "total_funding"),
    ("Peachscore", "funding_rounds"),
}
PROFILE_FIELDS = {
    "Comatch": ("total_funding",),
    "FounderCloud": ("hq_country", "notes"),
    "Gust": ("users_traction",),
    "OpenVC": ("users_traction",),
    "Visible.vc": ("hq_country", "total_funding"),
    "Peachscore": ("total_funding", "funding_rounds"),
}


class Validation:
    def __init__(self):
        self.failures = []
        self.passes = []

    def check(self, condition, message):
        if condition:
            self.passes.append(message)
        else:
            self.failures.append(message)

    def require(self):
        if self.failures:
            for failure in self.failures:
                print(f"FAIL: {failure}", file=sys.stderr)
            raise SystemExit(1)


def slug(value):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")


def read_canonical():
    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        rows = list(reader)
    return headers, rows


def extract_urls(text):
    return [match.rstrip(").,") for match in re.findall(r"https?://[^\s;]+", text or "")]


def normalized(value):
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def check_canonical(validation, headers, rows):
    validation.check(CSV_PATH.exists(), "canonical CSV exists")
    active_csvs = sorted(path.name for path in (ROOT / "data").glob("*.csv"))
    validation.check(
        active_csvs == [CSV_PATH.name],
        "data/ contains exactly one active CSV source",
    )
    validation.check(len(rows) == EXPECTED_ROWS, "canonical CSV contains 36 companies")
    validation.check(len(headers) == EXPECTED_COLUMNS, "canonical CSV contains 65 columns")
    validation.check(len(headers) == len(set(headers)), "canonical headers are unique")
    companies = [row.get("company", "").strip() for row in rows]
    validation.check(all(companies), "all company identifiers are non-empty")
    validation.check(len(companies) == len(set(companies)), "company identifiers are unique")
    slugs = [slug(company) for company in companies]
    validation.check(len(slugs) == len(set(slugs)), "generated company slugs are unique")

    malformed = []
    for row in rows:
        for field in ("url", "primary_sources", "secondary_sources"):
            value = row.get(field, "")
            found = extract_urls(value)
            if field == "url" and value and not found:
                malformed.append(f"{row['company']}.{field}: {value}")
            for source_url in found:
                parsed = urlparse(source_url)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    malformed.append(f"{row['company']}.{field}: {source_url}")
    validation.check(not malformed, "all stored source links are structurally valid")

    by_company = {row["company"]: row for row in rows}
    missing_audit = []
    for company, field in RECONCILED_FIELDS:
        row = by_company[company]
        has_source = bool(extract_urls(row["primary_sources"] + " " + row["secondary_sources"]))
        explicitly_unverified = any(
            marker in row[field] for marker in ("Unresolved", "Insufficient Evidence", "Company Claim")
        )
        if not (has_source or explicitly_unverified):
            missing_audit.append(f"{company}.{field}")
    validation.check(
        not missing_audit,
        "every reconciled field has a source or explicit unresolved marker",
    )
    legacy_narrative = []
    for row in rows:
        for field, value in row.items():
            if field in LEGACY_FIELDS:
                continue
            for legacy_field in LEGACY_FIELDS:
                if legacy_field in (value or ""):
                    legacy_narrative.append(f"{row['company']}.{field}:{legacy_field}")
    validation.check(
        not legacy_narrative,
        "legacy score names do not appear in active research narratives",
    )
    return by_company


def check_xlsx(validation, headers, rows, required):
    if not XLSX_PATH.exists():
        validation.check(not required, "generated XLSX exists")
        return
    workbook = load_workbook(XLSX_PATH, read_only=True, data_only=True)
    validation.check(
        workbook.sheetnames == ["Competitive Tracker"],
        "XLSX contains the canonical sheet only",
    )
    sheet = workbook["Competitive Tracker"]
    xlsx_rows = [[normalized(cell) for cell in row] for row in sheet.iter_rows(values_only=True)]
    csv_rows = [headers] + [[normalized(row.get(header, "")) for header in headers] for row in rows]
    validation.check(len(xlsx_rows) == EXPECTED_ROWS + 1, "XLSX contains 36 data rows")
    validation.check(
        bool(xlsx_rows) and len(xlsx_rows[0]) == EXPECTED_COLUMNS,
        "XLSX contains 65 columns",
    )
    validation.check(xlsx_rows == csv_rows, "CSV and XLSX match after normalization")
    with zipfile.ZipFile(XLSX_PATH) as package:
        core_properties = package.read("docProps/core.xml")
    fixed_timestamp = b"2026-07-30T00:00:00Z"
    validation.check(
        core_properties.count(fixed_timestamp) == 2,
        "XLSX created and modified metadata use fixed timestamps",
    )


def function_source(path, function_name):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(source, node) or ""
    raise AssertionError(f"Function not found: {function_name}")


def check_scoring(validation, rows, artifacts_required):
    source = function_source(GENERATOR, "relationship_score")
    company_names = [row["company"] for row in rows]
    hardcoded = [name for name in company_names if repr(name) in source or f'"{name}"' in source]
    validation.check(not hardcoded, "scoring contains no hard-coded company-name conditions")
    banned_tokens = (
        "product_overlap_score",
        "feature_maturity_score",
        "market_traction_score",
        "funding_strength_score",
        "ai_depth_score",
        "nda_security_strength_score",
        "network_moat_score",
        "direct_threat_score",
        '"free"',
        "'free'",
    )
    validation.check(
        not any(token in source for token in banned_tokens),
        "relationship score does not consume legacy fields or price keywords",
    )
    validation.check(
        "default" not in source.lower(),
        "relationship score has no numeric missing-data default",
    )
    validation.check(
        '"value": None' in source and '"status": "Insufficient Evidence"' in source,
        "missing score inputs return null / Insufficient Evidence",
    )

    active_code = []
    for base in (ROOT / "tools", ROOT / "sites" / "full-report-site"):
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".js"}:
                active_code.append(path)
    cited_dataset_pattern = re.compile(
        r"bizmatch-competitive-research-cited\.(?:csv|xlsx)"
    )
    cited_refs = []
    for path in active_code:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if cited_dataset_pattern.search(line) and any(
                token in line for token in ("open(", "DictReader", "load_workbook", "read_csv")
            ):
                cited_refs.append(f"{path.relative_to(ROOT)}:{line_number}")
    validation.check(not cited_refs, "active code has no archived cited-dataset reference")

    if not artifacts_required:
        return
    generated_data = (
        ROOT / "sites" / "full-report-site" / "canonical-data.js"
    ).read_text(encoding="utf-8") if (ROOT / "sites" / "full-report-site" / "canonical-data.js").exists() else ""
    ranker_data = (
        ROOT / "sites" / "full-report-site" / "ranker-data.js"
    ).read_text(encoding="utf-8") if (ROOT / "sites" / "full-report-site" / "ranker-data.js").exists() else ""
    validation.check(
        not any(f'"{field}"' in generated_data for field in LEGACY_FIELDS),
        "generated canonical site data excludes all legacy scores",
    )
    validation.check(
        not any(f'"{field}"' in ranker_data for field in LEGACY_FIELDS),
        "active ranker data excludes all legacy scores",
    )
    validation.check(
        not re.search(r'"relationship_score"\s*:\s*(?!null)\d', generated_data),
        "generated relationship scores are null when evidence is insufficient",
    )
    active_pages = [
        ROOT / "sites" / "full-report-site" / name
        for name in (
            "index.html",
            "priority-competitors.html",
            "research-table.html",
            "category-analysis.html",
        )
    ]
    active_pages.extend((ROOT / "sites" / "full-report-site" / "companies").glob("*.html"))
    active_text = "\n".join(
        path.read_text(encoding="utf-8") for path in active_pages if path.exists()
    )
    validation.check(
        not any(f'"{field}"' in active_text or f">{field}<" in active_text for field in LEGACY_FIELDS),
        "active company and analysis pages do not render legacy score fields",
    )
    validation.check(
        not re.search(r"\b(?:High|Medium) threat\b", active_text, flags=re.IGNORECASE),
        "active pages contain no score-derived High/Medium threat labels",
    )


def check_profiles(validation, by_company, required):
    missing = []
    for company, fields in PROFILE_FIELDS.items():
        page = ROOT / "sites" / "full-report-site" / "companies" / f"{slug(company)}.html"
        if not page.exists():
            if required:
                missing.append(f"{company}: page missing")
            continue
        content = page.read_text(encoding="utf-8")
        for field in fields:
            if html.escape(by_company[company][field]) not in content:
                missing.append(f"{company}.{field}")
        if "Insufficient Evidence" not in content or "N/A" not in content:
            missing.append(f"{company}: score status")
    validation.check(not missing, "six reconciled company pages reflect canonical values")


def check_profile_manifest(validation, rows, message):
    expected = {f"{slug(row['company'])}.html" for row in rows}
    company_dir = ROOT / "sites" / "full-report-site" / "companies"
    actual = {path.name for path in company_dir.glob("*.html")}
    validation.check(
        actual == expected,
        message,
    )


def check_investor_facing_strategy(validation, required):
    active = ROOT / "sites" / "full-report-site" / "index.html"
    historical = (
        ROOT
        / "sites"
        / "full-report-site"
        / "strategic-conclusions-historical.html"
    )
    if not active.exists() or not historical.exists():
        validation.check(not required, "strategic recommendations are isolated from the active page")
        return
    active_text = active.read_text(encoding="utf-8")
    historical_text = historical.read_text(encoding="utf-8")
    investor_risk_phrases = (
        "Recommended Israeli Beachhead",
        "Proposed launch sequence",
        "Where BizMatch Can Win",
        "First 100 qualified users",
    )
    validation.check(
        not any(phrase in active_text for phrase in investor_risk_phrases)
        and "No current strategic recommendation is published" in active_text
        and "ARCHIVED — not current investor conclusions" in historical_text,
        "strategic recommendations are isolated from the active page",
    )


def artifact_paths():
    paths = [ROOT / "index.html", ROOT / "START_HERE.html", ROOT / "README.html", XLSX_PATH]
    for base in (
        ROOT / "sites" / "full-report-site",
        ROOT / "sites" / "citation-site",
        ROOT / "reports",
    ):
        paths.extend(
            path
            for path in base.rglob("*")
            if path.is_file() and path.suffix in {".html", ".js", ".md"}
        )
    return sorted(set(paths))


def hashes():
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in artifact_paths()
        if path.exists()
    }


def run_build_twice(validation):
    commands = (
        [sys.executable, str(ROOT / "tools" / "build_xlsx.py")],
        [sys.executable, str(GENERATOR)],
    )
    before = hashes()
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)
    first = hashes()
    time.sleep(2.1)
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)
    second = hashes()
    validation.check(
        first == second,
        "time-separated builds are byte-for-byte deterministic",
    )
    validation.check(
        before == second,
        "checked-in generated artifacts match the deterministic build",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pre-build", action="store_true", help="skip required derived-artifact checks")
    parser.add_argument("--check-build", action="store_true", help="run the build twice and compare hashes")
    args = parser.parse_args()

    validation = Validation()
    headers, rows = read_canonical()
    by_company = check_canonical(validation, headers, rows)
    check_scoring(validation, rows, artifacts_required=not args.pre_build)
    if not args.pre_build:
        check_profile_manifest(
            validation,
            rows,
            "company profile directory contains exactly the canonical profiles",
        )
        check_investor_facing_strategy(validation, required=True)
    if args.check_build:
        run_build_twice(validation)
        check_profile_manifest(
            validation,
            rows,
            "site build emits no extra company-profile files",
        )
    if not args.pre_build:
        check_xlsx(validation, headers, rows, required=True)
        check_profiles(validation, by_company, required=True)
    validation.require()
    print(f"PASS: {len(validation.passes)} integrity checks")
    for message in validation.passes:
        print(f"  - {message}")


if __name__ == "__main__":
    main()
