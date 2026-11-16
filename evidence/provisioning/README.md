# Provisioning evidence

setup.log captures tool installation and the official Docker repository installation. kernel-update-interrupted.log records the slow apt download before it was interrupted during the fetch phase. kernel-update-completed.log records a verified cached kernel-module package and successful completion of the upgrade. The package digest matched apt's signed metadata. See docs/validation-notes.md for details.

container-preflight.log records AppArmor activation, cgroups v2 and official image pulls. recovery-test.log records the stopped-disk copy and successful restoration test. final-vm-start.log records the final start with the corrected all-address forwarding ignore rule.

These are administrative setup logs. Mission-specific commands, output, UTC times, statuses and checksums are in evidence/runs/.

submission-patch-completion.log records the final available-package upgrades, including the temporary phased-update override used only for this lab VM. submission-system-profile.log captures the final guest identity, architecture, networking, storage, memory, compiler/trace tools, policy/firewall state and pending-package listing.
