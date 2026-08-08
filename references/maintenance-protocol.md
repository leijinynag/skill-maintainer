# Maintenance Protocol

This reference defines the evidence model used by `skill-maintainer`. It is a
decision aid, not a replacement for domain judgment.

## Change Ledger

| Category | Meaning |
| --- | --- |
| `preserve` | Existing behavior that must remain valid. |
| `add` | New behavior required by the request. |
| `replace` | Existing behavior whose rule or implementation changes. |
| `delete` | Obsolete, duplicate, conflicting, or unsupported content. |
| `move` | Content relocated to a reference, script, or more appropriate file. |
| `uncertain` | A claim or behavior without sufficient evidence. |
| `agent_judgment_space` | Cases where the agent should choose using evidence. |

Every `add` and `replace` entry should include:

- the evidence or concrete failure it addresses;
- the old rule it supersedes, if any;
- why merging is insufficient;
- the effect on judgment space;
- the eval case that protects it.

For a new rule, also record:

- the decision it helps the agent make;
- the evidence or condition that activates it;
- the preferred action when it activates;
- the judgment that remains with the agent;
- the bounded behavior when evidence is missing.

## Risk Signals

Classify by the highest applicable signal.

### Low

- Delete a rule explicitly superseded by another rule.
- Remove duplicate prose without changing meaning.
- Repair a broken local reference.
- Move repeated detail from `SKILL.md` to a directly linked reference.
- Reorganize headings without changing behavior.

### Medium

- Change a default, fallback, or output grouping.
- Merge rules whose combined meaning needs interpretation.
- Change which reference or script is loaded.
- Add a new supported input or result field.
- Change retry, narrowing, or evidence-selection guidance.

### High

- Change activation or non-activation boundaries.
- Change permission, confirmation, safety, or write behavior.
- Change an external API or tool contract.
- Change cross-skill handoff conditions.
- Change a required output schema or a claim about irreversible behavior.

If the request and the artifact disagree, mark the item `uncertain` and stop
short of inventing a contract. A structural script can report risk signals but
cannot establish semantic correctness.

## Pruning Heuristics

During the prune pass, inspect:

- repeated instructions stated in different sections;
- old rules left beside replacement rules;
- examples written with universal wording;
- `MUST` rules that should be `SHOULD` or `MAY`;
- negative rules (`MUST NOT`, `NEVER`, `禁止`, `不要`, `不得`, and similar)
  that lack scope, evidence, or a preferred alternative;
- runs of near-synonymous prohibitions that can be expressed as one positive
  target plus one hard guardrail;
- one-off branches with no eval or stable contract;
- details duplicated in both `SKILL.md` and a reference;
- references that are no longer reachable from the main file;
- new lines added without a corresponding behavior or eval benefit.

Prefer one precise rule over several near-synonyms. Keep the main file as a
navigation and decision layer; move large schemas, command lists, and examples
to directly linked references or deterministic scripts.

## Progress and Anti-Loop Review

Treat repeated work as a review signal, not as proof of a bug. Look for:

- repeated reads or checks of the same material without new context;
- repeated user questions after a safe, evidence-based default is available;
- retries with unchanged input and no changed validation target;
- plans or checklists that never produce an edit, decision, validation result, or
  explicit blocker;
- generic quality language such as "be thorough", "be careful", or "ensure
  quality" without an observable action or completion test;
- loop language such as "again", "re-check", "continue until", or "retry" without
  a checkable stop condition.

The auditor may report these as possible empty-loop signals. It cannot determine
from text alone whether an agent actually spun, so the finding remains a prompt
for review and should not automatically fail a skill.

## Negation Review

For each prohibition, ask:

1. What verified contract or risk makes it necessary?
2. What is the preferred action instead?
3. What scope or evidence activates it?
4. What should happen when the evidence is missing?

If the answer is only "because this happened once", classify the rule as
`uncertain` or delete it. A negative rule without an alternative can leave the
agent with no useful next action and increase the chance of both inaction and
literal misapplication.

## No-Op Review

Review each sentence against the model's default behavior. Delete guidance that
does not change behavior, expose a hidden convention, protect a contract, or
define a checkable result. When generic advice points at a real concern, rewrite
it as an observable action, evidence requirement, or completion criterion.
