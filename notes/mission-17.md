# Mission 17: Linux Says No

## Question

Can MAC deny a file that DAC allows?

## Prediction

Both world-readable teaching files will open unconfined. The enforcing AppArmor profile will allow one and deny the other.

## Concept

AppArmor attaches a mandatory policy to a program and mediates operations independently of owner-controlled DAC grants. Effective access must satisfy both layers.

## Defense

Keep the profile enforcing, grant specific required paths and audit the explicit denial.

## Verification

First prove DAC permits both, load the profile, then assert allowed.txt opens and denied.txt does not; collect profile status and available kernel denial logs.

## Reflection

The program return code is the main behavior check. Journal availability and policy logging can vary; a missing denial log does not by itself mean access was allowed.

## Experiment

Run `python3 scripts/run_lab.py --missions 17` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q50.** AppArmor mediates configured operations of a confined task, including filesystem access and optionally other resources; it is not simply a file owner setting.

**Q51.** DAC owners can grant ordinary file access; a mandatory profile can still deny the program even when its UID and file mode would permit the operation.

**Q52.** A compromised application that satisfies ordinary DAC can still be blocked from unrelated resources by MAC. The profile and kernel are trusted dependencies.

