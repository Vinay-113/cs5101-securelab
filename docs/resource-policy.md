# Application resource inventory (Mission 15)

Subject: the supplied address_space application, inspected while sleeping.

- Executable and dynamic loader/libraries: read and executable mappings are required. Deny arbitrary executable modification.
- Stack/heap memory: ordinary allocation is required; bound memory to 64 MiB for a small teaching service.
- Output descriptor: stdout is required for PID/address reporting; no access to arbitrary user file descriptors is needed.
- Clock/sleep and exit: required. Network sockets are not required; restrict address families or disable the network namespace interface.
- Secret files and home directories: not required; deny them with MAC or service filesystem restrictions.
- Persistent writes and temporary files: not required by address_space; use a read-only filesystem and isolated temporary directory if needed by a future version.
- Child processes: not required; bound tasks and avoid granting process-control capabilities.

This is a proposed policy based on program behavior and source review. Mission 17 verifies a specific AppArmor file-access policy. Mission 19 verifies a distinct systemd worker identity and sandbox configuration. These tests do not establish that the address_space binary has a complete production sandbox.
