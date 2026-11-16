# SECURELAB - CS5101

## Executive summary

22/22 mission scripts verified in run 20261116T101423Z. This includes a six-finding practice assessment, not the unavailable instructor challenge. All execution claims refer to captured guest output; conceptual explanations and predictions are labeled separately.

## System profile

Host: Apple Silicon macOS. Guest: headless Ubuntu 26.04 LTS ARM64 under Lima/Apple VZ, 2 vCPUs, 4 GiB RAM and 40 GiB sparse disk. No host folders mounted; no container ports published. Guest system and kernel details are captured in Mission 21. The Desktop/VirtualBox recommendation is adapted to this host. The missing instructor shared-memory sample is replaced with our synchronized anonymous mapping. Recorded guest platform: Linux-7.0.0-43-generic-aarch64-with-glibc2.43.

## Threat model and attack surface

Assets: synthetic incident/configuration records, process memory, service credentials and availability. Adversaries: an unprivileged lab user (Bob), malformed input and a compromised unprivileged application. Trusted dependencies: guest kernel, privileged administrator, compiler, baseline store and the host virtualization stack. The practice assessment tests only seeded fixtures inside /opt/securelab/practice and dedicated transient services. Host exploitation, public systems and production security certification are outside its scope.

## Practice assessment findings

Execution status: verified. The conditions, controls and retests below describe the practice design; actual completion requires verified Mission 22 evidence.

### F1: Confidentiality / authorization

Condition: Bob can read the synthetic incident record at mode 0644.

Remediation: root:securelab and 0640; Alice remains an authorized reader.

Retest: Bob read denied; Alice read succeeds.

### F2: Integrity / authorization

Condition: World-writable configuration allows Bob to modify settings.

Remediation: Change mode 0666 to 0640.

Retest: Bob write test changes from allowed to denied.

### F3: Integrity / isolation

Condition: A mode-0777 directory allows Bob to create entries.

Remediation: Use root:securelab and 0750.

Retest: Bob creates a file before; creation is denied afterward.

### F4: Attack surface

Condition: An unnecessary HTTP listener exposes a fixture on guest loopback port 8088.

Remediation: Stop the dedicated practice service.

Retest: HTTP succeeds before; connection fails and socket is absent afterward.

### F5: Privilege separation

Condition: A sleep worker runs as root despite requiring no privileged operations.

Remediation: Run as nobody with NoNewPrivileges and ProtectSystem=strict.

Retest: Observe root UID before and nobody UID plus NoNewPrivs=1 afterward.

### F6: Integrity monitoring

Condition: No protected comparison baseline exists for the practice configuration.

Remediation: Store a root-readable SHA-256 baseline outside the fixture.

Retest: Clean check passes, deliberate drift fails, restored file passes.

These are generated teaching weaknesses, not findings on the macOS host. Evidence: evidence/runs/20261116T101423Z/mission-22/.

## Mission 01: Who Are You?

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:14:24.216562+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-01/attempt-1.log`.

**Question:** How do users and processes carry identity?

**Prediction:** An ordinary program will inherit the invoking user's real and effective IDs. Running as Alice will change those credentials.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
uid=501(vinaypatil) gid=1000(vinaypatil) groups=1000(vinaypatil),999(systemd-journal)
Real UID       : 501
Effective UID  : 501
Real GID       : 1000
Effective GID  : 1000
Real UID       : 1000
Effective UID  : 1000
Real GID       : 1001
Effective GID  : 1001
```

**Concept:** Real IDs identify the originating user; effective IDs normally drive discretionary access checks. The filesystem UID can matter for Linux file checks. Authentication establishes identity; authorization evaluates a requested operation.

**Defense:** Use separate unprivileged accounts and grant only required access.

**Verification:** Compare id with identity.c under the student and Alice accounts.

**Reflection:** A compromised process can exercise its credentials; shared accounts weaken attribution.

**Q1.** UID records the real user identity; EUID is the effective identity used for many access decisions. They can differ with setuid or deliberate credential changes. No setuid program is created here.

**Q2.** Authentication proves an identity (for example, possession of an SSH key). Authorization decides whether that identity may read a file or perform another action.

**Q3.** Unauthorized reading violates confidentiality. Network listeners and parsers handling untrusted files are two workstation attack surfaces.

## Mission 02: Meet the Kernel

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:14:24.232526+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-02/attempt-1.log`.

**Question:** Where does an application request privileged resource operations?

**Prediction:** The file operation will appear as openat/open, write and close system calls; startup adds loader calls.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
close(3)                                = 0
close(3)                                = 0
openat(AT_FDCWD, "hello.txt", O_WRONLY|O_CREAT|O_TRUNC|O_NOFOLLOW, 0644) = 3
write(3, "Hello from user space!\n", 23) = 23
close(3)                                = 0
Hello from user space!
```

**Concept:** A system call transfers control from user space into the kernel, which validates arguments and mediates resources. The kernel is part of the trusted computing base (TCB).

**Defense:** Keep applications unprivileged and rely on validated kernel interfaces.

**Verification:** The trace contains the hello.txt open, message write and descriptor close; verify file contents.

**Reflection:** A userspace library call is not always a one-to-one syscall. Tracing can change timing.

**Q4.** Consult the captured trace: Linux libc commonly implements open using openat. write sends bytes and close releases the descriptor.

**Q5.** Direct unrestricted hardware access would bypass memory isolation, device arbitration and permission checks, allowing one application to damage other workloads.

**Q6.** The kernel enforces process isolation and access policy; if it lies or is compromised, userspace security assumptions fail.

## Mission 03: Process Detective

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:14:24.248538+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-03/attempt-1.log`.

**Question:** What security metadata does /proc expose?

**Prediction:** A sleeping process will expose credentials, one thread, memory counters, descriptor entries and process start information.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
PID: 2089
Command: sleep 30 
Uid:	501	501	501	501
Threads:	1
CapEff:	0000000000000000
NoNewPrivs:	0
Open file descriptors: 3
```

