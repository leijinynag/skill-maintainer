#!/usr/bin/env python3
"""Audit an Agent Skill directory without modifying the target or Git history."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


TEXT_SUFFIXES = {".md", ".markdown", ".yaml", ".yml", ".json", ".txt", ".py", ".sh"}
MARKDOWN_REF_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^)]*['\"])?\)", re.I)
CONTEXTUAL_REF_RE = re.compile(
    r"(?:read|see|load|use)\s+(?:[`']([^`']+)[`']|((?:[\w.-]+/)+[\w.-]+|[\w.-]+\.(?:md|yaml|yml|json|py|sh)))",
    re.I,
)
PATH_SUFFIXES = {".md", ".markdown", ".yaml", ".yml", ".json", ".txt", ".py", ".sh"}
CONTEXT_FILES = {"AGENTS.md", "CLAUDE.md"}
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")
RULE_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.+?)\s*$")
STRONG_RE = re.compile(r"\b(MUST|SHOULD|MAY)\b", re.I)
FENCE_RE = re.compile(r"^```")


def normalize(value: str) -> str:
    value = re.sub(r"`[^`]*`", "CODE", value.lower())
    value = re.sub(r"[*_>#\[\]().,:;/'\"-]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_frontmatter(path: Path) -> Tuple[Dict[str, str], List[Dict[str, Any]]]:
    text = read_text(path)
    findings: List[Dict[str, Any]] = []
    if not text.startswith("---\n"):
        return {}, [{"id": "frontmatter.missing", "severity": "error", "message": "SKILL.md must start with YAML frontmatter."}]
    end = text.find("\n---", 4)
    if end == -1:
        return {}, [{"id": "frontmatter.unclosed", "severity": "error", "message": "YAML frontmatter is not closed."}]
    fields: Dict[str, str] = {}
    lines = text[4:end].splitlines()
    block_key: Optional[str] = None
    block_style: Optional[str] = None
    block_lines: List[str] = []

    def finish_block() -> None:
        nonlocal block_key, block_style, block_lines
        if block_key is not None:
            if block_style == "|":
                fields[block_key] = "\n".join(block_lines).strip()
            else:
                fields[block_key] = " ".join(item.strip() for item in block_lines).strip()
        block_key = None
        block_style = None
        block_lines = []

    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            if block_key is not None:
                block_lines.append("")
            continue
        if block_key is not None and (line.startswith((" ", "\t")) or not re.match(r"^[A-Za-z0-9_-]+:", line)):
            block_lines.append(line.lstrip())
            continue
        finish_block()
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            if line.startswith((" ", "\t")):
                continue
            findings.append(
                {
                    "id": "frontmatter.unparsed",
                    "severity": "warning",
                    "message": f"Could not parse frontmatter line: {line}",
                }
            )
            continue
        key, value = match.groups()
        value = value.strip()
        if value in {">", "|", ">-", "|-", ">+", "|+"}:
            block_key = key
            block_style = value[0]
            block_lines = []
        else:
            fields[key] = value.strip("'\"")
    finish_block()
    for required in ("name", "description"):
        if not fields.get(required):
            findings.append({"id": f"frontmatter.{required}", "severity": "error", "message": f"Frontmatter is missing {required}."})
    return fields, findings


def iter_local_references(text: str) -> Iterable[str]:
    """Yield references that are intended to resolve inside the target directory."""

    for match in MARKDOWN_REF_RE.finditer(text):
        yield match.group(1)
    for match in CONTEXTUAL_REF_RE.finditer(text):
        raw = match.group(1) or match.group(2)
        if raw:
            yield raw


def is_local_path_reference(raw: str) -> bool:
    """Avoid treating prose code words or host-level context files as local paths."""

    candidate = raw.strip("<>`'\"")
    if not candidate or candidate.startswith(("http://", "https://", "#", "$")):
        return False
    if Path(candidate).name in CONTEXT_FILES:
        return False
    return "/" in candidate or Path(candidate).suffix.lower() in PATH_SUFFIXES


def iter_text_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def count_metrics(text: str) -> Dict[str, int]:
    lines = text.splitlines()
    rules = [RULE_RE.match(line).group(1) for line in lines if RULE_RE.match(line)]
    strong = Counter(match.group(1).upper() for line in lines for match in [STRONG_RE.search(line)] if match)
    return {
        "lines": len(lines),
        "non_empty_lines": sum(bool(line.strip()) for line in lines),
        "headings": sum(bool(HEADING_RE.match(line)) for line in lines),
        "list_rules": len(rules),
        "strong_must": strong["MUST"],
        "strong_should": strong["SHOULD"],
        "strong_may": strong["MAY"],
    }


def add_finding(findings: List[Dict[str, Any]], finding_id: str, severity: str, message: str, path: Optional[Path] = None) -> None:
    item: Dict[str, Any] = {"id": finding_id, "severity": severity, "message": message}
    if path is not None:
        item["path"] = str(path)
    findings.append(item)


def inspect_files(root: Path, skill_path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    findings: List[Dict[str, Any]] = []
    files = list(iter_text_files(root))
    metrics = {"files": len(files), "by_file": {}}
    for path in files:
        metrics["by_file"][str(path.relative_to(root))] = count_metrics(read_text(path))

    fields, frontmatter_findings = parse_frontmatter(skill_path)
    findings.extend(frontmatter_findings)
    expected_name = root.name
    if fields.get("name") and fields["name"] != expected_name:
        add_finding(findings, "frontmatter.name_mismatch", "error", f"Frontmatter name {fields['name']!r} does not match directory {expected_name!r}.", skill_path)

    text = read_text(skill_path)
    headings = Counter(normalize(match.group(1)) for line in text.splitlines() if (match := HEADING_RE.match(line)))
    for heading, count in headings.items():
        if heading and count > 1:
            add_finding(findings, "content.duplicate_heading", "warning", f"Heading appears {count} times: {heading}", skill_path)

    rules: Dict[str, List[int]] = {}
    fenced = False
    for line_number, line in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(line.strip()):
            fenced = not fenced
            continue
        if fenced:
            continue
        match = RULE_RE.match(line)
        if match and len(normalize(match.group(1))) >= 24:
            rules.setdefault(normalize(match.group(1)), []).append(line_number)
    for rule, locations in rules.items():
        if len(locations) > 1:
            add_finding(findings, "content.duplicate_rule", "warning", f"Near-identical list rule appears at lines {locations}: {rule}", skill_path)

    strong_lines: List[Tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if STRONG_RE.search(line):
            strong_lines.append((line_number, line.strip()))
    subjects: Dict[str, Dict[str, List[int]]] = {}
    for line_number, line in strong_lines:
        subject = normalize(re.sub(r"\b(MUST|SHOULD|MAY|NOT|NEVER|ALWAYS)\b", " ", line))
        if not subject:
            continue
        polarity = "negative" if re.search(r"\b(not|never|no|without)\b", line, re.I) else "positive"
        subjects.setdefault(subject, {}).setdefault(polarity, []).append(line_number)
    for subject, polarities in subjects.items():
        if "positive" in polarities and "negative" in polarities:
            add_finding(findings, "content.possible_conflict", "warning", f"Strong rules may conflict for subject {subject!r}: {polarities}", skill_path)

    for path in files:
        if path.parent.name == "references":
            nested = re.search(r"(?:references|reference)/", read_text(path), re.I)
            if nested:
                add_finding(findings, "references.nested", "warning", "Reference files should link directly from SKILL.md rather than deeply nesting references.", path)

    for raw in iter_local_references(text):
        if not is_local_path_reference(raw):
            continue
        raw = raw.split("#", 1)[0].strip("<>")
        candidate = (root / raw).resolve()
        if not candidate.exists():
            add_finding(findings, "references.broken", "error", f"Referenced local path does not exist: {raw}", skill_path)

    metrics["skill"] = count_metrics(text)
    metrics["frontmatter"] = fields
    return metrics, findings


def git_context(root: Path, git_ref: Optional[str]) -> Dict[str, Any]:
    context: Dict[str, Any] = {"available": False, "base_ref": git_ref, "diff": {"insertions": 0, "deletions": 0, "files": []}}
    try:
        top = subprocess.check_output(["git", "-C", str(root), "rev-parse", "--show-toplevel"], text=True, stderr=subprocess.DEVNULL).strip()
        context["available"] = True
        context["root"] = top
        context["branch"] = subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"], text=True, stderr=subprocess.DEVNULL).strip()
        context["head"] = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
        if git_ref:
            subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", git_ref], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            rows = subprocess.check_output(
                ["git", "-C", str(root), "diff", "--numstat", git_ref, "--", "."],
                text=True,
                stderr=subprocess.DEVNULL,
            ).splitlines()
            for row in rows:
                parts = row.split("\t")
                if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
                    context["diff"]["insertions"] += int(parts[0])
                    context["diff"]["deletions"] += int(parts[1])
                    context["diff"]["files"].append(parts[2])
    except (subprocess.CalledProcessError, OSError, ValueError) as exc:
        context["error"] = str(exc)
    return context


def is_fatal_finding(finding: Dict[str, Any]) -> bool:
    return finding["id"] in {
        "target.missing",
        "target.skill_missing",
        "frontmatter.missing",
        "frontmatter.unclosed",
        "frontmatter.name",
        "frontmatter.description",
        "frontmatter.name_mismatch",
        "git.ref_invalid",
    }


def classify_risk(request: str, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    text = request.lower()
    high_terms = ("trigger", "permission", "security", "safety", "write", "api", "handoff", "contract", "confirm")
    medium_terms = ("default", "fallback", "output", "route", "routing", "retry", "field", "behavior", "workflow")
    reasons: List[str] = []
    level = "low"
    if any(term in text for term in high_terms):
        level = "high"
        reasons.append("Request contains a safety, contract, routing, handoff, permission, or write-related signal.")
    elif any(term in text for term in medium_terms):
        level = "medium"
        reasons.append("Request appears to change behavior, defaults, routing, or output.")
    if any(item["severity"] == "error" for item in findings):
        level = "high" if level != "high" else level
        reasons.append("The audit found an error that requires human review.")
    elif any(item["severity"] == "warning" for item in findings) and level == "low":
        level = "medium"
        reasons.append("The audit found warnings that may affect behavior or maintainability.")
    return {"level": level, "reasons": reasons}


def build_report(root: Path, request: str, git_ref: Optional[str]) -> Dict[str, Any]:
    skill_path = root / "SKILL.md"
    findings: List[Dict[str, Any]] = []
    if not root.exists() or not root.is_dir():
        findings.append({"id": "target.missing", "severity": "error", "message": f"Target directory does not exist: {root}"})
        metrics: Dict[str, Any] = {}
    elif not skill_path.exists():
        findings.append({"id": "target.skill_missing", "severity": "error", "message": "Target directory does not contain SKILL.md."})
        metrics = {"files": 0, "by_file": {}}
    else:
        metrics, findings = inspect_files(root, skill_path)
    git = git_context(root, git_ref) if root.exists() else {"available": False, "base_ref": git_ref}
    if git_ref and git.get("error"):
        findings.append(
            {
                "id": "git.ref_invalid",
                "severity": "error",
                "message": f"Git ref could not be resolved: {git_ref}",
                "evidence": git["error"],
            }
        )
    diff = git.get("diff", {})
    if diff.get("insertions", 0) > 40 and diff.get("deletions", 0) == 0:
        findings.append({"id": "complexity.append_only", "severity": "warning", "message": "The Git diff adds many lines without deletions; review whether old rules should be replaced or removed."})
    report = {
        "report_version": "0.1.0",
        "target": {"path": str(root.resolve()), "name": root.name},
        "git_context": git,
        "baseline_metrics": metrics,
        "change_request": request,
        "change_ledger": {
            "preserve": [],
            "add": [],
            "replace": [],
            "delete": [],
            "move": [],
            "uncertain": [],
            "agent_judgment_space": [],
        },
        "findings": findings,
        "risk": classify_risk(request, findings),
        "proposed_changes": [],
        "applied_changes": [],
        "eval_cases": [],
        "validation": {"script": "audit_skill.py", "errors": sum(item["severity"] == "error" for item in findings), "warnings": sum(item["severity"] == "warning" for item in findings)},
    }
    return report


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_dir", type=Path)
    parser.add_argument("--request", default="", help="Natural-language maintenance request.")
    parser.add_argument("--json-out", type=Path, help="Write the JSON report to this path.")
    parser.add_argument("--git-ref", default=None, help="Optional Git ref used for a read-only diff.")
    args = parser.parse_args(argv)
    report = build_report(args.target_dir.resolve(), args.request, args.git_ref)
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    output_path = args.json_out or (args.target_dir.resolve() / ".skill-maintainer" / "audit-report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")
    if args.json_out is None:
        print(f"report: {output_path}")
    else:
        print(output, end="")
    errors = report["validation"]["errors"]
    warnings = report["validation"]["warnings"]
    if any(is_fatal_finding(item) for item in report["findings"]):
        return 2
    if errors or warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
