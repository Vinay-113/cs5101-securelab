# Mission 02: Meet the Kernel

## Question

Where does an application request privileged resource operations?

## Prediction

The file operation will appear as openat/open, write and close system calls; startup adds loader calls.

## Concept

A system call transfers control from user space into the kernel, which validates arguments and mediates resources. The kernel is part of the trusted computing base (TCB).

## Defense

Keep applications unprivileged and rely on validated kernel interfaces.

## Verification

The trace contains the hello.txt open, message write and descriptor close; verify file contents.

## Reflection

A userspace library call is not always a one-to-one syscall. Tracing can change timing.

## Experiment

Run `python3 scripts/run_lab.py --missions 2` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q4.** Consult the captured trace: Linux libc commonly implements open using openat. write sends bytes and close releases the descriptor.

**Q5.** Direct unrestricted hardware access would bypass memory isolation, device arbitration and permission checks, allowing one application to damage other workloads.

**Q6.** The kernel enforces process isolation and access policy; if it lies or is compromised, userspace security assumptions fail.

