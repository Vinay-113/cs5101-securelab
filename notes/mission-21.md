# Mission 21: Who Protects the VM?

## Question

Where do the VM trust boundaries end?

## Prediction

The guest will identify ARM64 Ubuntu and virtualized hardware. The host remains macOS on Apple Silicon.

## Concept

A guest kernel enforces guest process boundaries, while virtual devices and Apple's virtualization/hypervisor stack implement the VM boundary. Lima manages lifecycle and SSH transport.

## Defense

Minimize shared interfaces; keep host mounts disabled, no bridged adapter, no published container ports and no unnecessary devices.

## Verification

Capture guest version/architecture and virtualization detection; document the actual stack rather than a generic x86 diagram.

## Reflection

A guest compromise does not imply a host escape, but hypervisor/device bugs, shared folders and management channels add dependencies. No measured/secure boot or hardware TEE claim is made.

## Experiment

Run `python3 scripts/run_lab.py --missions 21` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q65.** Guest applications, privileged services and the guest kernel are inside the guest boundary; the hypervisor and host lie outside it but are part of its security dependencies.

**Q66.** The virtualization layer presents virtual hardware. In this setup Lima orchestrates a VM backed by Apple Virtualization.framework and the host hypervisor mechanisms.

**Q67.** The VM trusts virtual devices, hypervisor, host kernel and management software in addition to its guest TCB. Host compromise can undermine the guest.