**Concept:** /proc presents kernel-maintained process state. CapEff, NoNewPrivs, Seccomp and TracerPid add security context beyond the starter script.

**Defense:** Investigate unexpected credentials, tracing, capabilities, descriptor access and resource use.

**Verification:** Run the inspector on a live process we own; reject invalid PID strings and count actual fd entries.

**Reflection:** A process can exit or a PID can be reused during collection. Permission errors are not evidence of zero descriptors.

**Q7.** Status exposes UIDs/GIDs, parent PID, state, threads, memory, capabilities, seccomp and no-new-privileges. Some information is restricted by procfs policy.

**Q8.** Excess CPU, memory, threads or descriptors can exhaust shared resources and threaten availability; cgroups and limits constrain impact.

**Q9.** Unexpected thread counts can reveal concurrency, runaway workers or resource abuse, but a high count alone is not proof of malicious behavior.

## Mission 04: Can One Process Read Another?

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:14:24.264511+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-04/attempt-1.log`.

**Question:** Does a pointer identify memory across processes?

**Prediction:** The address belongs to one virtual address space. Maps will show executable, libraries, stack and anonymous regions; ASLR may vary addresses between launches.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
PID = 2103
&secret = 0xfffffcd521b4
c26e99166000-c26e99200000 rw-p 00000000 00:00 0                          [heap]
fffffcd32000-fffffcd53000 rw-p 00000000 00:00 0                          [stack]
PID = 2108
&secret = 0xffffc6fb2d64
```

**Concept:** Page tables and MMU permissions translate process virtual addresses to physical memory. The same numeric address may refer to different pages in another process.

**Defense:** Use process isolation, least privilege and mediated debugging interfaces.

**Verification:** Capture maps while the process is alive and compare two independent launches.

**Reflection:** Ordinary pointer dereferencing cannot cross an address-space boundary. ptrace, process_vm_readv and /proc/PID/mem are controlled exceptions, not impossible mechanisms.

**Q10.** An address space contains executable code, data, heap, stack, mapped files/libraries, anonymous mappings and kernel-provided helper mappings where applicable.

**Q11.** A pointer is interpreted through the current process's page tables. Another process cannot use it to directly select the first process's pages.

**Q12.** The MMU enforces per-page mappings and read/write/execute permissions configured by the kernel, producing a fault on disallowed access.

## Mission 05: The Race

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:14:26.300948+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-05/attempt-1.log`.

**Question:** Can concurrent increments lose updates?

**Prediction:** Several unsynchronized runs may fall below two million; the mutex runs should always reach two million.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
Unsynchronized run 1
Expected: 2000000
Actual  : 1053523
Unsynchronized run 2
Expected: 2000000
Actual  : 1030106
Unsynchronized run 3
Expected: 2000000
Actual  : 1019242
Unsynchronized run 4
Expected: 2000000
Actual  : 992367
Unsynchronized run 5
Expected: 2000000
Actual  : 1010067
Mutex run 1
Expected: 2000000
Actual  : 2000000
Mutex run 2
Expected: 2000000
Actual  : 2000000
Mutex run 3
Expected: 2000000
Actual  : 2000000
```

**Concept:** Increment is a read-modify-write critical section. Concurrent non-atomic accesses constitute a C data race and undefined behavior. -O0 aids observation but does not make the race valid or deterministic.

**Defense:** Protect every access to shared state with the same mutex, or use suitable C atomics.

**Verification:** Repeat five unsafe runs and three mutex runs; separately run five exact-count regression checks.

**Reflection:** A race could bypass a quota, double-spend a balance or invalidate a check/use assumption. A correct count in one unsafe run does not prove safety.

**Q13.** Two threads can read the same old value and both store the same incremented value, losing an update. More broadly, the C program has undefined behavior.

**Q14.** counter++ is the critical section. The protected version acquires lock before it and releases lock afterward.

**Q15.** A check and update can interleave so that an authorization, balance or resource limit is enforced inconsistently.

## Mission 06: Two Processes Need to Talk

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:14:26.518706+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-06/attempt-1.log`.

**Question:** How do pipe and shared-memory IPC differ?

**Prediction:** Both demos will transmit a fixed parent message. The pipe serializes bytes through the kernel; a process-shared semaphore orders access to a shared mapping.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
Child received: Hello from the parent
Shared-memory child received: Hello through a synchronized shared mapping
```

**Concept:** A pipe is a kernel-managed byte stream accessed through inherited descriptors. Shared memory exposes common pages; synchronization establishes publication and visibility.

**Defense:** Limit descriptor inheritance, close unused pipe ends, bound messages, and protect shared-memory permissions and synchronization.

**Verification:** Check exact pipe text and shared-memory receipt after semaphore publication.

**Reflection:** The supplied handout refers to instructor shared-memory code that was absent. shared_ipc.c is a self-contained comparison using an anonymous shared mapping inherited by fork.

**Q16.** A pipe uses read/write operations and kernel buffering; shared memory allows direct loads/stores into shared pages after setup.

**Q17.** Without synchronization, concurrent readers and writers can observe partial or inconsistent state. Semaphore ordering prevents reading before publication.

**Q18.** Protect both endpoints and data: unauthorized endpoint access enables injection or disclosure even when message formatting is correct.

