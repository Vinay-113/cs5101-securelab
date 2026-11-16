# Mission 19: Harden the Machine

## Question

Can three justified changes be verified and reversed?

## Prediction

The audit will record services, ports, updates and firewall state. Incoming default-deny, service confinement and restrictive umask will be testable afterward.

## Concept

Hardening reduces unnecessary privilege and exposure while keeping a recovery path. apt update refreshes metadata; apt upgrade actually installs available updates.

## Defense

Permit management SSH before enabling UFW; run the teaching worker as nobody with no-new-privileges; set a 077 umask for future interactive lab files.

## Verification

Capture before/after, verify firewall default, process UID/NoNewPrivs and mode 0600 on a newly created file. Record package update output.

## Reflection

UFW is not a complete Docker port policy: published Docker ports can bypass it. This project publishes no container ports. Kernel updates may require reboot and are reported separately.

## Experiment

Run `python3 scripts/run_lab.py --missions 19` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q58.** Keep only documented services needed by the lab: guest management, journald, policy enforcement and temporary mission services. Service necessity depends on the VM inventory.

**Q59.** Management SSH remains limited by the VM's host-loopback forwarding. The local SSH exercise binds only guest loopback. No container ports are published.

**Q60.** Patches remove known vulnerabilities in the trusted computing base and applications. Updating metadata without installing packages is not remediation.

**Q61.** A change can cause lockout or break a dependency; a snapshot, recorded previous configuration and a scoped rollback make recovery practical.

