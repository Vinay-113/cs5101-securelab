# Mission 09: Too Much Power

## Question

How can Linux express privileges more narrowly than root?

## Prediction

An ordinary shell will have few or no effective capabilities. System file capabilities depend on the installed image.

## Concept

Linux capabilities divide privileged operations into sets associated with threads and executable files. They are not identical to unforgeable object-capability systems.

## Defense

Separate privileged setup from unprivileged processing; drop capability sets and avoid unnecessary file capabilities.

## Verification

Capture id, sudo policy, capsh and existing getcap output without granting new privileges.

## Reflection

Some capabilities, especially CAP_SYS_ADMIN, remain very broad; a capability grant needs individual analysis.

## Experiment

Run `python3 scripts/run_lab.py --missions 9` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q25.** Root can bypass many discretionary checks and administer critical resources, so compromise has a much larger blast radius.

**Q26.** Linux capabilities split traditional root authority into named privileges such as CAP_NET_BIND_SERVICE. They are per-thread kernel privileges, not general-purpose object handles.

**Q27.** Keep the network/parser component unprivileged and isolate a small audited helper for the one privileged operation it needs.

