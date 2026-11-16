# Permission design (Mission 12)

- `/opt/securelab`, root:securelab, 0755: everyone can traverse to the public subtree; only root can add top-level entries.
- `public`, root:securelab, 0755: lab users may list/traverse; only root writes.
- `employees`, root:securelab, 0750: root and securelab group may list/traverse; Bob has no access.
- `secrets`, root:securelab, 0750: same restricted traversal boundary.
- `secrets/incident.txt`, root:securelab, 0640: root reads/writes; securelab group reads; others have no rights.

Alice belongs to securelab and can read the incident. Bob does not and is denied. Alice cannot overwrite the root-owned file. Directory permissions and file permissions are verified independently through path inspection and access tests.
