# Mission 06: Two Processes Need to Talk

## Question

How do pipe and shared-memory IPC differ?

## Prediction

Both demos will transmit a fixed parent message. The pipe serializes bytes through the kernel; a process-shared semaphore orders access to a shared mapping.

## Concept

A pipe is a kernel-managed byte stream accessed through inherited descriptors. Shared memory exposes common pages; synchronization establishes publication and visibility.

## Defense

Limit descriptor inheritance, close unused pipe ends, bound messages, and protect shared-memory permissions and synchronization.

## Verification

Check exact pipe text and shared-memory receipt after semaphore publication.

## Reflection

The supplied handout refers to instructor shared-memory code that was absent. shared_ipc.c is a self-contained comparison using an anonymous shared mapping inherited by fork.

## Experiment

Run `python3 scripts/run_lab.py --missions 6` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q16.** A pipe uses read/write operations and kernel buffering; shared memory allows direct loads/stores into shared pages after setup.

**Q17.** Without synchronization, concurrent readers and writers can observe partial or inconsistent state. Semaphore ordering prevents reading before publication.

**Q18.** Protect both endpoints and data: unauthorized endpoint access enables injection or disclosure even when message formatting is correct.

