# Mission 10: The Dangerous Array

## Question

What happens when a fixed input exceeds a stack buffer?

## Prediction

Short input fits; the protected or ASan build should stop the long copy. The bounded implementation rejects input longer than 15 bytes.

## Concept

A 16-byte array needs one byte for the string terminator. Writing 34 bytes crosses its boundary and causes undefined behavior. No exploit payload or foreign process is used.

## Defense

Reject oversize inputs before copying; retain stack protection and sanitizers during testing.

## Verification

Capture compilation, short success, protected long-input nonzero exit, ASan stack-buffer-overflow and exact safe boundaries.

## Reflection

An unprotected build is inspected but not exploited. A crash is one possible symptom; it is not a guaranteed outcome of undefined behavior.

## Experiment

Run `python3 scripts/run_lab.py --missions 10` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q28.** It means accessing bytes outside the array's allocated object; adjacent state can be overwritten and C provides no valid semantics for the operation.

**Q29.** Corruption can damage data, crash a process or alter control flow. This lab only observes local detection and termination.

**Q30.** A pre-copy size check includes the terminator and rejects an input that will not fit, preventing the out-of-bounds operation rather than detecting it afterward.

