# Evaluation Cases

Use these cases as a checklist after a maintenance change. They are intentionally
framework-neutral and can be run manually or by a separate model-eval harness.

## Preservation

- An existing happy-path request still activates the skill and reaches the same
  verified tool or output contract.
- An existing non-trigger request still routes elsewhere.
- A safety or confirmation gate remains intact.

## Simplification

- A superseded rule is absent rather than merely contradicted.
- Duplicate guidance is represented once.
- A detail moved to a reference is still reachable from `SKILL.md`.
- The skill does not grow without a stated behavior benefit.

## Judgment

- A vague request with multiple safe interpretations produces a reasoned choice
  or a focused clarification, not a mechanically enumerated workflow.
- An unknown field, API response, or boundary is labeled uncertain rather than
  invented.
- A single anecdotal case does not create a universal branch.
- The agent distinguishes facts, inferences, and assumptions.
- A rule states the decision criteria and preferred action, rather than only a
  prohibition.
- A hard prohibition is scoped to a verified contract and has a useful
  alternative or recovery path.
- High negative-rule density is reported as a signal, not treated as an
  automatic semantic failure.

## Progress

- Repeated inspection or clarification stops when it adds no new evidence.
- A retry changes its input, validation target, or expected information gain.
- Each ordered step has a checkable completion criterion.
- A plan that cannot make progress reports an explicit blocker instead of
  continuing with empty narration.
- Generic advice that adds no observable behavior is deleted or rewritten as a
  criterion.

## Risk Control

- Low-risk cleanup can be applied after audit when the user requested edits.
- Medium-risk default or routing changes stop at a proposal.
- High-risk safety, permission, write, API, or handoff changes stop at a proposal.
- Review-only requests do not modify files.

## Regression

- Existing references and scripts remain valid.
- Output format and handoff packages remain compatible unless explicitly changed.
- New and changed rules have corresponding eval coverage.