## Mission 07: Alice vs Bob

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:14:26.534621+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-07/attempt-1.log`.

**Question:** How does chmod change a second user's access?

**Prediction:** Bob can read an Alice-owned 0644 file and is denied after it becomes 0600; Alice retains read access.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
-rw-r--r-- 644 alice:alice /opt/securelab/dac/secret.txt
VERIFIED ALLOWED: + common.sh:14: printf '%q ' sudo -u bob cat /opt/securelab/dac/secret.txt
-rw------- 600 alice:alice /opt/securelab/dac/secret.txt
VERIFIED DENIED (exit 1): + common.sh:19: printf '%q ' sudo -u bob cat /opt/securelab/dac/secret.txt
VERIFIED ALLOWED: + common.sh:14: printf '%q ' sudo -u alice cat /opt/securelab/dac/secret.txt
MISSION 07 VERIFIED
```

**Concept:** DAC uses ownership, group membership and mode bits. The owner can change the policy, subject to filesystem and other controls.

**Defense:** Restrict secret files to the smallest needed audience.

**Verification:** Capture stat before/after and assert both denied Bob access and allowed Alice access.

**Reflection:** File modes do not help if an ancestor directory or another copy exposes the same data.

**Q19.** 0644 grants others read access; 0600 removes group and other permissions, leaving the owner read/write.

**Q20.** The file owner normally controls its discretionary mode and ACL, while privileged administrators may override ordinary DAC.

**Q21.** Removing Bob's unnecessary access illustrates least privilege. Owner, group and other are three distinct permission classes; each has r/w/x bits.

## Mission 08: The Permission Maze

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:14:26.599214+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-08/attempt-1.log`.

**Question:** Can one named user receive a narrow exception?

**Prediction:** A named Bob read ACL will permit reading without granting write or making the file world-readable.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
user::rw-
VERIFIED DENIED (exit 1): + common.sh:19: printf '%q ' sudo -u bob cat /opt/securelab/acl/secret.txt
user::rw-
user:bob:r--
mask::r--
VERIFIED ALLOWED: + common.sh:14: printf '%q ' sudo -u bob cat /opt/securelab/acl/secret.txt
VERIFIED DENIED (exit 2): + common.sh:19: printf '%q ' sudo -u bob sh -c 'echo unauthorized >> /opt/securelab/acl/secret.txt'
VERIFIED DENIED (exit 1): + common.sh:19: printf '%q ' sudo -u bob cat /opt/securelab/acl/secret.txt
MISSION 08 VERIFIED
```

**Concept:** POSIX ACLs supplement owner/group/other with named entries. The ACL mask bounds effective permissions of named users and group-class entries.

**Defense:** Grant u:bob:r, verify effective rights, then remove the temporary exception.

**Verification:** Capture getfacl before and after, test read allowed/write denied, remove ACL and prove read denied again.

**Reflection:** ls mode bits alone can obscure ACL intent: the group-class bits reflect the ACL mask, not simply the owning group entry.

**Q22.** The named Bob entry grants read access subject to the mask; the owner remains Alice.

**Q23.** An ACL can identify Bob individually without granting the same permission to every member of the owning group or all other users.

**Q24.** Fine-grained least privilege is exercised. ACLs are still discretionary access controls and do not inherently stop an owner from changing policy.

## Mission 09: Too Much Power

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:14:26.663365+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-09/attempt-1.log`.

**Question:** How can Linux express privileges more narrowly than root?

**Prediction:** An ordinary shell will have few or no effective capabilities. System file capabilities depend on the installed image.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
uid=501(vinaypatil) gid=1000(vinaypatil) groups=1000(vinaypatil),999(systemd-journal)
Current: =
Bounding set =cap_chown,cap_dac_override,cap_dac_read_search,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_linux_immutable,cap_net_bind_service,cap_net_broadcast,cap_net_admin,cap_net_raw,cap_ipc_lock,cap_ipc_owner,cap_sys_module,cap_sys_rawio,cap_sys_chroot,cap_sys_ptrace,cap_sys_pacct,cap_sys_admin,cap_sys_boot,cap_sys_nice,cap_sys_resource,cap_sys_time,cap_sys_tty_config,cap_mknod,cap_lease,cap_audit_write,cap_audit_control,cap_setfcap,cap_mac_override,cap_mac_admin,cap_syslog,cap_wake_alarm,cap_block_suspend,cap_audit_read,cap_perfmon,cap_bpf,cap_checkpoint_restore
uid=501(vinaypatil) euid=501(vinaypatil)
/usr/bin/ping cap_net_raw=ep
/usr/bin/mtr-packet cap_net_raw=ep
```

**Concept:** Linux capabilities divide privileged operations into sets associated with threads and executable files. They are not identical to unforgeable object-capability systems.

**Defense:** Separate privileged setup from unprivileged processing; drop capability sets and avoid unnecessary file capabilities.

**Verification:** Capture id, sudo policy, capsh and existing getcap output without granting new privileges.

**Reflection:** Some capabilities, especially CAP_SYS_ADMIN, remain very broad; a capability grant needs individual analysis.

**Q25.** Root can bypass many discretionary checks and administer critical resources, so compromise has a much larger blast radius.

**Q26.** Linux capabilities split traditional root authority into named privileges such as CAP_NET_BIND_SERVICE. They are per-thread kernel privileges, not general-purpose object handles.

**Q27.** Keep the network/parser component unprivileged and isolate a small audited helper for the one privileged operation it needs.

## Mission 10: The Dangerous Array

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:14:26.695563+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-10/attempt-1.log`.

**Question:** What happens when a fixed input exceeds a stack buffer?

**Prediction:** Short input fits; the protected or ASan build should stop the long copy. The bounded implementation rejects input longer than 15 bytes.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
Copying 6 bytes into a 16-byte buffer...
Copying 34 bytes into a 16-byte buffer...
*** stack smashing detected ***: terminated
Protected overflow exit: 134
Copying 34 bytes into a 16-byte buffer...
==2283==ERROR: AddressSanitizer: stack-buffer-overflow on address 0xe1d116af0030 at pc 0xe5d119144e9c bp 0xfffffeb4aff0 sp 0xfffffeb4a7d0
SUMMARY: AddressSanitizer: stack-buffer-overflow src/memory_overflow_demo.c:9 in main
ASan overflow exit: 1
Accepted: short
```

