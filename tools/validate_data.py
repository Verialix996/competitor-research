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
SUBSTITUTES_PATH = ROOT / "data" / "substitutes-research.csv"
SUBSTITUTE_EVIDENCE_PATH = ROOT / "data" / "substitute-evidence.csv"
SUBSTITUTE_WORKFLOWS_PATH = ROOT / "data" / "substitute-workflows.csv"
SUBSTITUTE_REPORT_SCRIPT = ROOT / "tools" / "build_substitute_reports.py"
GENERATOR = ROOT / "tools" / "generate_site.py"
RECONCILIATION_SCRIPT = ROOT / "tools" / "apply_reconciliation.py"
EXPECTED_ROWS = 36
EXPECTED_COLUMNS = 65
SUBSTITUTE_JOB_IDS = {
    "JOB-COFOUNDER",
    "JOB-FOUNDER-INVESTOR",
    "JOB-INVESTOR-SOURCING",
    "JOB-TRUSTED-PROGRESSION",
}
SUBSTITUTE_CLASSIFICATIONS = {
    "Direct Competitor",
    "Adjacent Competitor",
    "Workflow Substitute",
    "Service Substitute",
    "Community/Network Substitute",
    "Manual Process",
    "Do Nothing",
    "Infrastructure Tool",
    "Unclear",
}
SUBSTITUTE_STRENGTHS = {
    "Strong Substitute",
    "Partial Substitute",
    "Weak Substitute",
    "Complementary Tool",
    "Insufficient Evidence",
}
SUBSTITUTE_SOURCE_TYPES = {
    "Independent Behavioral Evidence",
    "Independent User Report",
    "Independent Market Evidence",
    "Company Documentation",
    "Company Claim",
    "Community Discussion",
    "Anecdotal Evidence",
    "Inference",
    "Unverified",
}
SUBSTITUTE_HEADERS = (
    "substitute_id",
    "name",
    "category",
    "classification",
    "target_persona",
    "job_to_be_done",
    "workflow_stages_covered",
    "current_behavior",
    "why_users_choose_it",
    "advantages",
    "limitations",
    "switching_cost",
    "trust_mechanism",
    "payment_model",
    "substitute_strength",
    "evidence_summary",
    "evidence_ids",
    "source_url",
    "source_title",
    "source_type",
    "source_date",
    "last_verified",
    "confidence",
    "research_status",
    "existing_competitor_slug",
    "notes",
)
SUBSTITUTE_EVIDENCE_HEADERS = (
    "evidence_id",
    "substitute_id",
    "job_id",
    "claim_type",
    "evidence_dimension",
    "claim",
    "source_url",
    "source_title",
    "source_date",
    "last_verified",
    "source_type",
    "supporting_excerpt_or_summary",
    "confidence",
    "limitation",
)
SUBSTITUTE_WORKFLOW_HEADERS = (
    "workflow_id",
    "job_id",
    "stage_id",
    "stage_order",
    "current_action",
    "tools_channels",
    "people_involved",
    "manual_work",
    "time_or_friction",
    "trust_requirement",
    "current_advantage",
    "current_limitation",
    "substitute_ids",
    "evidence_ids",
    "evidence_status",
    "confidence",
)
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


def read_csv_table(path):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return tuple(reader.fieldnames or ()), list(reader)


def split_values(value):
    return [item.strip() for item in (value or "").split("|") if item.strip()]


