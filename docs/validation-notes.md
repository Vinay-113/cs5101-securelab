# Validation notes

The first mission run verified 20 of 22 scripts. Both initial failures are preserved as attempt-1 logs.

- Mission 12: the student invoking `namei` could not traverse the deliberately restricted directory. The diagnostic now uses `sudo namei`; Alice/Bob's actual access tests still run as those unprivileged identities.
- Mission 22: systemd's default simple-service readiness can return before the child has completed its credential transition. The immediate UID assertion sampled the pre-exec child as root. The corrected worker uses Type=exec, which waits for execution; its runtime UID and NoNewPrivs are then checked. Cleanup also stops any leftover fixed worker. The same explicit readiness is used for Mission 19.
- The corrected/dependent missions (12, 18, 19 and 22) passed on the second attempt. Final status is 22/22 verified; the eight program behavior tests also passed after booting the updated kernel.
- Lima's catch-all forwarding rule needs `guestIPMustBeZero: false` when `guestIP` is 0.0.0.0. The final rule covers guest loopback bindings as well as wildcard bindings. The actual host-manager sockets are recorded in evidence/host-listeners.txt; listener bindings are loopback only. Outbound NAT connections are distinct from listening/published ports.
- AppleDouble metadata files from the initial macOS archive are excluded from source hashing and submission packaging. They are not compiled inputs. The current archive sync disables macOS extended metadata.
- The kernel module package's slow download was resumed using parallel HTTPS ranges from the same official Ubuntu archive, preserving downloaded bytes. Its full SHA-256 was checked against apt's signed package metadata before it was cached in the guest. The interrupted and completed apt logs are both retained under evidence/provisioning.
- The clean stopped-disk recovery copy was restored successfully: a marker created after the copy was absent after restoration, and the VM booted kernel 7.0.0-43-generic.

The instructor-specific Mission 22 remains separate from this project's explicitly labeled practice assessment. The earlier audit listed four deferred utility updates. Final preparation completed available updates, including a Docker runtime update, using a temporary APT phased-update override only in this disposable lab VM. The final package inventory lists no pending upgrades. The update command/output is retained in evidence/provisioning/submission-patch-completion.log.

Stopped-disk recovery copies are stored in `.vm-recovery`, outside Lima's `.vm` instance directory, so Lima does not mistake them for another instance. A FINAL-HARDENED recovery copy is also available locally.

## Final submission checks

Mission 19 attempt 3 captures live root/nobody credentials before and after confinement and corrects the umask test to use ordinary touch-created files. The controlled baseline produces 0644; the project policy produces 0600. mktemp is used only for the private containing directory, so its forced file mode cannot invalidate the comparison.

Mission 20 was retested after hardening. Mission 16 was retested after the Docker update. The eight program behavior tests passed again. The PDF now includes the measured hardening checklist, a handout-page requirements map and completed result-based reflection. Only the PDF report is distributed; alternate Markdown/HTML report exports are removed.
