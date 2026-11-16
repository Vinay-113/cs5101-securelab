# Mission 05: The Race

## Question

Can concurrent increments lose updates?

## Prediction

Several unsynchronized runs may fall below two million; the mutex runs should always reach two million.

## Concept

Increment is a read-modify-write critical section. Concurrent non-atomic accesses constitute a C data race and undefined behavior. -O0 aids observation but does not make the race valid or deterministic.

## Defense

Protect every access to shared state with the same mutex, or use suitable C atomics.

## Verification

Repeat five unsafe runs and three mutex runs; separately run five exact-count regression checks.

## Reflection

A race could bypass a quota, double-spend a balance or invalidate a check/use assumption. A correct count in one unsafe run does not prove safety.

## Experiment

Run `python3 scripts/run_lab.py --missions 5` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q13.** Two threads can read the same old value and both store the same incremented value, losing an update. More broadly, the C program has undefined behavior.

**Q14.** counter++ is the critical section. The protected version acquires lock before it and releases lock afterward.

**Q15.** A check and update can interleave so that an authorization, balance or resource limit is enforced inconsistently.

