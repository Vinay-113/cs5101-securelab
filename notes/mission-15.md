# Mission 15: The Suspicious Application

## Question

Which resources does a harmless program need?

## Prediction

address_space needs its executable/libraries, a stack and stdout, but no listening socket or secret files.

## Concept

Attack surface is the set of reachable interfaces and resources that can be misused. A resource inventory motivates confinement.

## Defense

Restrict network access, sensitive file access and writable filesystem areas; bound memory and process creation.

## Verification

Inspect our live process's credentials, descriptors and sockets; distinguish all-system ss output from per-process lsof output.

## Reflection

Observing no access during a short run does not prove the program cannot access a resource. A policy needs explicit enforcement and regression checks.

## Experiment

Run `python3 scripts/run_lab.py --missions 15` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q44.** The address-space demo needs executable/library mappings, ordinary memory, timing/sleep syscalls and stdout. It has no application need for network or secret-file access.

**Q45.** Deny network creation, home/secret reads and arbitrary filesystem writes; cap processes and memory. Policy tests must still confirm normal operation.

**Q46.** Least privilege reduces what a compromised component can read, modify or invoke. Mission 17 demonstrates file confinement and Mission 19 applies service confinement.

