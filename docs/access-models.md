# Access-control comparison (Mission 18)

## DAC

Decision basis: process identity, file ownership, group and mode bits, subject to other controls. The owner normally manages grants.

Observed example: Bob reads an Alice-owned 0644 record, then is denied at 0600.

Scenario: a developer owns a private working file and shares it with a Unix project group.

Limitation: a compromised owner can broaden discretionary access; root can often bypass it.

## POSIX ACL

Decision basis: named user/group entries and the ACL mask, supplementing DAC.

Observed example: `u:bob:r` grants one named reader; write remains denied. Removing the grant revokes the access.

Scenario: a single auditor needs read access without joining the full engineering group.

Limitation: masks, inherited defaults and many exceptions complicate review. An ACL is a form of DAC, not a mandatory policy layer.

## MAC (AppArmor)

Decision basis: administrator-defined mandatory policy associated with the confined task.

Observed example: a probe is denied one world-readable file while allowed another; ordinary DAC permits both.

Scenario: a document converter can read only its input area and system libraries even if its user owns unrelated secrets.

Limitation: incomplete profiles or an unconfined execution path leave gaps; the profile/kernel must be trusted. SELinux uses labels and policy rules rather than AppArmor's chiefly path-oriented model.

## RBAC

Decision basis: permissions assigned to roles and users assigned to those roles.

Conceptual example: database-administrator role grants backup/restore and schema-management operations. No dedicated RBAC engine is deployed by this project.

Scenario: an organization grants and revokes job-function access by role membership.

Limitation: role explosion and overly broad roles; Unix groups alone do not implement all RBAC features such as constraints and separation of duties.

## Linux capabilities

Decision basis: named privileged kernel operations in per-thread capability sets, and file capabilities contributing at exec under defined rules.

Observed example: inspect capsh and existing getcap output without modifying system binaries.

Scenario: an otherwise unprivileged service needs only CAP_NET_BIND_SERVICE to bind a privileged port (when the system's privileged-port threshold requires it).

Limitation: some capabilities are very broad; they do not replace ordinary file access control or eliminate the need to validate privileged requests. Linux capabilities differ from object-capability security models.
