# Mission 03: Process Detective

## Question

What security metadata does /proc expose?

## Prediction

A sleeping process will expose credentials, one thread, memory counters, descriptor entries and process start information.

## Concept

/proc presents kernel-maintained process state. CapEff, NoNewPrivs, Seccomp and TracerPid add security context beyond the starter script.

## Defense

Investigate unexpected credentials, tracing, capabilities, descriptor access and resource use.

## Verification

Run the inspector on a live process we own; reject invalid PID strings and count actual fd entries.

## Reflection

A process can exit or a PID can be reused during collection. Permission errors are not evidence of zero descriptors.

## Experiment

Run `python3 scripts/run_lab.py --missions 3` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q7.** Status exposes UIDs/GIDs, parent PID, state, threads, memory, capabilities, seccomp and no-new-privileges. Some information is restricted by procfs policy.

**Q8.** Excess CPU, memory, threads or descriptors can exhaust shared resources and threaten availability; cgroups and limits constrain impact.

**Q9.** Unexpected thread counts can reveal concurrency, runaway workers or resource abuse, but a high count alone is not proof of malicious behavior.

