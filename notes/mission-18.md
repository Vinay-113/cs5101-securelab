# Mission 18: Compare Access-Control Models

## Question

Who decides access under each model?

## Prediction

The comparison will connect observed DAC, ACL, capability and MAC behavior; RBAC remains a conceptual scenario.

## Concept

Different models answer different questions: identity and ownership, mandatory policy, role membership, named ACL rights or privileged kernel operations.

## Defense

Combine models deliberately and verify effective access instead of assuming one mechanism subsumes all others.

## Verification

Re-test Alice/Bob and the enforcing AppArmor profile; consult the comparison in docs/access-models.md.

## Reflection

RBAC is explained rather than falsely presented as a deployed role system.

## Experiment

Run `python3 scripts/run_lab.py --missions 18` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q53.** In DAC, the resource owner normally chooses discretionary grants, within administrator and mandatory-policy constraints.

**Q54.** An administrator or security policy authority defines MAC rules; ordinary file owners cannot bypass them merely by chmod.

**Q55.** Assign a database-administrator role the required database-management permissions, then grant/revoke role membership instead of duplicating per-user rights.

**Q56.** A Linux capability grants a narrower class of privileged kernel operations than unrestricted root; this is distinct from an object-capability design.

**Q57.** ACLs add named users/groups and a mask to the ordinary Unix mode design, permitting targeted exceptions. They increase review complexity and remain discretionary.

