# Practice challenge rules and scenario

This challenge was created for this project because the instructor's separate Mission 22 document and prepared image were unavailable. It does not replace any instructor-specific grading requirements.

You administer a guest VM storing synthetic incident and configuration records. Alice is an authorized analyst. Bob is an ordinary account without incident/configuration access. An unrelated worker should not need administrative authority, and an HTTP listener is not required after the exercise.

Scope: `/opt/securelab/practice`, `/var/lib/securelab/integrity`, and the dedicated `securelab-practice-*` systemd units. The practice HTTP server binds **127.0.0.1:8088** inside the guest. It is never published to the host or a public network. No personal or production data is used.

The challenge script first creates six known teaching conditions and captures a baseline. It then demonstrates each original condition, applies one appropriate control, and re-tests. Changes are restricted to the fixture and dedicated teaching processes; traps stop the services and lock down fixture permissions if an intermediate step fails.

Expected findings and classifications:

1. Confidentiality/authorization: Bob can read a record at 0644; fix to root:securelab 0640 and retain Alice access.
2. Integrity/authorization: configuration at 0666 is writable by Bob; fix to 0640.
3. Integrity/isolation: a 0777 directory allows Bob to add entries; fix to 0750.
4. Attack surface: unnecessary guest-loopback HTTP port 8088; stop the service and prove both failed connection and absent socket.
5. Privilege separation: a worker runs as root without a need; replace it with nobody, NoNewPrivileges and a protected filesystem view, then inspect credentials.
6. Integrity monitoring: no protected comparison reference; create a root-only baseline, show a controlled mismatch and restore the approved bytes.

Passing criterion: all six `F1` through `F6 VERIFIED` markers, a completed after inventory and the outer `MISSION 22 VERIFIED` marker. Capture outputs and command exit statuses. A generated weakness is not an independently discovered vulnerability.

The practice script's automatic corrections are an executable worked solution. To conduct an independent exercise, review the baseline before reading the correction section and make your own notes. Never run it on an unrelated host.
