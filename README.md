# skill-maintainer

[English](README.md) | [简体中文](README.zh-CN.md)

`skill-maintainer` is an Agent Skill for maintaining, refactoring, and reviewing
Agent Skills and instruction directories without uncontrolled growth or overly
rigid workflows.

## What It Solves

It is designed for cases where:

- a Skill keeps getting longer without removing obsolete rules;
- new guidance duplicates or conflicts with existing guidance;
- one-off incidents become permanent branches;
- a rigid workflow gradually replaces agent judgment;
- generic no-op guidance such as "be thorough" adds context without changing
  behavior;
- repeated checks, retries, or clarifications can continue without information
  gain;
- a change affects trigger boundaries, defaults, safety, permissions, or output
  contracts.

The Skill uses a review-before-editing model:

```text
discover
  -> inspect
  -> build change ledger
  -> classify risk
  -> propose
  -> apply low-risk changes or wait for confirmation
  -> prune
  -> validate
  -> report
```

Each maintenance pass separates:

`preserve`, `add`, `replace`, `delete`, `move`, `uncertain`, and
`agent_judgment_space`.

## Supported Scope

The Skill can inspect and maintain:

- `SKILL.md`
- `AGENTS.md`
- `CLAUDE.md`
- `agents/openai.yaml`
- `references/`
- `scripts/`
- `assets/`
- `evals/`
- Git history and diffs

`SKILL.md` is treated as the primary behavior source. Other agent instruction
files are read as related context rather than separate host-specific workflows.

## Installation

### Clone with Git

```bash
git clone https://github.com/leijinynag/skill-maintainer.git
cd skill-maintainer
```

### Clone with GitHub CLI

```bash
gh repo clone leijinynag/skill-maintainer
cd skill-maintainer
```

### Download a ZIP archive

Open the repository page, select **Code -> Download ZIP**, extract the archive,
and enter the extracted directory.

### Install globally for Codex

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/leijinynag/skill-maintainer.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/skill-maintainer"
```

To update an existing clone:

```bash
git -C "${CODEX_HOME:-$HOME/.codex}/skills/skill-maintainer" pull
```

### Install in one project

```bash
mkdir -p .codex/skills
git clone https://github.com/leijinynag/skill-maintainer.git \
  .codex/skills/skill-maintainer
```

Or pin it as a Git submodule:

```bash
git submodule add \
  https://github.com/leijinynag/skill-maintainer.git \
  .codex/skills/skill-maintainer
```

### Use a symlink for local development

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -sfn "$PWD" \
  "${CODEX_HOME:-$HOME/.codex}/skills/skill-maintainer"
```

### Install in Claude or another compatible host

Copy the repository directory into the host's supported Skill directory. Keep
the following structure:

```text
skill-maintainer/
├── SKILL.md
├── agents/
├── references/
├── scripts/
└── evals/
```

If the host only supports a single Skill file, copy at least `SKILL.md`. To keep
deterministic auditing available, also copy `scripts/` and `references/`.

## Usage

Invoke it in Codex or another Agent Skill-compatible environment:

```text
Use $skill-maintainer to audit and simplify this Agent skill before changing it.
```

Example:

```text
Use $skill-maintainer to review this SKILL.md, remove obsolete and duplicate
rules, and identify any workflow branches that unnecessarily reduce judgment.
```

## Risk Levels

| Risk | Default behavior |
| --- | --- |
| `low` | Apply low-risk cleanup after auditing when the user requested edits |
| `medium` | Produce a proposal and patch; wait for confirmation |
| `high` | Produce a proposal and patch; wait for confirmation |

Medium and high risk changes generally include changes to defaults, routing,
trigger boundaries, safety, permissions, writes, APIs, output contracts, or
cross-Skill handoffs.

## Deterministic Audit

Run the dependency-free structural auditor:

```bash
python3 scripts/audit_skill.py <target-dir> \
  --request "Remove the obsolete fallback and merge duplicate rules." \
  --json-out <report-path> \
  --git-ref main
```

Without `--json-out`, the report is written to:

```text
.skill-maintainer/audit-report.json
```

The auditor checks:

- frontmatter and Skill naming;
- local references and broken links;
- duplicate headings and rules;
- possible conflicts among `MUST` / `SHOULD` / `MAY`;
- negative-rule density, adjacent prohibitions, and missing alternatives;
- possible empty-loop signals from unbounded checks, retries, or clarification;
- generic no-op guidance without observable actions or completion criteria;
- reference nesting and Git diff growth;
- append-only complexity growth and report completeness.

Negative-rule, empty-loop, and no-op findings are review signals. They do not
automatically mean the Skill is wrong, and they do not fail security-oriented
Skills merely because they contain more guardrails.

Exit codes:

- `0`: audit passed;
- `1`: ordinary findings or warnings require review;
- `2`: the target, `SKILL.md`, or Git ref is invalid.

The script reports deterministic structural facts. It does not decide whether a
domain-specific rule is semantically correct and does not modify target files or
Git history.

## Report Format

Reports include:

```json
{
  "report_version": "0.1.0",
  "target": {},
  "git_context": {},
  "baseline_metrics": {},
  "change_request": "",
  "change_ledger": {},
  "findings": [],
  "risk": {},
  "proposed_changes": [],
  "applied_changes": [],
  "eval_cases": [],
  "validation": {}
}
```

Findings should distinguish facts, evidence, inferences, and unknowns.

## Limitations

The first release intentionally stays small:

- no automatic model-evaluation runner; only framework-neutral eval cases;
- no Git commit, rollback, history rewrite, release, or remote publishing;
- no business API access or company-specific internal paths;
- structural checks cannot establish semantic correctness for a domain rule;
- medium and high risk changes require explicit human confirmation.

Future versions may add Skill snapshots, release channels, rollback assistance,
and a model-evaluation runner.

## Development and Testing

```bash
python3 -m unittest discover scripts -p 'test_*.py'
python3 scripts/validate_skill.py .
python3 /path/to/skill-creator/scripts/quick_validate.py .
python3 scripts/audit_skill.py . --request "Audit the repository Skill"
```

The `evals/` directory contains cases for manual or independent model-based
forward testing. GitHub Actions runs unit tests, Skill validation, and a
self-audit on pushes and pull requests. It does not call real models or business
APIs.

## License

[MIT License](LICENSE)
