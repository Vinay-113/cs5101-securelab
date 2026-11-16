# Mission 04: Can One Process Read Another?

## Question

Does a pointer identify memory across processes?

## Prediction

The address belongs to one virtual address space. Maps will show executable, libraries, stack and anonymous regions; ASLR may vary addresses between launches.

## Concept

Page tables and MMU permissions translate process virtual addresses to physical memory. The same numeric address may refer to different pages in another process.

## Defense

Use process isolation, least privilege and mediated debugging interfaces.

## Verification

Capture maps while the process is alive and compare two independent launches.

## Reflection

Ordinary pointer dereferencing cannot cross an address-space boundary. ptrace, process_vm_readv and /proc/PID/mem are controlled exceptions, not impossible mechanisms.

## Experiment

Run `python3 scripts/run_lab.py --missions 4` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q10.** An address space contains executable code, data, heap, stack, mapped files/libraries, anonymous mappings and kernel-provided helper mappings where applicable.

**Q11.** A pointer is interpreted through the current process's page tables. Another process cannot use it to directly select the first process's pages.

**Q12.** The MMU enforces per-page mappings and read/write/execute permissions configured by the kernel, producing a fault on disallowed access.

