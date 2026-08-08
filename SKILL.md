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

Every action in the protocol should have a progress signal: new evidence, lower
risk, an edit, or a validation result. Continue when the next action has a stated
gain. Stop and report the blocker when repeated inspection, planning, or
clarification produces no new evidence or state change. A retry is justified only
when its input, validation target, or expected information gain changes.

Each ordered step needs a checkable completion criterion. Prefer "all modified
rules have an owner and eval" over vague criteria such as "understand the skill".
Do not add a new step merely to narrate work that the agent would already do or
that produces no observable change.

Prune no-op guidance: a sentence earns its place only when it changes the agent's
default behavior or supplies a contract, decision criterion, or checkable result.
Replace vague advice such as "be thorough" or "ensure quality" with the observable
action or evidence that matters, or delete it when the model already does it by
default.

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

Write the desired action and its decision criteria before writing a prohibition.
Keep a negative rule only when it protects a verified contract, safety boundary,
permission rule, data-integrity invariant, or irreversible operation. Pair such a
guardrail with the preferred action, scope, or recovery path. Prefer "report the
unknown field and preserve it as uncertain" to a bare "do not invent fields".
Several near-synonymous prohibitions should become one scoped rule or be removed.
High negative-rule density is a review signal, not an automatic failure: security
and permission skills may legitimately need more hard guardrails.

When reviewing an existing skill, inspect its context pointers as part of behavior.
The pointer should name the material and the distinct condition that activates it.
Keep always-loaded instructions short; disclose branch-specific detail behind a
reachable reference. Do not split a document merely to make it look modular.

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
