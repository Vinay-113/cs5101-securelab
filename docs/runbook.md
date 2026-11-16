# Demonstration and recovery runbook

## Ten-minute presentation

1. Open the PDF report and show its core-lab result, requirements map, scope, and separate instructor-challenge dependency.
2. Show Mission 1 identity output and explain real/effective IDs versus authentication/authorization.
3. Show Mission 2's actual openat/write/close trace and the system-call trust boundary.
4. Compare Mission 4's address maps and Mission 5's repeated unsafe/protected counts. Explain that undefined behavior is not guaranteed to produce a specific value.
5. Show Bob's denied read, a temporary ACL grant and its revocation. Contrast those discretionary controls with Mission 17's mandatory denial on a DAC-readable file.
6. Show the controlled ASan overflow diagnostic and safe-copy boundary check. Explain NX, PIE/ASLR and canaries as distinct layers.
7. Show the constrained container's cgroup limits, namespace identity and read-only failure. Explain its shared-kernel dependency.
8. Show the hardening before/after inventory, local key-authenticated SSH, and the actual VM trust stack.
9. Show the practice challenge's F1-F6 verification markers and distinguish generated fixtures from the unavailable instructor assessment.
10. Show evidence hashes and the clean stopped-disk recovery copy. Explain the evidence-based reflection and future improvements.

## If a mission fails

Read that mission's last attempt log first. Preserve the failed attempt. Correct the cause, sync the source, and re-run only the affected mission plus dependent checks using `--resume`. Do not overwrite the old log or edit an observed result to make it pass. Regenerate reports and checksums from the new manifest.

## If guest access is lost

The managed Lima SSH listener is host-local. Check `bash scripts/vm.sh status` and the `.vm/securelab/serial*.log` files. If a lab change broke the guest, stop the VM and restore the SECURELAB-CLEAN stopped-disk copy. The restore command preserves the current disk as `disk.before-restore-*` so recovery can be reversed.

## Before submitting

Read the source and be prepared to explain the observed results and analytical reflections. Confirm your instructor accepts the headless ARM64 setup and the format of your evidence. Complete the instructor-specific Mission 22 when its rules/image are supplied. Keep a trusted evidence archive separately and verify its checksum.