**Concept:** A 16-byte array needs one byte for the string terminator. Writing 34 bytes crosses its boundary and causes undefined behavior. No exploit payload or foreign process is used.

**Defense:** Reject oversize inputs before copying; retain stack protection and sanitizers during testing.

**Verification:** Capture compilation, short success, protected long-input nonzero exit, ASan stack-buffer-overflow and exact safe boundaries.

**Reflection:** An unprotected build is inspected but not exploited. A crash is one possible symptom; it is not a guaranteed outcome of undefined behavior.

**Q28.** It means accessing bytes outside the array's allocated object; adjacent state can be overwritten and C provides no valid semantics for the operation.

**Q29.** Corruption can damage data, crash a process or alter control flow. This lab only observes local detection and termination.

**Q30.** A pre-copy size check includes the terminator and rejects an input that will not fit, preventing the out-of-bounds operation rather than detecting it afterward.

## Mission 11: Why Did the Defense Work?

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:14:28.027288+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-11/attempt-1.log`.

**Question:** Which layers protect a modern executable?

**Prediction:** The protected binary should show PIE, a canary, non-executable stack and full RELRO. The comparison disables canary and PIE while retaining NX.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH	Symbols		FORTIFY	Fortified	Fortifiable	FILE
Full RELRO      Canary found      NX enabled    PIE enabled     No RPATH   No RUNPATH   102 Symbols	  No	0		2		/opt/securelab/bin/memory_protected
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH	Symbols		FORTIFY	Fortified	Fortifiable	FILE
Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH   104 Symbols	  No	0		2		/opt/securelab/bin/memory_unprotected
2
  GNU_STACK      0x000000 0x0000000000000000 0x0000000000000000 0x000000 0x000000 RW  0x10
  GNU_RELRO      0x00fd48 0x000000000001fd48 0x000000000001fd48 0x0002b8 0x0002b8 R   0x1
     9: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND __stack_chk_fail@GLIBC_2.17 (2)
    85: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND __stack_chk_fail@GLIBC_2.17
```

**Concept:** ASLR randomizes mappings; PIE permits executable relocation. NX removes execute permission from data pages. Canaries check for certain stack overwrites. RELRO protects relocation metadata.

**Defense:** Keep compiler hardening enabled and repair unsafe memory operations; mitigations do not establish memory safety.

**Verification:** Capture checksec for both builds, randomize_va_space, GNU_STACK flags and __stack_chk_fail symbol.

**Reflection:** A canary detects some overwrites on function return, not every memory error. ASLR adds uncertainty rather than eliminating corruption.

**Q31.** ASLR makes mapping locations such as stack, libraries and PIE text less predictable across launches.

**Q32.** NX prevents instruction execution on pages lacking execute permission; it does not prevent data corruption or every code-reuse technique.

**Q33.** A stack canary is a guard checked before returning from protected functions to detect some stack corruption.

**Q34.** Independent controls cover different failure modes, so one bypass need not defeat every protection. Bounds checks remain the primary fix.

## Mission 12: The Secret File

Status: **VERIFIED**. Exit: 0; attempt 2; UTC 2026-11-16T10:17:30.618993+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-12/attempt-2.log`.

**Question:** How do file and directory permissions combine?

**Prediction:** Alice, as a securelab group member, can traverse secrets and read incident.txt. Bob cannot traverse it. Alice cannot overwrite the root-owned record.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
f: /opt/securelab/secrets/incident.txt
-rw-r----- root securelab incident.txt
VERIFIED ALLOWED: + common.sh:14: printf '%q ' sudo -u alice cat /opt/securelab/secrets/incident.txt
sudo -u alice cat /opt/securelab/secrets/incident.txt + common.sh:14: printf '\n'
cat: /opt/securelab/secrets/incident.txt: Permission denied
VERIFIED DENIED (exit 1): + common.sh:19: printf '%q ' sudo -u bob cat /opt/securelab/secrets/incident.txt
sudo -u bob cat /opt/securelab/secrets/incident.txt + common.sh:19: printf '\n'
sh: 1: cannot create /opt/securelab/secrets/incident.txt: Permission denied
VERIFIED DENIED (exit 2): + common.sh:19: printf '%q ' sudo -u alice sh -c 'echo changed >> /opt/securelab/secrets/incident.txt'
```

**Concept:** Directory execute controls traversal; read controls name listing; write plus execute controls entry changes. A file permission alone is insufficient.

**Defense:** Use root:securelab, 0750 restricted directories and 0640 records; keep public data separate.

**Verification:** Capture namei path components; test Alice read allowed, Bob read denied and Alice write denied.

**Reflection:** World-readable content can still be hidden by a non-traversable directory, but relying on that alone is fragile when files are moved or copied.

**Q35.** Each ancestor must allow traversal before a file can be opened; directory write/execute can also permit replacement or deletion even when the file itself is not writable.

**Q36.** Root and explicitly authorized securelab group members such as Alice; Bob has no business need.

**Q37.** If reachable through traversable directories, a world-readable incident file could disclose confidential data. Use restrictive file and directory permissions together.

## Mission 13: Can We Trust the File?

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:14:28.176135+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-13/attempt-1.log`.

**Question:** Can a checksum detect modification?

**Prediction:** The baseline check will pass, then fail after appending text.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
7e8320091ff5b18af4c4b21db8c2bd0bbbadabe170236c86d98c433886d88dfc  config.txt
config.txt: OK
VERIFIED ALLOWED: + common.sh:14: printf '%q ' sha256sum -c config.sha256
bbd7b221e620b35e51bda162276e595fb24263fb3312b327cae37403ac840016  config.txt
config.txt: FAILED
VERIFIED DENIED (exit 1): + common.sh:19: printf '%q ' sha256sum -c config.sha256
MISSION 13 VERIFIED
```

