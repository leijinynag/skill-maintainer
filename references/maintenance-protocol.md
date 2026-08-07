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
- one-off branches with no eval or stable contract;
- details duplicated in both `SKILL.md` and a reference;
- references that are no longer reachable from the main file;
- new lines added without a corresponding behavior or eval benefit.

Prefer one precise rule over several near-synonyms. Keep the main file as a
navigation and decision layer; move large schemas, command lists, and examples
to directly linked references or deterministic scripts.