def normalized_name(value):
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


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
    expected_csvs = sorted(
        (
            CSV_PATH.name,
            SUBSTITUTES_PATH.name,
            SUBSTITUTE_EVIDENCE_PATH.name,
            SUBSTITUTE_WORKFLOWS_PATH.name,
        )
    )
    validation.check(
        active_csvs == expected_csvs,
        "data/ contains only the separated canonical competitor and substitute CSV layers",
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


def check_substitutes(validation, competitor_rows, artifacts_required):
    tables = (
        (SUBSTITUTES_PATH, SUBSTITUTE_HEADERS),
        (SUBSTITUTE_EVIDENCE_PATH, SUBSTITUTE_EVIDENCE_HEADERS),
        (SUBSTITUTE_WORKFLOWS_PATH, SUBSTITUTE_WORKFLOW_HEADERS),
    )
    loaded = {}
    for path, expected_headers in tables:
        validation.check(path.exists(), f"{path.name} exists")
        headers, rows = read_csv_table(path)
        loaded[path] = (headers, rows)
        validation.check(
            headers == expected_headers,
            f"{path.name} uses the documented canonical schema and column order",
        )
        validation.check(
            len(headers) == len(set(headers)),
            f"{path.name} has unique headers",
        )

    substitute_headers, substitutes = loaded[SUBSTITUTES_PATH]
    evidence_headers, evidence = loaded[SUBSTITUTE_EVIDENCE_PATH]
    workflow_headers, workflows = loaded[SUBSTITUTE_WORKFLOWS_PATH]
    del substitute_headers, evidence_headers, workflow_headers

    substitute_ids = [row["substitute_id"].strip() for row in substitutes]
    names = [row["name"].strip() for row in substitutes]
    normalized_names = [normalized_name(name) for name in names]
    validation.check(
        all(substitute_ids) and len(substitute_ids) == len(set(substitute_ids)),
        "substitute identifiers are non-empty and unique",
    )
    validation.check(
        all(names) and len(normalized_names) == len(set(normalized_names)),
        "substitute names remain unique after punctuation and case normalization",
    )
    validation.check(
        all(row["classification"] in SUBSTITUTE_CLASSIFICATIONS for row in substitutes),
        "every substitute has an allowed classification",
    )
    validation.check(
        all(
            split_values(row["job_to_be_done"])
            and set(split_values(row["job_to_be_done"])) <= SUBSTITUTE_JOB_IDS
            for row in substitutes
        ),
        "every substitute links to one or more allowed Jobs",
    )
    validation.check(
        all(row["substitute_strength"] in SUBSTITUTE_STRENGTHS for row in substitutes),
        "substitute strength is qualitative and uses only the documented categories",
    )
    validation.check(
        not any("score" in header.lower() for header in SUBSTITUTE_HEADERS),
        "substitute entity schema contains no numeric score field",
    )

    competitor_slugs = {slug(row["company"]): row["company"] for row in competitor_rows}
    linked_errors = []
    for row in substitutes:
        link_slug = row["existing_competitor_slug"].strip()
        name_slug = slug(row["name"].split(" such as ")[0])
        if link_slug and link_slug not in competitor_slugs:
            linked_errors.append(f"{row['substitute_id']}: unknown {link_slug}")
        exact_competitor = next(
            (
                company_slug
                for company_slug, company in competitor_slugs.items()
                if normalized_name(company) in normalized_name(row["name"])
            ),
            None,
        )
        if exact_competitor and not link_slug:
            linked_errors.append(
                f"{row['substitute_id']}: existing competitor {exact_competitor} is not linked"
            )
        if link_slug and link_slug != name_slug and normalized_name(
            competitor_slugs[link_slug]
        ) not in normalized_name(row["name"] + " " + row["notes"]) and link_slug != "yc-co-founder-matching":
            linked_errors.append(f"{row['substitute_id']}: ambiguous link {link_slug}")
    validation.check(
        not linked_errors,
        "existing competitor entities are linked by canonical slug and not silently duplicated",
    )

    malformed = []
    source_gaps = []
    for row in substitutes:
        source_type = row["source_type"].strip()
        source_url = row["source_url"].strip()
        if source_type not in SUBSTITUTE_SOURCE_TYPES:
            source_gaps.append(f"{row['substitute_id']}: invalid source type {source_type}")
        if source_type == "Unverified":
            if row["research_status"] != "Unverified":
                source_gaps.append(f"{row['substitute_id']}: unverified source not reflected in status")
        elif not source_url:
            source_gaps.append(f"{row['substitute_id']}: sourced record has no URL")
        if source_url:
            parsed = urlparse(source_url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                malformed.append(f"{row['substitute_id']}: {source_url}")
    validation.check(
        not source_gaps,
        "every substitute has a source or is explicitly Unverified",
    )
    validation.check(
        not malformed,
        "all substitute representative source URLs are structurally valid",
    )

    evidence_ids = [row["evidence_id"].strip() for row in evidence]
    validation.check(
        all(evidence_ids) and len(evidence_ids) == len(set(evidence_ids)),
        "substitute evidence identifiers are non-empty and unique",
    )
    evidence_id_set = set(evidence_ids)
    evidence_source_errors = []
    evidence_link_errors = []
    for row in evidence:
        source_type = row["source_type"].strip()
        source_url = row["source_url"].strip()
        if source_type not in SUBSTITUTE_SOURCE_TYPES:
            evidence_source_errors.append(
                f"{row['evidence_id']}: invalid source type {source_type}"
            )
        if not row["claim"].strip():
            evidence_source_errors.append(f"{row['evidence_id']}: empty claim")
        if source_type == "Unverified":
            if source_url:
                evidence_source_errors.append(
                    f"{row['evidence_id']}: Unverified row unexpectedly has a URL"
                )
        elif not source_url:
            evidence_source_errors.append(f"{row['evidence_id']}: sourced claim has no URL")
        if source_url:
            parsed = urlparse(source_url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                evidence_source_errors.append(
                    f"{row['evidence_id']}: malformed URL {source_url}"
                )
        if source_type == "Inference" and row["evidence_dimension"] != "Inference":
            evidence_source_errors.append(
                f"{row['evidence_id']}: Inference is not explicitly labeled"
            )
        unknown_substitutes = set(split_values(row["substitute_id"])) - set(substitute_ids)
        unknown_jobs = set(split_values(row["job_id"])) - SUBSTITUTE_JOB_IDS
        if unknown_substitutes or unknown_jobs:
            evidence_link_errors.append(
                f"{row['evidence_id']}: substitutes={sorted(unknown_substitutes)} "
                f"jobs={sorted(unknown_jobs)}"
            )
    validation.check(
        not evidence_source_errors,
        "every factual evidence claim has a valid source and explicit evidence type",
    )
    validation.check(
        not evidence_link_errors,
        "evidence records link only to canonical substitutes and Jobs",
    )

    orphan_references = []
    for row in substitutes:
        unknown = set(split_values(row["evidence_ids"])) - evidence_id_set
        if unknown:
            orphan_references.append(
                f"{row['substitute_id']}: {sorted(unknown)}"
            )
    workflow_ids = [row["workflow_id"].strip() for row in workflows]
    validation.check(
        all(workflow_ids) and len(workflow_ids) == len(set(workflow_ids)),
        "workflow identifiers are non-empty and unique",
    )
    workflow_errors = []
    coverage = {job_id: set() for job_id in SUBSTITUTE_JOB_IDS}
    for row in workflows:
        job_id = row["job_id"].strip()
        if job_id not in SUBSTITUTE_JOB_IDS:
            workflow_errors.append(f"{row['workflow_id']}: invalid Job {job_id}")
            continue
        try:
            stage_order = int(row["stage_order"])
        except ValueError:
            workflow_errors.append(f"{row['workflow_id']}: invalid stage order")
            continue
        coverage[job_id].add(stage_order)
        unknown_substitutes = set(split_values(row["substitute_ids"])) - set(substitute_ids)
        unknown_evidence = set(split_values(row["evidence_ids"])) - evidence_id_set
        if unknown_substitutes or unknown_evidence:
            workflow_errors.append(
                f"{row['workflow_id']}: substitutes={sorted(unknown_substitutes)} "
                f"evidence={sorted(unknown_evidence)}"
            )
        if not row["evidence_ids"].strip() and row["evidence_status"] != "Unverified":
            workflow_errors.append(
                f"{row['workflow_id']}: missing evidence is not marked Unverified"
            )
    validation.check(
        not workflow_errors,
        "workflow rows use canonical references and mark unsupported stages Unverified",
    )
    validation.check(
        all(orders == set(range(1, 12)) for orders in coverage.values()),
        "all four Jobs contain exactly the eleven documented workflow stages",
    )
    validation.check(
        not orphan_references,
        "substitute entity evidence references resolve to the evidence register",
    )

    tracker_text = CSV_PATH.read_text(encoding="utf-8")
    validation.check(
        "substitute_id" not in tracker_text
        and not any(
            row["substitute_id"] in tracker_text
            for row in substitutes
        ),
        "substitute records are not injected into the 36-company tracker",
    )

    score_source = function_source(GENERATOR, "relationship_score")
    validation.check(
        not any(
            repr(row["name"]) in score_source or f'"{row["name"]}"' in score_source
            for row in substitutes
        ),
        "relationship scoring contains no substitute-name assignments",
    )
    renderer_source = function_source(GENERATOR, "substitutes_page")
    report_source = SUBSTITUTE_REPORT_SCRIPT.read_text(encoding="utf-8")
    validation.check(
        not any(
            row["name"] in renderer_source or row["name"] in report_source
            for row in substitutes
        ),
        "substitute outputs are data-driven and contain no hard-coded substitute list",
    )

    if not artifacts_required:
        return
    substitute_page = ROOT / "sites" / "full-report-site" / "alternative-workflows.html"
    substitute_data = ROOT / "sites" / "full-report-site" / "substitutes-data.js"
    generated_reports = (
        ROOT / "SUBSTITUTE_MATRIX.md",
        ROOT / "SUBSTITUTE_WORKFLOWS.md",
        ROOT / "SUBSTITUTE_EVIDENCE_REGISTER.md",
    )
    validation.check(
        substitute_page.exists() and substitute_data.exists(),
        "site includes the generated Alternative Workflows data and page",
    )
    validation.check(
        all(path.exists() for path in generated_reports),
        "generated substitute matrix, workflow maps, and evidence register exist",
    )
    if substitute_page.exists() and substitute_data.exists():
        page_text = substitute_page.read_text(encoding="utf-8")
        data_text = substitute_data.read_text(encoding="utf-8")
        validation.check(
            all(row["substitute_id"] in data_text for row in substitutes)
            and "data/substitutes-research.csv" in data_text,
            "Alternative Workflows data is generated from every canonical substitute record",
        )
        labeled_types = {
            row["source_type"]
            for row in evidence
            if row["source_type"] in {"Company Claim", "Inference", "Unverified"}
        }
        validation.check(
            all(source_type in page_text for source_type in labeled_types)
            and "not independent proof of effectiveness" in page_text,
            "Company Claim, Inference, and Unverified evidence remain visibly labeled",
        )
        validation.check(
            "relationship_score" not in data_text
            and "direct_threat_score" not in data_text,
            "substitute site data contains no numeric relationship or legacy threat score",
        )


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
    paths = [
        ROOT / "index.html",
        ROOT / "START_HERE.html",
        ROOT / "README.html",
        ROOT / "SUBSTITUTE_MATRIX.md",
        ROOT / "SUBSTITUTE_WORKFLOWS.md",
        ROOT / "SUBSTITUTE_EVIDENCE_REGISTER.md",
        XLSX_PATH,
    ]
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
        [sys.executable, str(SUBSTITUTE_REPORT_SCRIPT)],
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
    check_substitutes(validation, rows, artifacts_required=not args.pre_build)
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