**Concept:** SHA-256 fingerprints bytes. Comparison with a trusted baseline detects drift; an unauthenticated checksum cannot identify the author or resist replacement of both data and baseline.

**Defense:** Protect the baseline separately; use signatures or HMAC when authenticity is needed.

**Verification:** Record both hashes and assert sha256sum -c changes from success to failure.

**Reflection:** Hashing is not secure deletion. Unlink removes a name, and overwriting is unreliable on SSDs, snapshots and copy-on-write storage. Encryption-key management and platform-appropriate sanitization matter.

**Q38.** Changing file bytes produces a different SHA-256 digest with overwhelming probability; consult the captured original and modified digests.

**Q39.** No. Anyone can hash bytes. A hash alone neither proves authorship nor protects an attacker-writable baseline.

**Q40.** Integrity asks whether bytes match a trusted reference; authenticity asks whether their claimed origin is trustworthy.

## Mission 14: What Happened While I Was Away?

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:14:28.192185+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-14/attempt-1.log`.

**Question:** Can logs reconstruct an event sequence?

**Prediction:** Eight harmless explicitly labeled synthetic events will appear in timestamp order under a run-specific journal tag.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
2026-11-16T15:44:28.200604+05:30 lima-securelab securelab-20261116T101423Z[2525]: synthetic lab session started
2026-11-16T15:44:28.201984+05:30 lima-securelab securelab-20261116T101423Z[2527]: identity baseline captured
2026-11-16T15:44:28.202459+05:30 lima-securelab securelab-20261116T101423Z[2528]: synthetic file created
2026-11-16T15:44:28.204532+05:30 lima-securelab securelab-20261116T101423Z[2531]: file permissions restricted to 0600
2026-11-16T15:44:28.205771+05:30 lima-securelab securelab-20261116T101423Z[2533]: SHA256 baseline captured
2026-11-16T15:44:28.206189+05:30 lima-securelab securelab-20261116T101423Z[2534]: controlled content change applied
2026-11-16T15:44:28.207417+05:30 lima-securelab securelab-20261116T101423Z[2536]: hash mismatch detected
2026-11-16T15:44:28.208646+05:30 lima-securelab securelab-20261116T101423Z[2538]: approved bytes restored and verification passed
```

**Concept:** journald associates messages with timestamps and origin metadata. Logging is evidence subject to coverage, clock and retention limits.

**Defense:** Keep useful persistent logs, restrict access, synchronize time and consider remote tamper-resistant collection.

**Verification:** Synchronize the journal and require all eight tagged events; collect SSH and login context separately.

**Reflection:** The eight messages are deliberate lab markers, not automatic proof that their described security actions happened. Actual action evidence is in the corresponding mission logs.

**Q41.** Authentication failures/successes, service changes, policy denials and privileged actions are useful, if the relevant subsystem actually logs them.

**Q42.** Timestamps order events and correlate sources; clock skew, timezone conversion and coarse precision must be considered.

**Q43.** Unlogged actions, lost/rotated records, attacker tampering and misleading application messages limit conclusions. Absence of a log is not proof of absence.

## Mission 15: The Suspicious Application

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:14:28.258183+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-15/attempt-1.log`.

**Question:** Which resources does a harmless program need?

**Prediction:** address_space needs its executable/libraries, a stack and stdout, but no listening socket or secret files.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
   2562    2553   501   501    1  0.0  0.0 /opt/securelab/bin/address_space
Name:	address_space
Uid:	501	501	501	501
Threads:	1
CapEff:	0000000000000000
```

**Concept:** Attack surface is the set of reachable interfaces and resources that can be misused. A resource inventory motivates confinement.

**Defense:** Restrict network access, sensitive file access and writable filesystem areas; bound memory and process creation.

**Verification:** Inspect our live process's credentials, descriptors and sockets; distinguish all-system ss output from per-process lsof output.

**Reflection:** Observing no access during a short run does not prove the program cannot access a resource. A policy needs explicit enforcement and regression checks.

**Q44.** The address-space demo needs executable/library mappings, ordinary memory, timing/sleep syscalls and stdout. It has no application need for network or secret-file access.

**Q45.** Deny network creation, home/secret reads and arbitrary filesystem writes; cap processes and memory. Policy tests must still confirm normal operation.

**Q46.** Least privilege reduces what a compromised component can read, modify or invoke. Mission 17 demonstrates file confinement and Mission 19 applies service confinement.

## Mission 16: Build Your First Container Sandbox

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:14:28.290343+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-16/attempt-1.log`.

**Question:** Which boundaries does a container actually provide?

**Prediction:** The container shares the guest kernel but has a distinct PID namespace; cgroup files will expose configured memory, CPU and PID limits.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
Hello from Docker!
To try something more ambitious, you can run an Ubuntu container with:
Linux 1a8400882803 7.0.0-43-generic #43-Ubuntu SMP PREEMPT_DYNAMIC Fri Oct 23 13:33:03 UTC 2026 aarch64 GNU/Linux
PRETTY_NAME="Ubuntu 26.04.1 LTS"
NAME="Ubuntu"
Guest PID namespace:
pid:[4026531836]
Container PID namespace:
pid:[4026532389]
Cgroup controls:
67108864
32
50000 100000
CapEff:	0000000000000000
NoNewPrivs:	1
touch: cannot touch '/should-not-write': Read-only file system
```

**Concept:** Namespaces isolate resource views; cgroups constrain accounting and consumption. Containers are processes under the same kernel, not separate guest kernels.

