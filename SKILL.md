---
name: skill-maintainer
description: >
  Maintain, refactor, and review Agent Skills and instruction directories without
  uncontrolled growth or rigid workflow behavior. Use when modifying SKILL.md,
  AGENTS.md, CLAUDE.md, agent metadata, references, scripts, assets, or evals;
  especially when a requested change may replace old rules, introduce duplicate
  guidance, alter routing or safety behavior, or reduce the agent's room for
  judgment.
---

# Skill Maintainer

Maintain the smallest coherent instruction set that satisfies the requested behavior.
Preserve verified contracts and useful agent judgment; do not turn every observed
case into a permanent branch.

## Operating Mode

Use this skill for maintenance and review of a skill directory or a related agent
instruction directory. Treat `SKILL.md` as the primary behavior source. Read
`AGENTS.md`, `CLAUDE.md`, `agents/openai.yaml`, `references/`, `scripts/`, `assets/`,
and `evals/` when they exist and affect the requested change.

Use `scripts/audit_skill.py` for deterministic structure checks. Pass the target
directory, the user's request, and a Git base ref when one is available. Write the
JSON report to the project-level `.skill-maintainer/` directory by default.

## Maintenance Protocol

1. Discover the target directory, related instruction files, tests/evals, and Git
   context. Do not edit until the target and the requested behavior are clear.
2. Inspect the current behavior, not only the lines that look relevant. Identify
   activation boundaries, safety constraints, tools, handoffs, output contracts,
   defaults, references, scripts, and known eval coverage.
3. Build a change ledger with these categories:
   `preserve`, `add`, `replace`, `delete`, `move`, `uncertain`, and
   `agent_judgment_space`.
4. For every proposed addition, state the concrete failure it prevents, whether it
   replaces an existing rule, why it cannot be merged into an existing rule, and
   whether it narrows agent judgment.
5. Classify the requested change:
   - `low`: delete obsolete or duplicate content, repair local links, move repeated
     detail to a reference, or make a non-behavioral structural cleanup.
   - `medium`: merge or rewrite behavior rules, change defaults, alter loading
     guidance, or change output organization.
   - `high`: change activation boundaries, safety/permission/confirmation rules,
     tool calls or writes, external API contracts, output contracts, or handoffs.
6. Present the ledger, risk level, proposed edits, and eval impact before editing.
   Apply `low` changes automatically only when the user asked to maintain or modify
   the files. For `medium` and `high` changes, stop after the proposal and wait for
   explicit confirmation. For review-only requests, never edit.
7. Apply the smallest coherent change. Prefer replacing, merging, deleting, or
   moving over appending. Remove superseded rules in the same change.
8. Run a prune pass: search for duplicate instructions, contradictory strong rules,
   stale examples, obsolete references, and branches that only serve one anecdote.
9. Validate structure and links, then create eval cases for preserved behavior,
   ambiguous requests, unknown inputs, and the changed behavior. Report additions,
   changes, deletions, moves, remaining uncertainty, and net complexity change.

## Preserve Judgment

Keep these as explicit contracts when needed: permissions, safety, data integrity,
confirmed API semantics, irreversible operations, and reliable handoff conditions.

Prefer decision criteria over exhaustive branching. Let the agent choose the next
step from evidence when multiple paths are valid. Do not:

- encode an example, candidate field, or provisional interpretation as a universal
  rule;
- add a permanent branch for one observed case without a stable contract;
- invent fields, states, API semantics, or failure classes to make a workflow look
  complete;
- require clarification when a safe, evidence-based default is sufficient;
- replace reasoning with a mandatory sequence merely because the sequence worked once.

Use `MUST` only for non-negotiable contracts, `SHOULD` for defaults that may yield to
evidence, and `MAY` for optional tactics. If evidence is insufficient, label the
item uncertain and preserve a bounded stopping condition.

## Git and Change Safety

Use Git read-only commands such as `status`, `log`, `show`, `diff`, and `blame` to
understand history. Do not commit, revert, reset, switch branches, publish, or
rewrite history. Do not discard changes made by the user.

When a requested change conflicts with existing edits, describe the conflict and
work with the existing state. Do not silently restore an older version.

## References

Read [references/maintenance-protocol.md](references/maintenance-protocol.md) for
the ledger schema, risk signals, and pruning heuristics. Read
[references/eval-cases.md](references/eval-cases.md) when designing or reviewing
behavior evals.
