# Mission 16: Build Your First Container Sandbox

## Question

Which boundaries does a container actually provide?

## Prediction

The container shares the guest kernel but has a distinct PID namespace; cgroup files will expose configured memory, CPU and PID limits.

## Concept

Namespaces isolate resource views; cgroups constrain accounting and consumption. Containers are processes under the same kernel, not separate guest kernels.

## Defense

Use no network, read-only root filesystem, no added capabilities, no-new-privileges and resource limits. No ports are published.

## Verification

Capture hello-world and Ubuntu output, namespace inode, cgroup limits and rejected root-filesystem write.

## Reflection

Docker daemon access is highly privileged. It is installed only in the disposable guest and used through sudo, without granting docker-group membership.

## Experiment

Run `python3 scripts/run_lab.py --missions 16` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q47.** A PID namespace gives the container a process-ID view in which its first process can be PID 1. Host/guest parent namespaces may still see those processes.

**Q48.** A VM has virtual hardware and its own guest kernel. A container shares its host kernel; here that host is the Ubuntu VM.

**Q49.** Cgroups can control memory, CPU bandwidth, process counts and device/I/O access depending on controllers and configuration. Namespaces alone do not impose resource quotas.