**Defense:** Use no network, read-only root filesystem, no added capabilities, no-new-privileges and resource limits. No ports are published.

**Verification:** Capture hello-world and Ubuntu output, namespace inode, cgroup limits and rejected root-filesystem write.

**Reflection:** Docker daemon access is highly privileged. It is installed only in the disposable guest and used through sudo, without granting docker-group membership.

**Q47.** A PID namespace gives the container a process-ID view in which its first process can be PID 1. Host/guest parent namespaces may still see those processes.

**Q48.** A VM has virtual hardware and its own guest kernel. A container shares its host kernel; here that host is the Ubuntu VM.

**Q49.** Cgroups can control memory, CPU bandwidth, process counts and device/I/O access depending on controllers and configuration. Namespaces alone do not impose resource quotas.

## Mission 17: Linux Says No

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:15:12.091453+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-17/attempt-1.log`.

**Question:** Can MAC deny a file that DAC allows?

**Prediction:** Both world-readable teaching files will open unconfined. The enforcing AppArmor profile will allow one and deny the other.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
/opt/securelab/apparmor/allowed.txt: ALLOWED
/opt/securelab/apparmor/denied.txt: ALLOWED
/opt/securelab/apparmor/allowed.txt: ALLOWED
/opt/securelab/apparmor/denied.txt: DENIED
   securelab-probe
```

**Concept:** AppArmor attaches a mandatory policy to a program and mediates operations independently of owner-controlled DAC grants. Effective access must satisfy both layers.

**Defense:** Keep the profile enforcing, grant specific required paths and audit the explicit denial.

**Verification:** First prove DAC permits both, load the profile, then assert allowed.txt opens and denied.txt does not; collect profile status and available kernel denial logs.

**Reflection:** The program return code is the main behavior check. Journal availability and policy logging can vary; a missing denial log does not by itself mean access was allowed.

**Q50.** AppArmor mediates configured operations of a confined task, including filesystem access and optionally other resources; it is not simply a file owner setting.

**Q51.** DAC owners can grant ordinary file access; a mandatory profile can still deny the program even when its UID and file mode would permit the operation.

**Q52.** A compromised application that satisfies ordinary DAC can still be blocked from unrelated resources by MAC. The profile and kernel are trusted dependencies.

## Mission 18: Compare Access-Control Models

Status: **VERIFIED**. Exit: 0; attempt 2; UTC 2026-11-16T10:17:30.685823+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-18/attempt-2.log`.

**Question:** Who decides access under each model?

**Prediction:** The comparison will connect observed DAC, ACL, capability and MAC behavior; RBAC remains a conceptual scenario.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
VERIFIED ALLOWED: + common.sh:14: printf '%q ' sudo -u alice cat /opt/securelab/secrets/incident.txt
VERIFIED DENIED (exit 1): + common.sh:19: printf '%q ' sudo -u bob cat /opt/securelab/secrets/incident.txt
/opt/securelab/apparmor/allowed.txt: ALLOWED
/opt/securelab/apparmor/denied.txt: DENIED
Current: =
MISSION 18 VERIFIED
```

**Concept:** Different models answer different questions: identity and ownership, mandatory policy, role membership, named ACL rights or privileged kernel operations.

**Defense:** Combine models deliberately and verify effective access instead of assuming one mechanism subsumes all others.

**Verification:** Re-test Alice/Bob and the enforcing AppArmor profile; consult the comparison in docs/access-models.md.

**Reflection:** RBAC is explained rather than falsely presented as a deployed role system.

**Q53.** In DAC, the resource owner normally chooses discretionary grants, within administrator and mandatory-policy constraints.

**Q54.** An administrator or security policy authority defines MAC rules; ordinary file owners cannot bypass them merely by chmod.

**Q55.** Assign a database-administrator role the required database-management permissions, then grant/revoke role membership instead of duplicating per-user rights.

**Q56.** A Linux capability grants a narrower class of privileged kernel operations than unrestricted root; this is distinct from an object-capability design.

**Q57.** ACLs add named users/groups and a mask to the ordinary Unix mode design, permitting targeted exceptions. They increase review complexity and remain discretionary.

## Mission 19: Harden the Machine

Status: **VERIFIED**. Exit: 0; attempt 2; UTC 2026-11-16T10:17:30.702107+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-19/attempt-2.log`.

**Question:** Can three justified changes be verified and reversed?

**Prediction:** The audit will record services, ports, updates and firewall state. Incoming default-deny, service confinement and restrictive umask will be testable afterward.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
Default: deny (incoming), allow (outgoing), deny (routed)
Default: deny (incoming), allow (outgoing), deny (routed)
Uid:	65534	65534	65534	65534
NoNewPrivs:	1
0077
600 /tmp/tmp.EA9QBhTEMF
Default: deny (incoming), allow (outgoing), deny (routed)
User=nobody
Verified: incoming firewall policy, confined unprivileged service, restrictive umask.
```

**Concept:** Hardening reduces unnecessary privilege and exposure while keeping a recovery path. apt update refreshes metadata; apt upgrade actually installs available updates.

**Defense:** Permit management SSH before enabling UFW; run the teaching worker as nobody with no-new-privileges; set a 077 umask for future interactive lab files.

**Verification:** Capture before/after, verify firewall default, process UID/NoNewPrivs and mode 0600 on a newly created file. Record package update output.

**Reflection:** UFW is not a complete Docker port policy: published Docker ports can bypass it. This project publishes no container ports. Kernel updates may require reboot and are reported separately.

**Q58.** Keep only documented services needed by the lab: guest management, journald, policy enforcement and temporary mission services. Service necessity depends on the VM inventory.

**Q59.** Management SSH remains limited by the VM's host-loopback forwarding. The local SSH exercise binds only guest loopback. No container ports are published.

