# Evaluation Set

These cases are framework-neutral. Run them manually or with a model evaluation
harness after changing the skill.

`trigger_eval_set.json` checks activation and non-activation.
`maintenance_eval_set.json` checks preservation, pruning, judgment space, risk
gating, anti-loop progress, negation density, completion criteria, and regression
behavior.

The first release does not include an automatic model runner or semantic scorer.
