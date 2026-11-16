# Mission 14: What Happened While I Was Away?

## Question

Can logs reconstruct an event sequence?

## Prediction

Eight harmless explicitly labeled synthetic events will appear in timestamp order under a run-specific journal tag.

## Concept

journald associates messages with timestamps and origin metadata. Logging is evidence subject to coverage, clock and retention limits.

## Defense

Keep useful persistent logs, restrict access, synchronize time and consider remote tamper-resistant collection.

## Verification

Synchronize the journal and require all eight tagged events; collect SSH and login context separately.

## Reflection

The eight messages are deliberate lab markers, not automatic proof that their described security actions happened. Actual action evidence is in the corresponding mission logs.

## Experiment

Run `python3 scripts/run_lab.py --missions 14` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q41.** Authentication failures/successes, service changes, policy denials and privileged actions are useful, if the relevant subsystem actually logs them.

**Q42.** Timestamps order events and correlate sources; clock skew, timezone conversion and coarse precision must be considered.

**Q43.** Unlogged actions, lost/rotated records, attacker tampering and misleading application messages limit conclusions. Absence of a log is not proof of absence.