**Q60.** Patches remove known vulnerabilities in the trusted computing base and applications. Updating metadata without installing packages is not remediation.

**Q61.** A change can cause lockout or break a dependency; a snapshot, recorded previous configuration and a scoped rollback make recovery practical.

## Mission 20: Secure Remote Access

Status: **VERIFIED**. Exit: 0; attempt 1; UTC 2026-11-16T10:15:14.627534+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-20/attempt-1.log`.

**Question:** What does a key-authenticated localhost SSH session prove?

**Prediction:** A temporary key will authenticate to a guest-loopback-only sshd. The session will retain the student's non-root authorization.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
LISTEN 0      128        127.0.0.1:2222      0.0.0.0:*   
LOCAL_SSH_SUCCESS
uid=501(vinaypatil) gid=1000(vinaypatil) groups=1000(vinaypatil),999(systemd-journal)
Nov 16 15:45:15 lima-securelab sshd[3846]: Accepted publickey for vinaypatil from 127.0.0.1 port 33496 ssh2: ED25519 SHA256:fQY8KKiUfj2QFwmR6TGQ2IfyDErVlOeZvY+d2Js+cCg
Nov 16 15:45:15 lima-securelab sshd-session[3846]: pam_unix(sshd:session): session opened for user vinaypatil(uid=501) by vinaypatil(uid=0)
listenaddress 127.0.0.1:2222
permitrootlogin no
passwordauthentication no
```

**Concept:** SSH authenticates the server host key and the client user's key possession. After login, Unix credentials and policy still determine access.

**Defense:** Use pinned local host keys, key-only authentication, no root login and a loopback listener. Delete the temporary private key after use.

**Verification:** Require LOCAL_SSH_SUCCESS, non-root id output, loopback bind and sshd effective settings; capture authentication journal.

**Reflection:** The isolated listener uses port 2222 so the managed Lima transport remains available. A localhost test does not prove a public network deployment is secure.

**Q62.** The client verifies server host identity and the server verifies the user's credential (here an Ed25519 key). Encryption protects transport once negotiation succeeds.

**Q63.** The user's UID/GID, groups, DAC/ACLs, MAC and sudo policy determine allowed actions after authentication.

**Q64.** Use journalctl for the specific sshd unit; the accepted key and session events support login evidence. Other Ubuntu setups may also route logs to auth.log.

## Mission 21: Who Protects the VM?

Status: **VERIFIED**. Exit: 0; attempt 3; UTC 2026-11-16T10:23:55.387774+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-21/attempt-3.log`.

**Question:** Where do the VM trust boundaries end?

**Prediction:** The guest will identify ARM64 Ubuntu and virtualized hardware. The host remains macOS on Apple Silicon.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
Linux lima-securelab 7.0.0-43-generic #43-Ubuntu SMP PREEMPT_DYNAMIC Fri Oct 23 13:33:03 UTC 2026 aarch64 GNU/Linux
aarch64
PRETTY_NAME="Ubuntu 26.04.1 LTS"
apple
Architecture:                            aarch64
Apple Virtualization Generic Platform
```

**Concept:** A guest kernel enforces guest process boundaries, while virtual devices and Apple's virtualization/hypervisor stack implement the VM boundary. Lima manages lifecycle and SSH transport.

**Defense:** Minimize shared interfaces; keep host mounts disabled, no bridged adapter, no published container ports and no unnecessary devices.

**Verification:** Capture guest version/architecture and virtualization detection; document the actual stack rather than a generic x86 diagram.

**Reflection:** A guest compromise does not imply a host escape, but hypervisor/device bugs, shared folders and management channels add dependencies. No measured/secure boot or hardware TEE claim is made.

**Q65.** Guest applications, privileged services and the guest kernel are inside the guest boundary; the hypervisor and host lie outside it but are part of its security dependencies.

**Q66.** The virtualization layer presents virtual hardware. In this setup Lima orchestrates a VM backed by Apple Virtualization.framework and the host hypervisor mechanisms.

**Q67.** The VM trusts virtual devices, hypervisor, host kernel and management software in addition to its guest TCB. Host compromise can undermine the guest.

## Mission 22: Practice: Secure the Machine

Status: **VERIFIED**. Exit: 0; attempt 2; UTC 2026-11-16T10:17:34.169774+00:00. Evidence: `evidence/runs/20261116T101423Z/mission-22/attempt-2.log`.

**Question:** Can six scoped weaknesses be investigated, fixed and re-tested?

**Prediction:** The generated fixture will expose incorrect file/directory permissions, an unnecessary loopback listener, a root worker and missing integrity baselining. Each fix will have an original-condition retest.

**Experiment:** The exact commands are in `missions/run.sh` (and linked helper scripts), recorded with shell tracing in the evidence log.

**Observation (captured excerpt):**

```text
F1 VERIFIED: unauthorized read denied; authorized read retained
F2 VERIFIED: unauthorized configuration write denied
F3 VERIFIED: unauthorized directory creation denied
F4 VERIFIED: unnecessary listener absent
F5 VERIFIED: worker runs unprivileged with no new privileges
F6 VERIFIED: protected integrity baseline detects drift and passes after restoration
```

**Concept:** A baseline supports classification and evidence. Multiple OS controls address confidentiality, integrity, authorization, attack surface and privilege separation.

**Defense:** Use restrictive modes/groups, stop the unwanted listener, run the worker as nobody with no-new-privileges and keep a root-protected integrity reference.

**Verification:** Require all six F1-F6 VERIFIED markers, baseline/after inventories and successful authorized access after remediation.

**Reflection:** This is a practice assessment of intentionally seeded fixtures. The real instructor challenge, separate rules and image were not supplied, so it cannot be claimed completed.

**Q68-75.** Baseline first; identify six findings; classify each; choose and apply a control; re-test the same condition; preserve logs and checksums; summarize evidence and limitations in the final report.

