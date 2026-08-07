# skill-maintainer

An agent skill for maintaining other agent skills and instruction directories
without uncontrolled growth or overly rigid workflows.

It helps an agent inspect a skill before editing, build a change ledger, classify
risk, remove superseded rules, preserve judgment space, and validate the result.

## What It Does

- Audits `SKILL.md`, `AGENTS.md`, `CLAUDE.md`, metadata, references, scripts, and evals.
- Separates `preserve`, `add`, `replace`, `delete`, `move`, `uncertain`, and
  `agent_judgment_space`.
- Detects broken references, duplicate guidance, conflicting strong rules, and
  likely "append-only" growth.
- Allows low-risk cleanup while stopping medium/high-risk behavior changes for
  explicit confirmation.
- Produces a human-readable summary and a JSON report under `.skill-maintainer/`.

It does not commit, revert, publish, call business APIs, or decide whether a
domain-specific rule is semantically correct.

## Install

For Codex, copy or symlink this repository's skill directory into the local skill
directory:

```bash
cp -R . "${CODEX_HOME:-$HOME/.codex}/skills/skill-maintainer"
```

For Claude-compatible environments, use the host's supported skill directory or
reference this repository's `SKILL.md` from the project configuration.

## Use

Invoke the skill explicitly:

```text
Use $skill-maintainer to audit and simplify this skill before changing it.
```

The included deterministic audit can also be run directly:

```bash
python3 scripts/audit_skill.py ../some-skill \
  --request "Remove the obsolete fallback and simplify the routing rules." \
  --git-ref main
```

## Development

```bash
python3 -m unittest discover scripts -p 'test_*.py'
python3 /path/to/skill-creator/scripts/quick_validate.py .
python3 scripts/audit_skill.py .
```

The behavior evals in `evals/` are a framework-neutral checklist for manual or
model-based forward testing. The first release intentionally does not include a
model runner or automatic semantic scoring.

## License

MIT. See [LICENSE](LICENSE).
