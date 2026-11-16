# Mission 22: Practice: Secure the Machine

## Question

Can six scoped weaknesses be investigated, fixed and re-tested?

## Prediction

The generated fixture will expose incorrect file/directory permissions, an unnecessary loopback listener, a root worker and missing integrity baselining. Each fix will have an original-condition retest.

## Concept

A baseline supports classification and evidence. Multiple OS controls address confidentiality, integrity, authorization, attack surface and privilege separation.

## Defense

Use restrictive modes/groups, stop the unwanted listener, run the worker as nobody with no-new-privileges and keep a root-protected integrity reference.

## Verification

Require all six F1-F6 VERIFIED markers, baseline/after inventories and successful authorized access after remediation.

## Reflection

This is a practice assessment of intentionally seeded fixtures. The real instructor challenge, separate rules and image were not supplied, so it cannot be claimed completed.

## Experiment

Run `python3 scripts/run_lab.py --missions 22` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q68-75.** Baseline first; identify six findings; classify each; choose and apply a control; re-test the same condition; preserve logs and checksums; summarize evidence and limitations in the final report.

**Q76.** The most striking result is the AppArmor probe: both teaching files opened under DAC, yet the same program was denied one file after its profile was enforced. Compared with the temporary ACL grant for Bob, this shows that owner-controlled permission and mandatory application policy answer different authorization questions. The allowed-file control still succeeded, demonstrating selective confinement rather than a general application failure.

**Q77.** Protecting the incident record uses both directory traversal restrictions and file modes; integrity additionally needs a separately protected baseline. One control is insufficient.

**Q78.** The address-space maps and the stack-buffer-overflow diagnostic illustrate different boundaries: inter-process isolation versus memory safety inside one process.

**Q79.** Least privilege appears in group-based file access, named ACL grants, process capabilities, container restrictions, service identity and SSH authentication policy.

**Q80.** If the kernel is compromised, it can falsify logs, bypass permissions and read/alter process memory. Guest-level defenses no longer provide their assumed guarantees.

**Q81.** Protected resources include files, process memory, CPU/memory availability, credentials and communication endpoints.

**Q82.** Trusted components include the enforcing guest kernel, policy administrator, toolchain, baseline store and host virtualization stack.

**Q83.** Bob, malformed input, a compromised application and unintended clients represent distinct untrusted subjects in the scoped experiments.

**Q84.** Boundaries include user/kernel mode, per-process address spaces, identity-based file access, mandatory profiles, namespaces and the VM boundary.

**Q85.** The kernel enforces modes/ACLs, memory mappings, capabilities, namespaces and cgroups; AppArmor adds mandatory mediation.

**Q86.** Denial normally returns an error or terminates a violating process. We record exit status and diagnostics and may receive policy audit logs.

**Q87.** Misconfiguration, implementation bugs, excessive privilege or a compromised trusted layer can defeat a mechanism. A passing lab test covers only its stated condition.

**Q88.** Re-run the original negative test, retain positive-function tests, record actual output and exit codes, and verify evidence hashes against a trusted copy.