**Q76.** Reflection prompt: compare the observed ACL exception with the AppArmor denial even when DAC allowed access. Replace this draft with your own learning experience.

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

## Design comparisons and inventories

### Mission 6: IPC comparison

Property: Data access; Pipe / message passing: Kernel-buffered byte stream through read/write; Shared memory: Common mapped pages through loads/stores

Property: Synchronization; Pipe / message passing: Blocking reads/writes provide stream coordination; framing is still required; Shared memory: Explicit ordering needed; demo uses a process-shared semaphore

Property: Endpoint control; Pipe / message passing: Inherited file descriptors; close unused ends; Shared memory: Anonymous shared mapping inherited only by forked child

Property: Security limitation; Pipe / message passing: Leaked descriptors or unbounded messages can expose data or resources; Shared memory: Unauthorized mapping or unsynchronized access can disclose/corrupt state

### Mission 12: permission design

Path under /opt/securelab: .; Owner / mode: root:securelab / 0755; Intended access: All may traverse; root writes

Path under /opt/securelab: public; Owner / mode: root:securelab / 0755; Intended access: All may list/traverse; root writes

Path under /opt/securelab: employees; Owner / mode: root:securelab / 0750; Intended access: Root and analyst group may traverse

Path under /opt/securelab: secrets; Owner / mode: root:securelab / 0750; Intended access: Root and analyst group may traverse

Path under /opt/securelab: secrets/incident.txt; Owner / mode: root:securelab / 0640; Intended access: Alice reads; Bob denied; root writes

### Mission 15: application resource inventory

Resource: Executable / libraries; Need: Read / execute; Proposed restriction: Prevent modification; allow required mappings

Resource: Stack / ordinary memory; Need: Yes; Proposed restriction: Bound memory and process count

Resource: stdout; Need: PID/address report; Proposed restriction: Retain only required descriptors

Resource: Network; Need: No; Proposed restriction: Deny network creation or disable networking

Resource: Home / secrets; Need: No; Proposed restriction: Deny via MAC and filesystem sandbox

Resource: Persistent writes; Need: No; Proposed restriction: Read-only filesystem; isolated temporary area

### Mission 16: VM versus container

Property: Kernel; VM used here: Separate Ubuntu guest kernel; Container used here: Shares Ubuntu guest kernel

Property: Boundary; VM used here: Virtual hardware and host virtualization stack; Container used here: Namespaces, cgroups and kernel security policy

Property: Resource limits; VM used here: Configured vCPU, RAM and virtual disk; Container used here: CPU bandwidth, memory and PID limits

Property: Trust dependency; VM used here: Guest and host kernels plus virtual devices/hypervisor; Container used here: Same guest kernel as sibling containers

Property: Filesystem; VM used here: Guest virtual disk; no host mounts; Container used here: Read-only root for constrained test; no host binds

### Mission 18: access-control models

Mechanism: DAC; Decision basis: Owner, identity, group and mode; Scenario / example: Alice's 0600 secret denies Bob; Limitation: Owner can broaden grants

Mechanism: POSIX ACL; Decision basis: Named entries plus ACL mask; Scenario / example: Read-only auditor exception for Bob; Limitation: Mask/inheritance complicate review; still DAC

Mechanism: MAC / AppArmor; Decision basis: Administrator-defined program policy; Scenario / example: Deny probe's world-readable secret; Limitation: Unconfined paths or incomplete profile leave gaps

Mechanism: RBAC; Decision basis: Role-to-permission assignments; Scenario / example: Database administrator role (conceptual); Limitation: Broad roles and role explosion; not deployed here

Mechanism: Linux capabilities; Decision basis: Per-thread privileged operation sets; Scenario / example: Inspect capsh; narrow privileged helper design; Limitation: Some sets remain broad; not object capabilities

## Limitations and outstanding instructor requirement

The instructor Mission 22 image and separate rules remain unavailable. The final assessment here is practice only. RBAC is a conceptual comparison, not a deployed role engine. Journal markers in Mission 14 are synthetic events, explicitly labeled; they are not automatic records of earlier missions. The unsafe race has undefined behavior and varies between runs. Short successful tests do not prove complete confinement or absence of vulnerabilities. Host secure boot, storage encryption, a hardware TEE and independent forensic authenticity were not measured. Personalize the reflective answers before submission. Recorded pending packages after hardening: distro-info, python3-distro-info, python3-software-properties, software-properties-common. See the original apt output for deferred/phased updates.

## Future improvements

Use the instructor challenge when supplied; compare its rules before applying changes. Export the evidence checksum to a separate trusted location; add remote/persistent audit retention and clock monitoring. Test sandbox controls against a broader required-function matrix and review patch state after a reboot. Consider encrypted storage and verified boot as separate extensions. Keep Docker access restricted and review its firewall interaction before ever publishing a port.

## References

- Project specification: Secure OS (CS5101) - Project Handout.pdf, version 1.0, supplied by the user; 35 pages
- Ubuntu Desktop: https://ubuntu.com/download/desktop
- Lima installation: https://lima-vm.io/docs/installation/
- Lima snapshot limitations: https://lima-vm.io/docs/config/snapshots/
- Docker official Ubuntu installation: https://docs.docker.com/engine/install/ubuntu/
- Ubuntu AppArmor: https://ubuntu.com/server/docs/how-to/security/apparmor/
- Linux process status: https://man7.org/linux/man-pages/man5/proc_pid_status.5.html
- Linux memory mappings: https://man7.org/linux/man-pages/man2/mmap.2.html
- Linux capabilities: https://man7.org/linux/man-pages/man7/capabilities.7.html
- systemd execution controls: https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html
- OpenSSH manuals: https://www.openssh.com/manual.html
