# Mission 11: Why Did the Defense Work?

## Question

Which layers protect a modern executable?

## Prediction

The protected binary should show PIE, a canary, non-executable stack and full RELRO. The comparison disables canary and PIE while retaining NX.

## Concept

ASLR randomizes mappings; PIE permits executable relocation. NX removes execute permission from data pages. Canaries check for certain stack overwrites. RELRO protects relocation metadata.

## Defense

Keep compiler hardening enabled and repair unsafe memory operations; mitigations do not establish memory safety.

## Verification

Capture checksec for both builds, randomize_va_space, GNU_STACK flags and __stack_chk_fail symbol.

## Reflection

A canary detects some overwrites on function return, not every memory error. ASLR adds uncertainty rather than eliminating corruption.

## Experiment

Run `python3 scripts/run_lab.py --missions 11` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q31.** ASLR makes mapping locations such as stack, libraries and PIE text less predictable across launches.

**Q32.** NX prevents instruction execution on pages lacking execute permission; it does not prevent data corruption or every code-reuse technique.

**Q33.** A stack canary is a guard checked before returning from protected functions to detect some stack corruption.

**Q34.** Independent controls cover different failure modes, so one bypass need not defeat every protection. Bounds checks remain the primary fix.

