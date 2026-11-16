# SECURELAB - Secure Operating Systems (CS5101)

A reproducible implementation of the 22-mission handout: C programs, Bash experiments, evidence capture, explanatory notes, and a six-finding **practice** final assessment.

The instructor's separate Mission 22 rules and challenge VM were not supplied. The included practice challenge is a documented substitute for learning and testing, not a claim to have completed that unavailable assessment. A headless Ubuntu 26.04 ARM64 VM is used on this Apple Silicon Mac; the handout recommends Ubuntu Desktop and VirtualBox, but none of the implemented experiments needs a desktop UI.

## Submission files

Start with the [submission guide](docs/submission-guide.md). The repository contains the complete submission archive and its unpacked source, documentation, reports, and captured evidence.

- [Printable report](output/pdf/securelab-report.pdf)
- [Complete submission ZIP](output/securelab-submission.zip)
- [ZIP SHA-256 checksum](output/securelab-submission.sha256)

Recorded validation: **21 core mission scripts, 1 practice-assessment script and 8 behavior tests passed**. Mission 22 is an explicitly labeled practice challenge because the instructor's separate challenge image and rules were unavailable.

## Requirements and verification

- [Requirement-by-requirement evidence map](docs/requirements-map.json)
- [Explicit before/after hardening checklist](docs/hardening-checklist.json)
- [Completed analysis of the recorded experiments](docs/project-reflection.md)

## Open the results

- `output/pdf/securelab-report.pdf`: printable report generated from actual evidence.
- `evidence/latest.txt`: latest run location; `manifest.json` records each mission's status, exit code and attempts.
- `notes/mission-01.md` through `mission-22.md`: predictions, concepts, defenses, verification and answers to the handout questions.
- `docs/diagrams.md`, `docs/permission-design.md`, `docs/access-models.md`, `docs/resource-policy.md`: diagrams and design rationale.

Consult the generated report for what actually passed. Source files and predictions are not execution evidence.

## Reproduce on this Mac

```bash
bash scripts/install_host.sh
bash scripts/vm.sh start
bash scripts/vm.sh sync
bash scripts/vm.sh setup
bash scripts/vm.sh snapshot SECURELAB-CLEAN
bash scripts/vm.sh test
bash scripts/vm.sh run
bash scripts/vm.sh fetch
python3 scripts/build_report.py
```

`build_report.py` needs ReportLab only for PDF export (`python3 -m pip install reportlab`), and produces the PDF submission report. A bundled Python with ReportLab may be used. Linux's guest setup installs python3-reportlab.

The first run downloads an approximately 900 MB guest image, allocates a **40 GiB sparse disk**, and uses **4 GiB RAM / 2 vCPUs** while running. Lima itself is kept in `.tools`. VM data lives in `.vm`, and stopped-disk recovery copies live in `.vm-recovery`; Lima's downloaded-image cache may live in the user's normal Lima cache. No host directories are mounted into the VM. Extra guest port forwarding is disabled; managed SSH uses a host loopback endpoint. The VM has outbound NAT for package/image downloads. Docker publishes no ports and no host bridge is added.

## Use an existing disposable Ubuntu VM

Copy this source tree into `~/securelab`, then:

```bash
cd ~/securelab
bash scripts/setup_guest.sh
bash scripts/install_docker.sh
# Take a stopped VM snapshot/recovery copy through your hypervisor now.
make test
python3 scripts/run_lab.py
python3 scripts/build_report.py
```

Guest setup creates password-locked `alice` and `bob` test users and group `securelab`; it refuses to repurpose existing accounts with those names. The student needs noninteractive sudo in the disposable guest. Privileged operations require the lab marker created only after a virtualization check. They should not run on a personal Linux workstation.

## Re-run and diagnose

```bash
bash scripts/vm.sh shell
cd ~/securelab
python3 scripts/run_lab.py --missions 7,8,12,17,18
python3 scripts/run_lab.py --missions 19 --resume evidence/runs/RUN_ID
```

Mission 18 requires Missions 12 and 17 to have run. Build diagnostics are in `build.log`; each mission keeps every `attempt-N.log`. A nonzero exit or missing verification sentinel is recorded as a failure. Intentionally denied commands and expected local crash/sanitizer results are asserted rather than silently ignored. The unsynchronized race is nondeterministic; a correct unsafe result is not treated as proof of safety.

The SSH lesson uses a temporary key, a guest-loopback sshd on port 2222 and pinned local host key verification. Its private key is removed, and the listener is stopped afterward. Do not copy private VM management keys into a submission.

## Recovery

```bash
bash scripts/vm.sh stop
bash scripts/vm.sh restore SECURELAB-CLEAN
```

The `snapshot` command creates an **APFS clone of the stopped guest disk**, because Lima's VZ backend does not implement Lima's QEMU snapshot API. It is named SECURELAB-CLEAN to serve the handout's recovery purpose. `restore` preserves the current disk before restoring the recovery copy. Stop the VM before copying/restoring disks; never edit a live guest disk.

For a scoped reversal of Mission 19, run `bash scripts/rollback_hardening.sh` inside the guest. This restores the recorded UFW files/state and removes the teaching worker and lab umask rule. It does not undo package upgrades. A clean disk recovery copy is the comprehensive rollback.

Stop the VM when finished to release RAM: `bash scripts/vm.sh stop`. It can be restarted later; it does not start automatically at login.

## Evidence and submission

Every run contains commands, outputs, UTC timestamps, exit statuses, artifacts and SHA-256 checksums. Verify them inside a run directory with `sha256sum -c SHA256SUMS`. Checksums detect drift against this reference, not independent authorship. Keep a trusted copy elsewhere if stronger integrity assurance is needed.

Build a portable submission with `python3 scripts/package_submission.py`. It includes source, notes, reports and captured evidence; it excludes `.vm`, `.tools`, caches and generated executables. Do not submit the virtual disk or SSH management keys. The submission report is PDF-only. The analytical reflections are grounded in recorded results; the instructor-specific Mission 22 remains separately pending.
